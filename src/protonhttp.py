import os

import requests

import fs

class HTTPResponse(object):
	
	def __init__(self, obj):
		
		if isinstance(obj, tuple):
			self.uri, self.body, self.mimetype = obj

		elif isinstance(obj, requests.Response):
			self.body = obj.text
			self.mimetype = obj.headers.get('content-type', '').split(';')[0]
			self.uri = obj.url

		else:
			raise TypeError(
				'HTTPResponse() argument must be a requests.Response or a 3-tuple of strings, not %r'
				% type(obj).__name__
			)
		

def get(uri):
	
	prot, dompath= uri.split(':', 1)

	if prot == 'about':
		return HTTPResponse((uri, fs.read('about/' + dompath), 'text/html'))
	
	if prot == 'file':
		path = os.path.join('/', dompath.lstrip('/'))
		
		if os.path.exists(path):
			
			if os.path.isdir(path):
				doc = '''
					<html><head><title>{path}</title></head><body>
					<h1>Index of {path}</h1>
					<hr>
					<ul>{ls}</ul>
					</body></html>
				'''.format(
					path=path,
					ls=''.join([
						'<li><a href="%s">%s</a></li>' % (os.path.join(path, i), i) for i in os.listdir(path)
					])
				)
				return HTTPResponse((uri, doc, 'text/html'))

	return HTTPResponse(requests.get(uri, headers={'user-agent': 'proton/0.0.1'}, timeout=30))
