from multiprocessing import Process, Pipe
import time

import pygame

import protonhttp as http
import protonhtml as html

def load_doc(uri):

    rsp = http.get(uri)
    
    if rsp.mimetype != 'text/html':
        raise TypeError('THATS NO HTML!')
    
    doc = html.parse(rsp.body)
    
    doc.set_attr('src', rsp.uri)
    
    return doc

def tabproc(pipe):
    ''' The main tab function '''
    
    size = (0, 0)
    uri = ''
    dirty = False
    doc = None
    
    while True:
        
        if pipe.poll():
            cmdo = pipe.recv()
            
            if not isinstance(cmdo, dict) or 'c' not in cmdo:
                raise TypeError('You call _this_ a command??!!    %r' % cmd)
            
            cmd = cmdo['c']
            
            if cmd == 'shutdown':
                return
            
            if cmd == 'resize':
                size = cmdo['size']
                dirty = True
            
            if cmd == 'goto':
                doc = load_doc(cmdo['uri'])
                uri = doc.get_attr('src')
                dirty = True
        
        if dirty:
            start = time.time()
            img = doc.render()
            stop = time.time()
            print(stop-start)
            bfr = img.tobytes()
            pipe.send({'c': 'updateimg', 'width': img.size[0], 'height': img.size[1], 'buffer': bfr})
            dirty = False
        
        time.sleep(0.1)

class Tab(object):
    
    def __init__(self, uri):
        
        self.uri = uri
        
        self.pipe, threadpipe = Pipe()
        
        self.proc = Process(target=tabproc, args=(threadpipe,))
        
        self.proc.start()
        
        self.pipe.send({'c': 'goto', 'uri': uri})
        
        self.sf = pygame.Surface((1,1))
    
    def set_avail_space(self, space):
        
        self.pipe.send({'c': 'resize', 'size': space})
    
    def tick(self):
        
        while self.pipe.poll():
            cmdo = self.pipe.recv()
            
            if not isinstance(cmdo, dict) or 'c' not in cmdo:
                raise TypeError('You call _this_ a command??!!    %r' % cmd)
            
            cmd = cmdo['c']
            
            if cmd == 'updateimg':
                self.sf = pygame.image.frombuffer(cmdo['buffer'], (cmdo['width'], cmdo['height']), 'RGB')
    
    def close(self):
        
        self.pipe.send({'c': 'shutdown'})
        self.proc.join()
