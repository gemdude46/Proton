import pygame
from pygame.locals import *

import css as protoncss

pygame.font.init()

df_fonts = {}

for weight in range(5):
	for italic in (True, False):
		df_fonts[(weight, italic)] = pygame.font.Font(
			'rs/OpenSans-%s%s.ttf' % (
				('Light', '', 'Semibold', 'Bold', 'ExtraBold')[weight],
				'Italic' if italic else ''
			),
			14
		)

def render_element(self, gibchunks=False, pcss={}):
	
	if isinstance(self, str):
		
		if self.strip() == '':
			return None

		if self == ' BR ':
			self = ' '

		col = protoncss.color(pcss.get('color', '#000'))
		
		weight = pcss.get('font-weight', 'normal')

		italic = pcss.get('font-style') in ('oblique', 'italic')

		if weight not in ('lighter', 'normal', 'bold', 'bolder'): weight = 'normal'
		
		font = df_fonts[(('lighter', 'normal', 'bold', 'bolder').index(weight), italic)]

		return font.render(self, True, col)
	
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

		if chunk == ' BR ':
			lines.append([])
		
		chimg = None
		
		if isinstance(chunk, str) or chunk.block():
			chimg = render_element(chunk, pcss=css[-1])
		else:
			ccss = chunk.css()
			if ccss.get('display') != 'none':
				if ccss.get('display') == 'br':
					if not lines[-1]:
						lines[-1].append(render_element(' BR ', pcss=css[-1]))
					lines.append([])
				else:
					chunks.insert(chi, ' POPCSS ')
					subchunks = render_element(chunk, gibchunks=True)
					for schnk in subchunks[::-1]:
						chunks.insert(chi, schnk)
					css.append(ccss)
				continue
		
		if chimg is not None:
			plw = sum([i.get_width() for i in lines[-1]])
			if plw + chimg.get_width() > self.get_width():
				lines.append([chimg])
			else:
				lines[-1].append(chimg)
		
	ew = eh = 0
	for line in lines:
		if not line:
			continue
			
		eh += max([o.get_height() for o in line])
		ew = max(ew, sum([o.get_width() for o in line]))
	
	self.sfsize = (max(ew, self.get_width()), max(eh, self.get_height()))

	im = pygame.Surface(self.sfsize, flags=SRCALPHA)
	im.fill(protoncss.color(self.css().get('background-color', 'transparent')))
	
	csr = [0, 0]
	
	for line_i, line in enumerate(lines):
		if not line:
			continue
		
		tlw = sum([o.get_width() for o in line])

		chspace = 0

		ta = self.css().get('text-align', 'left')

		if ta == 'right':
			csr[0] = self.get_width() - tlw

		elif ta == 'center':
			csr[0] = (self.get_width() - tlw) // 2

		elif ta == 'justify' and len(line) > 1 and line_i != len(lines) - 1:
			chspace = (self.get_width() - tlw) / (len(line) - 1)

		lh = max([o.get_height() for o in line])
		for o in line:
			im.blit(o, (int(csr[0]), lh-o.get_height()+csr[1]))
			csr[0] += o.get_width() + chspace
		csr = [0, lh+csr[1]]
	
	margin = self.get_margins()

	if margin != (0,0,0,0):
		nsf = pygame.Surface((self.sfsize[0] + margin[1] + margin[3], self.sfsize[1] + margin[0] + margin[2]), flags=SRCALPHA)
		nsf.fill((0,0,0,0))
		nsf.blit(im, (margin[0], margin[3]))
		im = nsf

	return im
