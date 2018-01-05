import string

idchars = 'qwertyuiopasdfghjklxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM-_$1234567890'

class CSSLexer(object):
	
	def __init__(self, css):
		self.css = css
		self.i = 0
	
	@property
	def c(self):
		return self.css[self.i]

	def next(self):
		
		if self.c in string.whitespace:
			while self.c in string.whitespace:
				self.i += 1

			return ' '

		if self.c in idchars:
			s = ''
			while self.c in idchars:
				s += self.c
				self.i += 1
			return s

		if self.c in '"\'':
			q = self.c
			s = ''
			self.i += 1
			while self.c != q:

				if self.c == '\\':
					self.i += 1
					if self.c == '\\':
						s += '\\'
					elif self.c in '"\'':
						s += self.c
					elif self.c == '\n':
						pass
					elif self.c in '1234567890ABCDEF':
						p = ''
						while self.c in '1234567890ABCDEF' and len(p) < 6:
							p += self.c
							self.i += 1
						s += chr(int(p, 16))
					else:
						s += '\\' + self.c
				else:
					s += self.c
				self.i += 1
			self.i += 1
			return s

		c = self.c
		self.i += 1
		return c

class CSSASTNode(object):
	
	def __call__(self, el):
		return self.e(el)

class CSSASTAncestor(CSSASTNode):
	
	def __init__(self, a, s):
		self.a = a
		self.s = s
	
	def e(self, el):
		
		if not self.s.e(el):
			return False

		while True:
			el = el.parent
			if el is None:
				return False

			if self.a.e(el):
				return True

class CSSASTAnd(CSSASTNode):
	
	def __init__(self, l, r):
		self.l = l
		self.r = r
	
	def e(self, el):
		return self.l.e(el) and self.r.e(el)

class CSSASTBool(CSSASTNode):
	
	def __init__(self, val):
		self.val = val
	
	def e(self, el):
		return self.val

class CSSASTOr(CSSASTNode):
	
	def __init__(self, l, r):
		self.l = l
		self.r = r
	
	def e(self, el):
		return self.l.e(el) or self.r.e(el)

class CSSASTClass(CSSASTNode):
	
	def __init__(self, c):
		self.c = c
	
	def e(self, el):
		return self.c in el.get_attr('class', '').split()

class CSSASTId(CSSASTNode):
	
	def __init__(self, i):
		self.i = i
	
	def e(self, el):
		return self.i == el.get_attr('id', '')

class CSSASTParent(CSSASTNode):
	
	def __init__(self, p, s):
		self.p = p
		self.s = s
	
	def e(self, el):
		
		if not el.parent:
			return False

		return self.p.e(el.parent) and self.s.e(el)

class CSSASTTag(CSSASTNode):
	
	def __init__(self, t):
		self.t = t
	
	def e(self, el):
		return self.t == el.tag

