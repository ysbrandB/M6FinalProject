from game_data import player
from helpers import import_cut_graphics
from settings import tile_size
import pygame


class Player:
    def __init__(self, x, y, level):
        self.level = level
        self.surface = level.display_surface
        self.sprites = import_cut_graphics(player['sprite_sheet_path'])

        self.left = False
        self.right = False
        self.flipped = False
        self.jumping = False
        self.running = False
        self.grounded = False

        self.gravity = 0.09
        self.friction = -0.12
        self.max_hor_vel = 3.5
        self.max_ver_vel = 2.5
        self.initial_acceleration = 0.1

        self.DEFAULT_SPEED = 1.0
        self.RUNNING_SPEED = 1.4
        self.speed_multiplier = self.DEFAULT_SPEED  # used for e.g. running

        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0, 0)
        self.acceleration = pygame.Vector2(0, self.gravity)

        # temporary!
        self.ground_level = y

        self.jump_snd = pygame.mixer.Sound('../sfx/jump.wav')

    def live(self, dt, tiles):
        self.horizontal_movement(dt)
        self.vertical_movement(dt)
        self.collision(tiles)
        self.draw()

    def horizontal_movement(self, dt):
        self.acceleration.x = 0
        if self.left:
            self.acceleration.x -= self.initial_acceleration * self.speed_multiplier
        if self.right:
            self.acceleration.x += self.initial_acceleration * self.speed_multiplier
        self.acceleration.x += self.velocity.x * self.friction
        self.velocity.x += self.acceleration.x * dt
        self.velocity.x = max(-self.max_hor_vel * self.speed_multiplier,
                              min(self.max_hor_vel * self.speed_multiplier, self.velocity.x))
        if abs(self.velocity.x) < 0.01:
            self.velocity.x = 0
        self.position.x += self.velocity.x * dt + (self.acceleration.x * 0.5) * (dt * dt)

    def vertical_movement(self, dt):
        self.velocity.y += self.acceleration.y * dt
        if self.velocity.y > self.max_ver_vel:
            self.velocity.y = self.max_ver_vel
        self.position.y += self.velocity.y * dt + (self.acceleration.x * 0.5) * (dt * dt)

    def collision(self, tiles):
        #tiles = self.level.static_sprites
        found_floor = False
        for tile_group in tiles:
            if tile_group == "terrain":
                for tile in tiles[tile_group]:
                    tile_x, tile_y, size = tile.rect[:-1]

                    # horizontal collisions
                    if abs(self.position.y - tile_y) < size - 4:
                        # left wall collision
                        if tile_x + size >= self.position.x > tile_x:
                            self.position.x = tile_x + size
                            self.acceleration.x *= 0.75
                        # right wall collision
                        if self.position.x + size > tile_x > self.position.x - size:
                            self.position.x = tile_x - size
                            self.acceleration.x *= 0.75

                    # vertical collisions
                    if abs(self.position.x - tile_x) < size - 4:
                        # ceiling
                        if tile_y + size - 2 > self.position.y > tile_y:
                            self.position.y = tile_y + size - 2
                            self.velocity.y = 0
                        # floor
                        if self.position.y + size > tile_y > self.position.y:
                            self.position.y = tile_y - size
                            self.velocity.y = 0
                            self.grounded = True
                            found_floor = True
        if not found_floor:
            self.grounded = False

    def jump(self):
        if self.grounded:
            self.jumping = True
            self.velocity.y = -self.max_ver_vel - 1
            self.grounded = False
            self.jump_snd.play()

    def damn_idk_is_there_a_ceiling(self):
        pass

    def draw(self):
        image = pygame.transform.flip(self.sprites[0], self.flipped, 0)
        self.surface.blit(image, (self.position.x, self.position.y))


