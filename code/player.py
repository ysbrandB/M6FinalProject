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
        self.grounded = False
        self.collected_coins=0
        self.gravity = 0.09
        self.friction = -0.12
        self.max_hor_vel = 3.5
        self.max_ver_vel = 2.11
        self.initial_acceleration = 0.1

        self.DEFAULT_SPEED = 1.0
        self.RUNNING_SPEED = 1.45
        self.speed_multiplier = self.DEFAULT_SPEED  # used for e.g. running
        self.jump_speed_multiplier = 1.5

        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0, 0)
        self.acceleration = pygame.Vector2(0, self.gravity)

        self.animation = player['animation_idle']
        self.STILL = 0
        self.WALKING = 1
        self.RUNNING = 2
        self.JUMPING = 3
        self.current_state = self.STILL
        self.last_state = self.STILL
        self.frame_index = 0
        self.frame_time = 0

        # temporary!
        self.ground_level = y

        self.jump_snd = pygame.mixer.Sound('../sfx/jump.wav')

    def live(self, dt, tiles, coins):
        self.collect_coins(coins)
        self.horizontal_movement(dt)
        self.vertical_movement(dt)
        self.collision(tiles)
        self.update_animation_state()
        self.animate(dt)
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
        if abs(self.velocity.x) < 0.03:
            self.velocity.x = 0
        self.position.x += self.velocity.x * dt + (self.acceleration.x * 0.5) * (dt * dt)

    def vertical_movement(self, dt):
        self.velocity.y += self.acceleration.y * dt
        if self.velocity.y > self.max_ver_vel:
            self.velocity.y = self.max_ver_vel
        self.position.y += self.velocity.y * dt + (self.acceleration.x * 0.5) * (dt * dt)

    def collision(self, tiles):
        found_floor = False
        for tile_group in tiles:
            if tile_group == "terrain":
                for tile in tiles[tile_group]:
                    tile_x, tile_y, size = tile.rect[:-1]

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
                            self.jumping = False
                            found_floor = True

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
        if not found_floor:
            self.grounded = False

    def jump(self):
        if self.grounded:
            self.jumping = True
            self.velocity.y = -self.max_ver_vel * self.jump_speed_multiplier
            self.grounded = False
            self.jump_snd.play()

    def draw(self):
        sprite = self.get_current_sprite()
        to_draw = pygame.transform.flip(sprite, self.flipped, 0)
        self.surface.blit(to_draw, (self.position.x, self.position.y))

    def update_animation_state(self):
        if self.jumping and not self.grounded:
            self.current_state = self.JUMPING
            return
        if self.left ^ self.right:
            if self.speed_multiplier == self.RUNNING_SPEED:
                self.current_state = self.RUNNING
                return
            else:
                self.current_state = self.WALKING
                return
        self.current_state = self.STILL

    def animate(self, dt):
        if not self.current_state == self.last_state:
            self.frame_index = 0
            self.last_state = self.current_state
        self.animation = player['animation_idle']
        match self.current_state:
            case self.WALKING:
                self.animation = player['animation_walking']
            case self.RUNNING:
                self.animation = player['animation_running']
            case self.JUMPING:
                self.animation = player['animation_jumping']

        # reminder that dt has already been multiplied by 0.1, therefore we multiply by 0.01 to get seconds
        self.frame_time += dt * 0.01
        if self.frame_time >= 1 / self.animation['fps']:
            self.frame_time = 0
            self.frame_index += 1
            if self.frame_index > len(self.animation['frames']) - 1:
                self.frame_index = 0

    def get_current_sprite(self):
        return self.sprites[self.animation['frames'][self.frame_index]]

    def collect_coins(self, coins):
        for coin in coins:
            if self.position.distance_to(coin.position)<5:
                self.collected_coins+=1
                coins.remove(coin)