class CSSParser(object):
	
	def __init__(self, lexer):
		self.lexer = lexer
		self.lbfr = None
	
	def n(self):
		if self.lbfr is None:
			self.lbfr = self.lexer.next()

		#print(self.lbfr)
		return self.lbfr
	
	def a(self, tk):
		return tk == self.n()
	
	def c(self):
		tk = self.n()
		self.lbfr = None
		return tk
	
	def ac(self, tk):
		if self.a(tk):
			return self.c()

		else:
			return False

	def populate_ruleset(self, rs):
		
		try:
			while True:
				self.ac(' ')
				rs.ruleset.extend(self.parse_media_query())

		except IndexError:
			return
	
	def parse_media_query(self):
		
		if self.ac('@'):
			
			if self.ac('media'):
				mquery = self.parse_media_query_condition()
				self.ac(' ')
				if not self.ac('{'):
					return []

				self.ac(' ')

				b = []
				while not self.ac('}'):
					b.append(self.parse_ruleset())
					self.ac(' ')

				return [(CSSASTAnd(mquery, cond), does) for cond, does in b]

			else:
				return []

		else:
			return [self.parse_ruleset()]
	
	def parse_media_query_condition(self):
		return CSSASTBool(False)
	
	def parse_ruleset(self):
		r = self.parse_rule()
		b = self.parse_block()

		return (r, b)

	def parse_rule(self):
		r = self.parse_rule_ancestor()

		self.ac(' ')

		if self.ac(','):
			self.ac(' ')
			r = CSSASTOr(r, self.parse_rule())

		return r
	
	def parse_rule_ancestor(self):
		r = self.parse_rule_parent()

		while self.ac(' '):
			if not (self.a(',') or self.a('{')):
				r = CSSASTAncestor(r, self.parse_rule_parent())
		
		return r
	
	def parse_rule_parent(self):
		r = self.parse_rule_chain()

		self.ac(' ')

		while self.ac('>'):
			self.ac(' ')
			r = CSSASTParent(r, self.parse_rule_chain())

		return r

	def parse_rule_chain(self):
		
		r = None

		if self.ac('*'):
			r = CSSASTBool(True)
		elif self.ac('#'):
			r = CSSASTId(self.c())
		elif self.ac('.'):
			r = CSSASTClass(self.c())
		else:
			r = CSSASTTag(self.c())

		if self.a('.') or self.a('#'):
			r = CSSASTAnd(r, self.parse_rule_chain())

		return r
	
	def parse_block(self):
		
		self.ac(' ')

		if not self.ac('{'):
			return dict()

		declarations = {}

		self.ac(' ')
		while not self.ac('}'):
			k, v = self.parse_declaration()
			declarations[k] = v
			self.ac(' ')

		return declarations 
	
	def parse_declaration(self):
		
		k = self.c()
		v = ''

		if self.ac(':'):
			while not (self.ac(';') or self.a('}')):
				v += self.c()

		v = v.strip()
		if v.lower().endswith('!important'):
			v = v[:-10]

		return k, v
		

def parse(css):
	
	lexer = CSSLexer(css)
	parser = CSSParser(lexer)

	rs = CSSRuleset()

	parser.populate_ruleset(rs)

	return rs


class CSSRuleset(object):
	
	def __init__(self):
		
		self.ruleset = []
	
	def rules(self, el):
		
		obj = {}
		
		for rule in self.ruleset:
			if rule[0](el):
				obj.update(rule[1])
		
		return obj

