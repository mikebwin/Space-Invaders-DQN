import pygame
from src.agents import Player, Squid, Octopus, Crab, Block
import random
import math

scale = 2

window_width = 224 * scale
window_height = 256 * scale

player_width = 20 * scale
player_height = 8 * scale
player_loc = (20 * scale, window_height - 20 * scale)
player_velocity = 5 * scale

enemies = [[], [], [], [], []]
enemy_velocity = 2
first_enemy_x = 10 * scale
first_enemy_y = 50 * scale
for row in range(0, 5):
	for col in range(0, 11):
		if row == 0:
			enemies[row].append(Squid(first_enemy_x + 16 * scale * (col + 1),
			                          first_enemy_y, enemy_velocity))
		elif row == 1 or row == 2:
			enemies[row].append(Crab(first_enemy_x + 16 * scale * (col + 1),
			                         first_enemy_y + 16 * scale * row, enemy_velocity))
		else:
			enemies[row].append(Octopus(first_enemy_x + 16 * scale * (col + 1),
			                            first_enemy_y + 16 * scale * row, enemy_velocity))
num_enemies = 55

first_block_y = window_height - 40 * scale
# create a bunch of hiding blocks for player
blocks = []
for row in range(first_block_y-24*scale, first_block_y, scale):
	for col in range(0, window_width):
		if (row == first_block_y or row == first_block_y - 8 * scale
				or row == first_block_y - 16 * scale or row == first_block_y - 24 * scale):
			if (col > 36 * scale and col <= 60 * scale or col > 100 * scale
			    and col < 124 * scale or col > 164 * scale and col < 188 * scale) and col % 16 == 0:
				blocks.insert(0, Block(col, row))


def main():
	pygame.init()

	screen = pygame.display.set_mode((window_width, window_height))
	running = True

	player = Player(player_loc[0], player_loc[1], player_width, player_height, velocity=player_velocity)
	enemy_direction = 'right'
	enemy_bullets = []
	bullet = None
	bullet_velocity = 15 * scale
	bullet_width = 2 * scale
	bullet_height = 8 * scale
	score = 0


	while running:
		pygame.time.delay(50)

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
		if num_enemies == 0:
			print("YOU WON")
			running = False

		keys = pygame.key.get_pressed()

		# movement
		if keys[pygame.K_LEFT]:
			if not out_of_bounds("Player", player.x_loc - player.velocity, player.y_loc, player.width, player.height):
				player.move('left')
		if keys[pygame.K_RIGHT]:
			if not out_of_bounds("Player", player.x_loc + player.velocity, player.y_loc, player.width, player.height):
				player.move('right')
		# firing player bullet
		if keys[pygame.K_UP]:
			# can only fire one bullet at a time
			if bullet is None:
				bullet = (player.x_loc + player.width / 2, player.y_loc, bullet_width, bullet_height)
		# firing enemy bullet
		if len(enemy_bullets) < 3 and random.random() < .03:
			random_enemy = enemies[random.randint(0, 4)][random.randint(0, 10)]
			enemy_bullet = (random_enemy.x_loc + random_enemy.width / 2, random_enemy.y_loc, bullet_width, bullet_height)
			enemy_bullets.append(enemy_bullet)

		# wipe to black every time, refresh
		screen.fill((0, 0, 0))

		# update both the enemies location and the player bullet
		enemy_direction = update_enemies(enemy_direction)
		if bullet:
			bullet = bullet[:1] + (bullet[1] - bullet_velocity,) + bullet[2:]  # update location of bullet
			if out_of_bounds("Player_Bullet", *bullet):
				bullet = None
			elif check_enemy_hit(bullet):
				bullet = None
			elif check_block_hit(bullet):
				bullet = None

		# move all enemy bullets and check if out of bounds. then empty out nulls
		for idx_bullet, enemy_bullet in enumerate(enemy_bullets):
			enemy_bullets[idx_bullet] = enemy_bullet[:1] + (enemy_bullet[1] + bullet_velocity/2,) + enemy_bullet[2:]
			if out_of_bounds("Enemy_Bullet", *enemy_bullet):
				enemy_bullets[idx_bullet] = None
			elif check_block_hit(enemy_bullet):
				enemy_bullets[idx_bullet] = None
		enemy_bullets = list(filter(None, enemy_bullets))

		# look through enemy bullets to see if any hit player
		for enemy_bullet in enemy_bullets:
			if check_player_hit(enemy_bullet, player):
				running = False
				print("YOU LOST")

		for type in enemies:
			for enemy in type:
				if check_player_hit((enemy.x_loc, enemy.y_loc, enemy.width, enemy.height), player):
					# running = False
					print("YOU LOST")
				check_block_hit((enemy.x_loc, enemy.y_loc, enemy.width, enemy.height), "enemy")

		# then draw enemies, if bullet still on screen, and the player
		draw_enemies(screen)
		for enemy_bullet in enemy_bullets:
			pygame.draw.rect(screen, (255,150,127), enemy_bullet)
		if bullet:
			pygame.draw.rect(screen, (255,255,255), bullet)
		pygame.draw.rect(screen, player.color, (player.x_loc, player.y_loc, player.width, player.height))
		for block in blocks:
			color = (0,178,0) if block.level == 3 else (0,124,0) if block.level == 2 else (0, 80, 0)
			pygame.draw.rect(screen, color,
			                 (block.x_loc, block.y_loc, block.width, block.height)) if block.alive else None

		pygame.display.update()


