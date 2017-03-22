import string

import domrenderer
import css

auto_closing_tags = (
    'area',
    'base',
    'br',
    'col',
    'command',
    'embed',
    'hr',
    'img',
    'input',
    'keygen',
    'link',
    'meta',
    'nextid',
    'param',
    'source',
    'track',
    'wbr'
)

f = open('master.css', 'r')
mastercss = css.parse(f.read())
f.close()

def parse(html):
    ''' Parses html into an Element '''
    
    html += ' ' * 8 # So range checker on look-ahead isn't required
    
    cel = Element(None, '$document') # Current ELement
    
    i = 0
    
    while i < len(html) - 8:
        
        if html[i] not in '<&>' + string.whitespace:
            s = ''
            while html[i] not in '<&>' + string.whitespace:
                s += html[i]
                i += 1
            
            cel.write(s)
        
        elif html[i] in string.whitespace:
            if not cel.content or not isinstance(cel.content[-1], str) or cel.content[-1][-1] not in string.whitespace:
                cel.write(' ')
                
            i += 1
        
        elif html[i] == '&':
            while html[i] != ';':
                i += 1
            
            cel.write('[?]')
            i += 1
        
        elif html[i] == '<':
            if html[i+1] == '!':
                if html[i+2] == html[i+3] == '-':
                    while html[i-1] + html[i-2] + html[i-3] != '>--':
                        i += 1
                else:
                    while html[i] != '>':
                        i += 1
                    
                    i += 1
                
            else:
                closing = False
                if html[i+1] == '/':
                    closing = True
                
                i += 1 + closing
                
                while html[i] in string.whitespace:
                    i += 1
                
                t = ''
                while html[i] not in '<&>' + string.whitespace:
                    t += html[i]
                    i += 1
                
                while html[i] != '>':
                    i += 1
                
                i += 1
                
                if closing:
                    while cel.is_or_has_ancestor_of_tag(t):
                        cel.parent.write(cel)
                        cel = cel.parent
                else:
                    if t in auto_closing_tags:
                        cel.write(Element(cel, t))
                    else:
                        cel = Element(cel, t)
        
        else:
            cel.write(html[i])
            i += 1
    
    while cel.tag != '$document':
        cel.parent.write(cel)
        cel = cel.parent
    
    return cel


class Element(object):
    
    def __init__(self, parent, tag, attrs={}):
        
        self.parent = parent
        self.tag = tag.lower()
        self.attrs = attrs
        self.content = []
        self.sfsize = (0,0)
        self.css_cache = None
        
    def write(self, content):
        
        if isinstance(content, str) and self.content and isinstance(self.content[-1], str):
            self.content[-1] += content
        else:
            self.content.append(content)
    
    def set_attr(self, k, v):
        self.attrs[k] = v
    
    def get_attr(self, k):
        return self.attrs.get(k)
    
    def is_or_has_ancestor_of_tag(self, tag):
        ''' Returns true iff self is a tag or any of self's ancestors are tag '''
        
        tag = tag.lower()
        
        return self.tag == tag or (self.parent.is_or_has_ancestor_of_tag(tag) if self.parent else False)
    
    def get_width(self):
        
        if self.tag == '$document':
            return 640
        
        else:
            return self.parent.get_width()
    
    def get_height(self):
        
        if self.tag == '$document':
            return 440
        
        else:
            return self.sfsize[1]
    
    def get_size(self):
        
        return (self.get_width(), self.get_height())
    
    def css(self):
        
        if self.css_cache is None:
            mycss = mastercss.rules(self)
            
            for prop, val in list(mycss.items()):
                if val == 'inherit':
                    mycss[prop] = self.parent.css().get(prop) if self.parent else None
                    if mycss[prop] is None:
                        del mycss[prop]
            
            self.css_cache = mycss
        
        return self.css_cache
    
    def block(self):
        
        return 'block' in self.css().get('display')
    
    def to_html(self):
        return ('<%s>' % self.tag) + ''.join([c if isinstance(c, str) else c.to_html() for c in self.content]) + ('</%s>' % self.tag)
    
    def render(self):
        return domrenderer.render_element(self)
    
    def __repr__(self):
        return '<Element %s>' % self.tag
