#!/usr/bin/env python3
import time

import pygame

import logo_gen
import tab

class BrowserApp(object):
    
    def __init__(self, window):
        
        ntab = tab.Tab('http://navcomic.com')
        ntab.set_avail_space((640, 440))
        self.tabs = [ntab]
        self.activetab = 0
        
        self.window = window
        
        window.fill((0,0,0))
        window.blit(logo_gen.gen_logo(256), (window.get_width() // 2 - 128, window.get_height() // 2 - 128))
        pygame.display.update()        
        
    def run(self):
        
        while self.tabs:
            
            self.window.fill((200, 200, 200))
            
            self.tabs[self.activetab].tick()
            
            self.window.blit(self.tabs[self.activetab].sf, (0,40))
            
            pygame.display.update()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
    
    def quit(self):
        
        for tab in self.tabs:
            tab.close()
        
        self.tabs = []

if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    app = BrowserApp(screen)
    app.run()
    pygame.quit()