def check_player_hit(bullet, player):
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

def check_block_hit(bullet, type="bullet"):
	corners = [
		(bullet[0], bullet[1]),
		(bullet[0] + bullet[2], bullet[1]),
		(bullet[0], bullet[1] + bullet[3]),
		(bullet[0] + bullet[2], bullet[1] + bullet[3])
	]
	for idx_block, block in enumerate(blocks):
		okay_then = [x if x[0] >= block.x_loc and x[1] >= block.y_loc
		                  and (x[0] <= block.x_loc + block.width) and (x[1] <= block.y_loc + block.height)
		                  and block.alive else None for x in corners]
		for item in okay_then:
			if item is not None:
				if type == "bullet":
					blocks[idx_block].level -= 1
					if blocks[idx_block].level <= 0:
						blocks[idx_block].alive = False
				else:
					blocks[idx_block].alive = False
					blocks[idx_block].level = 0
				return True
	return False

def check_enemy_hit(bullet):
	corners = [
		(bullet[0], bullet[1]),
		(bullet[0] + bullet[2], bullet[1]),
		(bullet[0], bullet[1] + bullet[3]),
		(bullet[0] + bullet[2], bullet[1] + bullet[3])
	]
	for idx_type, e_type in enumerate(enemies):
		for idx_enemy, enemy in enumerate(e_type):
			okay_then = [x if x[0] >= enemy.x_loc and x[1] >= enemy.y_loc
			                  and (x[0] <= enemy.x_loc + enemy.width) and (x[1] <= enemy.y_loc + enemy.height)
			                  and enemy.alive else None for x in corners]
			for item in okay_then:
				if item is not None:
					enemies[idx_type][idx_enemy].alive = False
					return True

	return False


def draw_enemies(screen):
	for idx_type, e_type in enumerate(enemies):
		for idx_enemy, enemy in enumerate(e_type):
			(pygame.draw.rect(screen, enemy.color, (enemy.x_loc, enemy.y_loc, enemy.width, enemy.height))
			 if enemy.alive else None)


def update_enemies(direction):
	move_down = False
	right_check = enemies[-1][-1]
	if direction == "right" and out_of_bounds("Enemy", right_check.x_loc + 4, right_check.y_loc,
	                                          right_check.width, right_check.height):
		direction = "left"
		move_down = True

	left_check = enemies[0][0]
	if direction == "left" and out_of_bounds("Enemy", left_check.x_loc - 4, left_check.y_loc,
	                                         left_check.width, left_check.height):
		direction = "right"
		move_down = True

	for idx_type, e_type in enumerate(enemies):
		for idx_enemy, enemy in enumerate(e_type):
			if direction == "left":
				enemies[idx_type][idx_enemy].x_loc -= enemy.velocity * math.sqrt(55/(num_enemies+1))
			else:
				enemies[idx_type][idx_enemy].x_loc += enemy.velocity * math.sqrt(55/(num_enemies+1))
			if move_down:
				enemies[idx_type][idx_enemy].y_loc += 4 * scale

	return direction


def out_of_bounds(agent_type, agent_x, agent_y, agent_width, agent_height):
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



if __name__ == "__main__":
	# call the main function
	main()
