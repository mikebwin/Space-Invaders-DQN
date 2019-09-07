scale = 2

class Player:

	def __init__(self, x_loc, y_loc, width, height, velocity=0):
		self.color = (0, 255, 0)  # RGB: Green
		self.x_loc = x_loc
		self.y_loc = y_loc
		self.width = width
		self.height = height
		self.velocity = velocity

	def move(self, direction):
		if direction == 'left':
			self.x_loc -= self.velocity
		if direction == 'right':
			self.x_loc += self.velocity

class Squid():
	def __init__(self, x_loc, y_loc, velocity):
		self.color = (230,230,250)  # RGB:
		self.x_loc = x_loc
		self.y_loc = y_loc
		self.width = 8 * scale
		self.height = 8 * scale
		self.velocity = velocity
		self.alive = True

	def move(self, direction):
		if direction == 'left':
			self.x_loc -= self.velocity
		if direction == 'right':
			self.x_loc += self.velocity

class Crab():
	def __init__(self, x_loc, y_loc, velocity):
		self.color = (173,216,230)  # RGB:
		self.x_loc = x_loc
		self.y_loc = y_loc
		self.width = 11 * scale
		self.height = 8 * scale
		self.velocity = velocity
		self.alive = True

	def move(self, direction):
		if direction == 'left':
			self.x_loc -= self.velocity
		if direction == 'right':
			self.x_loc += self.velocity

class Octopus():
	def __init__(self, x_loc, y_loc, velocity):
		self.color = (255,127,80)  # RGB:
		self.x_loc = x_loc
		self.y_loc = y_loc
		self.width = 12 * scale
		self.height = 8 * scale
		self.velocity = velocity
		self.alive = True

	def move(self, direction):
		if direction == 'left':
			self.x_loc -= self.velocity
		if direction == 'right':
			self.x_loc += self.velocity

class Block():
	def __init__(self, x_loc, y_loc):
		self.x_loc = x_loc
		self.y_loc = y_loc
		self.width = 8 * scale
		self.height = 8 * scale
		self.level = 3
		self.alive = True
		self.color = (0,178,0)
