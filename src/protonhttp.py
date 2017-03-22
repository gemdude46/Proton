import requests

class HTTPResponse(object):
    
    def __init__(self, resp):
        
        self.body = resp.text
        self.mimetype = resp.headers.get('content-type', '').split(';')[0]
        self.uri = resp.url
        

def get(uri):
    
    return HTTPResponse(requests.get(uri, headers={'user-agent': 'proton/0.0.1'}, timeout=30))
