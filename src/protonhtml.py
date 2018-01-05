import string

import domrenderer
import css
import fs

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

mastercss = css.parse(fs.read('rs/master.css'))

def parse(html):
	''' Parses html into an Element '''
	
	html += ' ' * 8 # So range checker on look-ahead isn't required
	
	cel = Element(None, '$document') # Current ELement
	
	i = 0
	
	while i < len(html) - 8:
		
		if cel.tag == 'plaintext':
			cel.write(html[i:])
			i = len(html)

		elif html[i] not in '<&>' + string.whitespace: # or cel.tag in ('style', 'script'):
			s = ''
			while html[i] not in '<&>' + string.whitespace: # or (cel.tag in ('style', 'script') and html[i:i+2] != '</'):
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
			if cel.tag == 'script' and html[i+1] != '/':
				cel.write('<')
				i += 1
				continue

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
				
				a = {}

				while html[i] != '>':
					
					if html[i] not in string.whitespace and not closing:
						ct = ''
						while html[i] not in '=<&>' + string.whitespace:
							ct += html[i]
							i += 1

						if html[i] == '=':
							i += 1

							if html[i] in '"\'':
								q = html[i]
								v = ''
								i += 1
								while html[i] != q:
									v += html[i]
									i += 1
								i += 1
								a[ct] = v

							else:
								v = ''
								while html[i] not in '<&>' + string.whitespace:
									v += html[i]
									i += 1
								a[ct] = v
						else:
							a[ct] = ''

						continue
					i += 1
				
				i += 1
				
				if closing:
					while cel.is_or_has_ancestor_of_tag(t):
						cel.parent.write(cel)
						cel = cel.parent
				else:
					if t in auto_closing_tags:
						cel.write(Element(cel, t, a))
					else:
						cel = Element(cel, t, a)
		
		else:
			cel.write(html[i])
			i += 1
	
	while cel.tag != '$document':
		cel.parent.write(cel)
		cel = cel.parent
	
	return cel


class Element(object):
	
	def __init__(self, parent, tag, attrs=None):
		
		self.parent = parent
		self.tag = tag.lower()
		self.attrs = attrs or dict()
		self.content = []
		self.sfsize = (0,0)
		self.css_cache = None

		if self.tag == 'style':
			self.sheet_cache_hash = None
	
	def get_root(self):
		return self.parent.get_root() if self.parent else self

	def write(self, content):
		
		if isinstance(content, str) and self.content and isinstance(self.content[-1], str):
			self.content[-1] += content
		else:
			self.content.append(content)
	
	def set_attr(self, k, v):
		self.attrs[k] = str(v)
	
	def get_attr(self, k, d=None):
		return self.attrs.get(k, d)
	
	def get_element_children(self):
		return [el for el in self.content if isinstance(el, Element)]

	def is_or_has_ancestor_of_tag(self, tag):
		''' Returns true iff self is a tag or any of self's ancestors are tag '''
		
		tag = tag.lower()
		
		return self.tag == tag or (self.parent.is_or_has_ancestor_of_tag(tag) if self.parent else False)
	
	def get_elements_by_tag_name(self, tag):
		
		els = [self] if self.tag == tag else []

		for el in self.get_element_children():
			els.extend(el.get_elements_by_tag_name(tag))

		return els

	def get_width(self):
		
		if self.tag == '$document':
			return int(self.get_attr('available_width', 640))
		
		else:
			hm = 0
			if self.css().get('width', 'auto') == 'auto':
				hm = self.get_margins()
				hm = hm[1] + hm[3]
			return css.length(self.css().get('width', 'auto'), self.parent.get_width(), self.parent.get_width() - hm)
	
	def get_height(self):
		
		if self.tag == '$document':
			return int(self.get_attr('available_height', 440))
		
		else:
			return self.sfsize[1]
	
	def get_size(self):
		
		return (self.get_width(), self.get_height())
	
	def get_margins(self):
		
		if self.tag == '$document':
			return 0, 0, 0, 0

		pw = self.parent.get_width()
		mw = 0 if self.css().get('width', 'auto') == 'auto' else self.get_width()

		return (
			css.length(self.css().get('margin-top', '0'), pw, 0),
			css.length(self.css().get('margin-right', '0'), pw, (pw - mw) // 2),
			css.length(self.css().get('margin-bottom', '0'), pw, 0),
			css.length(self.css().get('margin-left', '0'), pw, (pw - mw) // 2)
		)
	
	def get_sheet(self):
		
		if self.tag != 'style':
			raise TypeError('Cannot get CSS rules of non <style> element.')

		if self.sheet_cache_hash != hash(self.content[0]):
			self.sheet_cache = css.parse(self.content[0])
			self.sheet_cache_hash = hash(self.content[0])

		return self.sheet_cache

	def css(self):
		
		if self.css_cache is None:
			mycss = mastercss.rules(self)
			for el in self.get_root().get_elements_by_tag_name('style'):
				mycss.update(el.get_sheet().rules(self))
			
			EXP = []

			for prop, val in list(mycss.items()):
				if val == 'inherit':
					mycss[prop] = self.parent.css().get(prop) if self.parent else None
					if mycss[prop] is None:
						del mycss[prop]

				elif val.startswith('EXPAND '):
					EXP.append(prop)

			for prop in EXP:
				val = mycss[prop]
				_, expfrom, pos = val.split(' ', 2)
				expof = mycss[expfrom]
				expof = expof.split()
				nc = len(expof)
				nc = str(nc) + ':'
				ind = [int(i[len(nc):]) for i in pos.split() if i.startswith(nc)][0]
				mycss[prop] = expof[ind]


			self.css_cache = mycss
		
		return self.css_cache
	
	def block(self):
		
		display = self.css().get('display','')
		return 'block' in display or display == 'list-item'
	
	def to_html(self):
		return ('<%s>'%self.tag) + ''.join([c if isinstance(c, str) else c.to_html() for c in self.content]) + ('</%s>'%self.tag)
	
	def render(self):
		return domrenderer.render_element(self)
	
	def __repr__(self):
		return '<Element %s %r>' % (self.tag, self.attrs)
