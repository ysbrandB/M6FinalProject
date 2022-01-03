from tiles import AnimatableTile
import pygame


class Player(AnimatableTile):
    def __init__(self, size, grid_position, frames, data):
        super().__init__(size, grid_position, frames, data)

        self.left = False
        self.right = False
        self.flipped = False
        self.jumping = False
        self.grounded = False
        self.collected_coins = 0
        self.gravity = 0.09
        self.friction = -0.12
        self.max_hor_vel = 3.5
        self.max_ver_vel = 2.11
        self.initial_acceleration = 0.1

        self.DEFAULT_SPEED = 1.0
        self.RUNNING_SPEED = 1.45
        self.speed_multiplier = self.DEFAULT_SPEED  # used for e.g. running
        self.jump_speed_multiplier = 1.5

        self.velocity = pygame.Vector2(0, 0)
        self.acceleration = pygame.Vector2(0, self.gravity)

        self.STILL = 0
        self.WALKING = 1
        self.RUNNING = 2
        self.JUMPING = 3
        self.current_state = self.STILL
        self.last_state = self.STILL

        self.jump_snd = pygame.mixer.Sound('../sfx/jump.wav')
        self.coin_snd = pygame.mixer.Sound('../sfx/coin.wav')

    def live(self, dt, surface, tiles, coins):
        self.collect_coins(coins)
        self.horizontal_movement(dt)
        self.vertical_movement(dt)
        self.collision(tiles)
        self.grid_position = pygame.math.Vector2(round(self.position.x / self.size), round(self.position.y / self.size))
        self.update_animation_state()
        self.set_correct_animation()
        self.animate(dt)
        self.draw(surface)

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
            if tile_group == 'terrain':
                for tile in tiles[tile_group]:
                    tile_x = tile.position.x
                    tile_y = tile.position.y
                    size = tile.size

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

    def draw(self, surface):
        # overwriting super to incorporate flipping
        to_draw = pygame.transform.flip(self.image, self.flipped, 0)
        surface.blit(to_draw, self.position)

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

    def set_correct_animation(self):
        if not self.current_state == self.last_state:
            self.frame_index = 0
            self.last_state = self.current_state
        self.animation = self.data['animation_idle']
        match self.current_state:
            case self.WALKING:
                self.animation = self.data['animation_walking']
            case self.RUNNING:
                self.animation = self.data['animation_running']
            case self.JUMPING:
                self.animation = self.data['animation_jumping']

    def collect_coins(self, coins):
        for coin in coins:
            if self.get_center().distance_to(coin.get_center()) < 10:
                self.collected_coins += 1
                coins.remove(coin)
                self.coin_snd.play()
