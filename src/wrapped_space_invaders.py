import random, time, pygame, sys
from pygame.locals import *
from src.agents import Player, Squid, Octopus, Crab, Block

scale = 2

window_width = 224 * scale
window_height = 256 * scale

player_width = 20 * scale
player_height = 8 * scale
player_loc = (20 * scale, window_height - 20 * scale)
player_velocity = 5 * scale

bullet_velocity = 15 * scale
bullet_width = 2 * scale
bullet_height = 8 * scale


class GameState:
	def __init__(self):
		global FPSCLOCK, screen, BASICFONT, BIGFONT
		pygame.init()
		FPSCLOCK = pygame.time.Clock()
		screen = pygame.display.set_mode((window_width, window_height))
		BASICFONT = pygame.font.Font('freesansbold.ttf', 18)
		BIGFONT = pygame.font.Font('freesansbold.ttf', 100)
		pygame.display.set_caption('Shoddy - SPACE INVADERS')

		self.enemy_direction = 'right'
		self.enemy_bullets = []
		self.bullet = None

		self.enemies = [[], [], [], [], []]
		self.num_enemies = 55
		self.blocks = []
		self.player = Player(player_loc[0], player_loc[1], player_width, player_height, velocity=player_velocity)

		enemy_velocity = 2
		first_enemy_x = 10 * scale
		first_enemy_y = 50 * scale
		for row in range(0, 5):
			for col in range(0, 11):
				if row == 0:
					self.enemies[row].append(Squid(first_enemy_x + 16 * scale * (col + 1),
					                          first_enemy_y, enemy_velocity))
				elif row == 1 or row == 2:
					self.enemies[row].append(Crab(first_enemy_x + 16 * scale * (col + 1),
					                         first_enemy_y + 16 * scale * row, enemy_velocity))
				else:
					self.enemies[row].append(Octopus(first_enemy_x + 16 * scale * (col + 1),
					                            first_enemy_y + 16 * scale * row, enemy_velocity))

		first_block_y = window_height - 40 * scale
		# create a bunch of hiding blocks for player
		for row in range(first_block_y - 24 * scale, first_block_y, scale):
			for col in range(0, window_width):
				if (row == first_block_y or row == first_block_y - 8 * scale
						or row == first_block_y - 16 * scale or row == first_block_y - 24 * scale):
					if (col > 36 * scale and col <= 60 * scale or col > 100 * scale
					    and col < 124 * scale or col > 164 * scale and col < 188 * scale) and col % 16 == 0:
						self.blocks.insert(0, Block(col, row))

		self.frame_step([1, 0, 0, 0])
		pygame.display.update()

	def reinit(self):
		self.enemy_direction = 'right'
		self.enemy_bullets = []
		self.bullet = None

		self.enemies = [[], [], [], [], []]
		self.num_enemies = 55
		self.blocks = []
		self.player = Player(player_loc[0], player_loc[1], player_width, player_height, velocity=player_velocity)

		enemy_velocity = 2
		first_enemy_x = 10 * scale
		first_enemy_y = 50 * scale
		for row in range(0, 5):
			for col in range(0, 11):
				if row == 0:
					self.enemies[row].append(Squid(first_enemy_x + 16 * scale * (col + 1),
					                               first_enemy_y, enemy_velocity))
				elif row == 1 or row == 2:
					self.enemies[row].append(Crab(first_enemy_x + 16 * scale * (col + 1),
					                              first_enemy_y + 16 * scale * row, enemy_velocity))
				else:
					self.enemies[row].append(Octopus(first_enemy_x + 16 * scale * (col + 1),
					                                 first_enemy_y + 16 * scale * row, enemy_velocity))

		first_block_y = window_height - 40 * scale
		# create a bunch of hiding blocks for player
		for row in range(first_block_y - 24 * scale, first_block_y, scale):
			for col in range(0, window_width):
				if (row == first_block_y or row == first_block_y - 8 * scale
						or row == first_block_y - 16 * scale or row == first_block_y - 24 * scale):
					if (col > 36 * scale and col <= 60 * scale or col > 100 * scale
					    and col < 124 * scale or col > 164 * scale and col < 188 * scale) and col % 16 == 0:
						self.blocks.insert(0, Block(col, row))

		self.frame_step([1, 0, 0, 0])
		pygame.display.update()


	def frame_step(self, input):
		reward = 0
		terminal = False

		if self.num_enemies == 0:
			print("YOU WON")
			reward += 100000
			image_data = pygame.surfarray.array3d(pygame.display.get_surface())
			terminal = True
			return image_data, reward, terminal

		if(input[1] == 1) and not self.out_of_bounds("Player", self.player.x_loc - self.player.velocity, self.player.y_loc,
		                                             self.player.width):
			self.player.move('left')
		elif (input[2] == 1) and not self.out_of_bounds("Player", self.player.x_loc + self.player.velocity, self.player.y_loc,
		                                              self.player.width):
			self.player.move('right')
		# firing player bullet
		elif input[3] == 1:
			# can only fire one bullet at a time
			if self.bullet is None:
				self.bullet = (self.player.x_loc + self.player.width / 2, self.player.y_loc, bullet_width, bullet_height)
		# firing enemy bullet
		if len(self.enemy_bullets) < 3 and random.random() < .03:
			random_enemy = self.enemies[random.randint(0, 4)][random.randint(0, 10)]
			enemy_bullet = (
			random_enemy.x_loc + random_enemy.width / 2, random_enemy.y_loc, bullet_width, bullet_height)
			self.enemy_bullets.append(enemy_bullet)

		screen.fill((0, 0, 0))

		# update both the enemies location and the player bullet
		self.enemy_direction = self.update_enemies(self.enemy_direction)
		if self.bullet:
			self.bullet = self.bullet[:1] + (self.bullet[1] - bullet_velocity,) + self.bullet[2:]  # update location of bullet
			if self.out_of_bounds("Player_Bullet", *self.bullet[:-1]):
				self.bullet = None
				reward -= 5
			elif self.check_enemy_hit(self.bullet):
				self.bullet = None
				reward += 50
			elif self.check_block_hit(self.bullet):
				self.bullet = None
				reward -= 10

		# move all enemy bullets and check if out of bounds. then empty out nulls
		for idx_bullet, enemy_bullet in enumerate(self.enemy_bullets):
			self.enemy_bullets[idx_bullet] = enemy_bullet[:1] + (enemy_bullet[1] + bullet_velocity / 2,) + enemy_bullet[2:]
			if self.out_of_bounds("Enemy_Bullet", *enemy_bullet[:-1]):
				self.enemy_bullets[idx_bullet] = None
			elif self.check_block_hit(enemy_bullet):
				self.enemy_bullets[idx_bullet] = None
		self.enemy_bullets = list(filter(None, self.enemy_bullets))

		# look through enemy bullets to see if any hit player
		for enemy_bullet in self.enemy_bullets:
			if self.check_player_hit(enemy_bullet, self.player):
				print("YOU LOST")
				reward -= 1000
				image_data = pygame.surfarray.array3d(pygame.display.get_surface())
				terminal = True

				self.reinit()
				return image_data, reward, terminal

		# for when enemies run into the blocks or the player
		for type in self.enemies:
			for enemy in type:
				if self.check_player_hit((enemy.x_loc, enemy.y_loc, enemy.width, enemy.height), self.player):
					print("YOU LOST")
					reward -= 1000
					image_data = pygame.surfarray.array3d(pygame.display.get_surface())
					terminal = True

					self.reinit()
					return image_data, reward, terminal
				self.check_block_hit((enemy.x_loc, enemy.y_loc, enemy.width, enemy.height), "enemy")

		# if don't kill enemies fast enough
		if self.enemies[-1][-1].y_loc > window_height:
			print("YOU LOST")
			reward -= 1000
			image_data = pygame.surfarray.array3d(pygame.display.get_surface())
			terminal = True

			self.reinit()
			return image_data, reward, terminal

		self.draw_enemies()
		for enemy_bullet in self.enemy_bullets:
			pygame.draw.rect(screen, (255,150,127), enemy_bullet)
		if self.bullet:
			pygame.draw.rect(screen, (255,255,255), self.bullet)
		pygame.draw.rect(screen, self.player.color, (self.player.x_loc, self.player.y_loc, self.player.width, self.player.height))
		for block in self.blocks:
			color = (0,178,0) if block.level == 3 else (0,124,0) if block.level == 2 else (0, 80, 0)
			pygame.draw.rect(screen, color,
			                 (block.x_loc, block.y_loc, block.width, block.height)) if block.alive else None

		pygame.display.update()
		image_data = pygame.surfarray.array3d(pygame.display.get_surface())

		return image_data, reward, terminal


	def check_player_hit(self, bullet, player):
		corners = [
			(bullet[0], bullet[1]),
			(bullet[0] + bullet[2], bullet[1]),
			(bullet[0], bullet[1] + bullet[3]),
			(bullet[0] + bullet[2], bullet[1] + bullet[3])
		]
		okay_then = [x if x[0] >= player.x_loc and x[1] >= player.y_loc
		                  and (x[0] <= player.x_loc + player.width) and (x[1] <= player.y_loc + player.height)
		             else None for x in corners]
		for item in okay_then:
			if item is not None:
				return True
		return False


	def check_block_hit(self, bullet, type="bullet"):
		corners = [
			(bullet[0], bullet[1]),
			(bullet[0] + bullet[2], bullet[1]),
			(bullet[0], bullet[1] + bullet[3]),
			(bullet[0] + bullet[2], bullet[1] + bullet[3])
		]
		for idx_block, block in enumerate(self.blocks):
			okay_then = [x if x[0] >= block.x_loc and x[1] >= block.y_loc
			                  and (x[0] <= block.x_loc + block.width) and (x[1] <= block.y_loc + block.height)
			                  and block.alive else None for x in corners]
			for item in okay_then:
				if item is not None:
					if type == "bullet":
						self.blocks[idx_block].level -= 1
						if self.blocks[idx_block].level <= 0:
							self.blocks[idx_block].alive = False
					else:
						self.blocks[idx_block].alive = False
						self.blocks[idx_block].level = 0
					return True
		return False


	def check_enemy_hit(self, bullet):
		corners = [
			(bullet[0], bullet[1]),
			(bullet[0] + bullet[2], bullet[1]),
			(bullet[0], bullet[1] + bullet[3]),
			(bullet[0] + bullet[2], bullet[1] + bullet[3])
		]
		for idx_type, e_type in enumerate(self.enemies):
			for idx_enemy, enemy in enumerate(e_type):
				okay_then = [x if x[0] >= enemy.x_loc and x[1] >= enemy.y_loc
				                  and (x[0] <= enemy.x_loc + enemy.width) and (x[1] <= enemy.y_loc + enemy.height)
				                  and enemy.alive else None for x in corners]
				for item in okay_then:
					if item is not None:
						self.enemies[idx_type][idx_enemy].alive = False
						return True

		return False


	def draw_enemies(self):
		for idx_type, e_type in enumerate(self.enemies):
			for idx_enemy, enemy in enumerate(e_type):
				(pygame.draw.rect(screen, enemy.color, (enemy.x_loc, enemy.y_loc, enemy.width, enemy.height))
				 if enemy.alive else None)


	def out_of_bounds(self, agent_type, agent_x, agent_y, agent_width):
		if agent_type == "Player" or agent_type == "Enemy":
			if agent_x > 0 and agent_x + agent_width < window_width:
				return False

		if agent_type == "Player_Bullet":
			if agent_y > 0:
				return False

		if agent_type == "Enemy_Bullet":
			if agent_y < window_height:
				return False

		return True


	def update_enemies(self, direction):
		move_down = False
		right_check = self.enemies[-1][-1]
		if direction == "right" and self.out_of_bounds("Enemy", right_check.x_loc + 4, right_check.y_loc,
		                                          right_check.width):
			direction = "left"
			move_down = True

		left_check = self.enemies[0][0]
		if direction == "left" and self.out_of_bounds("Enemy", left_check.x_loc - 4, left_check.y_loc,
		                                         left_check.width):
			direction = "right"
			move_down = True

		for idx_type, e_type in enumerate(self.enemies):
			for idx_enemy, enemy in enumerate(e_type):
				if direction == "left":
					self.enemies[idx_type][idx_enemy].x_loc -= enemy.velocity
				else:
					self.enemies[idx_type][idx_enemy].x_loc += enemy.velocity
				if move_down:
					self.enemies[idx_type][idx_enemy].y_loc += 4 * scale

		return direction
