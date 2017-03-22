from PIL import Image, ImageDraw, ImageFont

import css as protoncss

df_fonts = {}

for weight in range(5):
    for italic in (True, False):
        df_fonts[(weight, italic)] = ImageFont.truetype(
            '../rs/OpenSans-%s%s.ttf' % (
                ('Light', '', 'Semibold', 'Bold', 'ExtraBold')[weight],
                'Italic' if italic else ''
            ),
            size = 14
        )

def render_element(self, gibchunks=False, pcss={}):
    
    if isinstance(self, str):
        
        col = protoncss.color(pcss.get('color', '#000'))
        
        weight = pcss.get('font-weight', 'normal')
        
        font = df_fonts[(('lighter', 'normal', 'bold', 'bolder').index(weight), False)]
        
        im = Image.new('RGB', (font.getsize(self)[0], 20), (255,255,255))
        draw = ImageDraw.Draw(im)
        
        draw.text((0,0), self, font=font, fill=col)
        return im
    
    if self.css().get('display') == 'none':
        return None
    
    chunks = []
    
    for c in self.content:
        if isinstance(c, str):
            chunks.extend([x+' ' for x in c.split(' ')])
        else:
            chunks.append(c)
    
    if gibchunks: return chunks
    
    css = [self.css()]
    
    lines = [[]]
    
    chi = 0
    while chi < len(chunks):
        chunk = chunks[chi]
        chi += 1
        
        if chunk == ' POPCSS ':
            css.pop()
            continue
        
        chimg = None
        
        if isinstance(chunk, str) or chunk.block():
            chimg = render_element(chunk, pcss=css[-1])
        else:
            ccss = chunk.css()
            if ccss.get('display') != 'none':
                chunks.insert(chi, ' POPCSS ')
                subchunks = render_element(chunk, gibchunks=True)
                for schnk in subchunks[::-1]:
                    chunks.insert(chi, schnk)
                css.append(ccss)
                continue
        
        if chimg is not None:
            plw = sum([i.size[0] for i in lines[-1]])
            if plw + chimg.size[0] > 640:
                lines.append([chimg])
            else:
                lines[-1].append(chimg)
        
    ew = eh = 0
    for line in lines:
        if not line:
            continue
            
        eh += max([o.size[1] for o in line])
        ew = max(ew, sum([o.size[0] for o in line]))
    
    self.sfsize = (ew, eh)
    
    im = Image.new('RGB', self.get_size(), (255,255,255))
    
    csr = [0,0]
    
    for line in lines:
        if not line:
            continue
            
        lh = max([o.size[1] for o in line])
        for o in line:
            im.paste(o, (csr[0], lh-o.size[1]+csr[1]))
            csr[0] += o.size[0]
        csr = [0, lh+csr[1]]
            
    return im
