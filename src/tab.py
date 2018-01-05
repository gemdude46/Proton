from multiprocessing import Process, Pipe
import time

import pygame

import protonhttp as http
import protonhtml as html

import cProfile

def load_doc(uri, updstatus=lambda s:0):

	updstatus('downloading')

	rsp = http.get(uri)
	
	if rsp.mimetype != 'text/html':
		raise TypeError('THATS NO HTML!')
	
	updstatus('parsing')

	doc = html.parse(rsp.body)
	
	doc.set_attr('src', rsp.uri)
	
	return doc

def tabproc(pipe):
	''' The main tab function '''
	
	size = (0, 0)
	uri = ''
	dirty = False
	doc = None

	def update_status(status):
		pipe.send({'c': 'updatestatus', 'status': status})
	
	update_status('initiating')

	while True:
		
		if pipe.poll():
			cmdo = pipe.recv()
			
			if not isinstance(cmdo, dict) or 'c' not in cmdo:
				raise TypeError('You call _this_ a command??!!	%r' % cmd)
			
			cmd = cmdo['c']
			
			if cmd == 'shutdown':
				return
			
			if cmd == 'resize':
				size = cmdo['size']
				dirty = True
			
			if cmd == 'goto':
				doc = load_doc(cmdo['uri'], updstatus=update_status)
				uri = doc.get_attr('src')
				dirty = True
		
		if dirty and size != (0, 0):
			update_status('rendering')
			doc.set_attr('available_width', size[0])
			doc.set_attr('available_height', size[1])
			#cProfile.runctx('img = doc.render()', globals(), locals(), 'profile.prof')
			img = doc.render()
			bfr = pygame.image.tostring(img, 'RGBA')
			pipe.send({'c': 'updateimg', 'size': img.get_size(), 'buffer': bfr})
			dirty = False

		else:
			update_status('')
		
		time.sleep(0.1)

class Tab(object):
	
	def __init__(self, uri):
		
		self.uri = uri
		
		self.pipe, threadpipe = Pipe()
		
		self.proc = Process(target=tabproc, args=(threadpipe,))
		
		self.proc.start()
		
		self.pipe.send({'c': 'goto', 'uri': uri})
		
		self.sf = pygame.Surface((1,1))

		self.status = ''
	
	def set_avail_space(self, space):
		
		self.pipe.send({'c': 'resize', 'size': space})
	
	def tick(self):
		
		while self.pipe.poll():
			cmdo = self.pipe.recv()
			
			if not isinstance(cmdo, dict) or 'c' not in cmdo:
				raise TypeError('You call _this_ a command??!!	%r' % cmd)
			
			cmd = cmdo['c']
			
			if cmd == 'updatestatus':
				self.status = cmdo['status']

			elif cmd == 'updateimg':
				self.sf = pygame.image.frombuffer(cmdo['buffer'], cmdo['size'], 'RGBA')
	
	def close(self):
		
		self.pipe.send({'c': 'shutdown'})
		self.proc.join()
