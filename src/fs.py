
def read(fn, binary=False):
	f = open(fn, 'rb' if binary else 'r')
	c = f.read()
	f.close()

	return c
