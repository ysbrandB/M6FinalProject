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

        self.gravity = 0.15
        self.friction = -0.12
        self.max_hor_vel = 4
        self.max_ver_vel = 4
        self.initial_acceleration = 0.15
        self.speed_multiplier = 1.0  # used for e.g. running

        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0, 0)
        self.acceleration = pygame.Vector2(0, self.gravity)

        # temporary!
        self.ground_level = y

        self.jump_snd = pygame.mixer.Sound('../sfx/jump.wav')

    def live(self, dt):
        self.horizontal_movement(dt)
        self.vertical_movement(dt)
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

        if self.position.y > self.ground_level:
            self.grounded = True
            self.velocity.y = 0
            self.position.y = self.ground_level

    def jump(self):
        if self.grounded:
            self.jumping = True
            self.velocity.y = -self.max_ver_vel - 1
            self.grounded = False
            self.jump_snd.play()

    def draw(self):
        image = pygame.transform.flip(self.sprites[0], self.flipped, 0)
        self.surface.blit(image, (self.position.x, self.position.y))