csscolors = {
  "aliceblue": "#f0f8ff",
  "antiquewhite": "#faebd7",
  "aqua": "#00ffff",
  "aquamarine": "#7fffd4",
  "azure": "#f0ffff",
  "beige": "#f5f5dc",
  "bisque": "#ffe4c4",
  "black": "#000000",
  "blanchedalmond": "#ffebcd",
  "blue": "#0000ff",
  "blueviolet": "#8a2be2",
  "brown": "#a52a2a",
  "burlywood": "#deb887",
  "cadetblue": "#5f9ea0",
  "chartreuse": "#7fff00",
  "chocolate": "#d2691e",
  "coral": "#ff7f50",
  "cornflowerblue": "#6495ed",
  "cornsilk": "#fff8dc",
  "crimson": "#dc143c",
  "cyan": "#00ffff",
  "darkblue": "#00008b",
  "darkcyan": "#008b8b",
  "darkgoldenrod": "#b8860b",
  "darkgray": "#a9a9a9",
  "darkgreen": "#006400",
  "darkgrey": "#a9a9a9",
  "darkkhaki": "#bdb76b",
  "darkmagenta": "#8b008b",
  "darkolivegreen": "#556b2f",
  "darkorange": "#ff8c00",
  "darkorchid": "#9932cc",
  "darkred": "#8b0000",
  "darksalmon": "#e9967a",
  "darkseagreen": "#8fbc8f",
  "darkslateblue": "#483d8b",
  "darkslategray": "#2f4f4f",
  "darkslategrey": "#2f4f4f",
  "darkturquoise": "#00ced1",
  "darkviolet": "#9400d3",
  "deeppink": "#ff1493",
  "deepskyblue": "#00bfff",
  "dimgray": "#696969",
  "dimgrey": "#696969",
  "dodgerblue": "#1e90ff",
  "firebrick": "#b22222",
  "floralwhite": "#fffaf0",
  "forestgreen": "#228b22",
  "fuchsia": "#ff00ff",
  "gainsboro": "#dcdcdc",
  "ghostwhite": "#f8f8ff",
  "gold": "#ffd700",
  "goldenrod": "#daa520",
  "gray": "#808080",
  "green": "#008000",
  "greenyellow": "#adff2f",
  "grey": "#808080",
  "honeydew": "#f0fff0",
  "hotpink": "#ff69b4",
  "indianred": "#cd5c5c",
  "indigo": "#4b0082",
  "ivory": "#fffff0",
  "khaki": "#f0e68c",
  "lavender": "#e6e6fa",
  "lavenderblush": "#fff0f5",
  "lawngreen": "#7cfc00",
  "lemonchiffon": "#fffacd",
  "lightblue": "#add8e6",
  "lightcoral": "#f08080",
  "lightcyan": "#e0ffff",
  "lightgoldenrodyellow": "#fafad2",
  "lightgray": "#d3d3d3",
  "lightgreen": "#90ee90",
  "lightgrey": "#d3d3d3",
  "lightpink": "#ffb6c1",
  "lightsalmon": "#ffa07a",
  "lightseagreen": "#20b2aa",
  "lightskyblue": "#87cefa",
  "lightslategray": "#778899",
  "lightslategrey": "#778899",
  "lightsteelblue": "#b0c4de",
  "lightyellow": "#ffffe0",
  "lime": "#00ff00",
  "limegreen": "#32cd32",
  "linen": "#faf0e6",
  "magenta": "#ff00ff",
  "maroon": "#800000",
  "mediumaquamarine": "#66cdaa",
  "mediumblue": "#0000cd",
  "mediumorchid": "#ba55d3",
  "mediumpurple": "#9370db",
  "mediumseagreen": "#3cb371",
  "mediumslateblue": "#7b68ee",
  "mediumspringgreen": "#00fa9a",
  "mediumturquoise": "#48d1cc",
  "mediumvioletred": "#c71585",
  "midnightblue": "#191970",
  "mintcream": "#f5fffa",
  "mistyrose": "#ffe4e1",
  "moccasin": "#ffe4b5",
  "navajowhite": "#ffdead",
  "navy": "#000080",
  "oldlace": "#fdf5e6",
  "olive": "#808000",
  "olivedrab": "#6b8e23",
  "orange": "#ffa500",
  "orangered": "#ff4500",
  "orchid": "#da70d6",
  "palegoldenrod": "#eee8aa",
  "palegreen": "#98fb98",
  "paleturquoise": "#afeeee",
  "palevioletred": "#db7093",
  "papayawhip": "#ffefd5",
  "peachpuff": "#ffdab9",
  "peru": "#cd853f",
  "pink": "#ffc0cb",
  "plum": "#dda0dd",
  "powderblue": "#b0e0e6",
  "purple": "#800080",
  "rebeccapurple": "#663399",
  "red": "#ff0000",
  "rosybrown": "#bc8f8f",
  "royalblue": "#4169e1",
  "saddlebrown": "#8b4513",
  "salmon": "#fa8072",
  "sandybrown": "#f4a460",
  "seagreen": "#2e8b57",
  "seashell": "#fff5ee",
  "sienna": "#a0522d",
  "silver": "#c0c0c0",
  "skyblue": "#87ceeb",
  "slateblue": "#6a5acd",
  "slategray": "#708090",
  "slategrey": "#708090",
  "snow": "#fffafa",
  "springgreen": "#00ff7f",
  "steelblue": "#4682b4",
  "tan": "#d2b48c",
  "teal": "#008080",
  "thistle": "#d8bfd8",
  "tomato": "#ff6347",
  "turquoise": "#40e0d0",
  "violet": "#ee82ee",
  "wheat": "#f5deb3",
  "white": "#ffffff",
  "whitesmoke": "#f5f5f5",
  "yellow": "#ffff00",
  "yellowgreen": "#9acd32"
}


def color(css):
	
	if css == 'transparent':
		return (0,0,0,0)

	if css[0] == '#':
		if len(css) == 4:
			return (int(css[1], 16)*17,int(css[2], 16)*17,int(css[3], 16)*17, 255)
		if len(css) == 7:
			return (int(css[1:3], 16),int(css[3:5], 16),int(css[5:], 16), 255)
	
	return color(csscolors.get(css, '#000'))


def length(css, parent, auto=0):
	
	if css == '0':
		return 0
	
	if css == 'auto':
		return auto

	if css.endswith('px'):
		return int(css[:-2])
	
	if css.endswith('%'):
		return int(float(css[:-1]) * parent / 100)
	
	return 0
