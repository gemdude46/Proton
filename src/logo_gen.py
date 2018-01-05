import pygame

logo128 = None

def gen_logo(size):
	''' Generate a size by size Proto logo '''
	
	if size < 128:		  # If this is the case, the generated image looks shit, so we scale
		return pygame.transform.scale(logo128, (size, size))
	
	sf = pygame.Surface((size, size))
	
	sf.fill((0,0,0))
	sf.set_colorkey((0,0,0))
	
	pygame.draw.circle(sf, (0,0,100), (size//2, size//2), size//2)
	
	pygame.draw.rect(sf, (255,0,0), ((2*size//11, 5*size//11), (size//11, size//11)))
	pygame.draw.polygon(sf, (255,0,0), ((3*size//22, 5*size//11), (5*size//22, 4*size//11), (7*size//22, 5*size//11)))
	
	pygame.draw.rect(sf, (0,255,0), ((5*size//11, 5*size//11), (size//11, size//11)))
	pygame.draw.polygon(sf, (0,255,0), ((9*size//22, 6*size//11), (size//2, 7*size//11), (13*size//22, 6*size//11)))
	
	pygame.draw.rect(sf, (0,0,255), ((8*size//11, 5*size//11), (size//11, size//11)))
	pygame.draw.polygon(sf, (0,0,255), ((15*size//22, 5*size//11), (17*size//22, 4*size//11), (19*size//22, 5*size//11)))
	
	return sf

logo128 = gen_logo(128)
