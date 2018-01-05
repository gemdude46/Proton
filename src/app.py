#!/usr/bin/env python3
import argparse
import os
import time

import pygame

os.chdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.path.pardir))

import logo_gen
import tab

class BrowserApp(object):
	
	def __init__(self, window, starturi='about:newtab', uifont=None):
		
		ntab = tab.Tab(starturi)
		ntab.set_avail_space((1136, 600))
		self.tabs = [ntab]
		self.activetab = 0
		
		self.window = window

		self.uifont = uifont or pygame.font.Font(None, 13)
		
		window.fill((0,0,0))
		window.blit(logo_gen.gen_logo(256), (window.get_width() // 2 - 128, window.get_height() // 2 - 128))
		pygame.display.update()		
		
	def run(self):
		
		while self.tabs:
			
			active_tab = self.tabs[self.activetab]

			self.window.fill((200, 200, 200))

			active_tab.tick()

			self.window.blit(active_tab.sf, (0,40))

			if active_tab.status:
				status_sf = self.uifont.render(active_tab.status, True, (0,0,0), (240,240,240))
				self.window.blit(status_sf, (0, self.window.get_height() - status_sf.get_height()))
			
			pygame.display.update()
			
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					self.quit()
	
	def quit(self):
		
		for tab in self.tabs:
			tab.close()
		
		self.tabs = []

if __name__ == '__main__':

	parser = argparse.ArgumentParser(description='A web browser powered by python and Pygame. Made of boredom.')
	
	parser.add_argument(
		'uri',
		type=str,
		help='The URI to open.',
		default='about:newtab',
		nargs='?'
	)

	args = parser.parse_args()


	pygame.init()
	screen = pygame.display.set_mode((1136, 640))
	app = BrowserApp(screen, starturi=args.uri, uifont=pygame.font.Font(None, 13))
	app.run()
	pygame.quit()
