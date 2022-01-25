from tiles import AnimatableTile
import pygame
from settings import horizontal_tile_number, vertical_tile_number, tile_size as global_tile_size


class Player(AnimatableTile):
    def __init__(self, size, grid_position, frames, data):
        super().__init__(size, grid_position, frames, data)

        self.left = False
        self.right = False
        self.flipped = False
        self.jumping = False
        self.AAAAAAAAAAAAAAA_IT_HURTS = False
        self.jump_cooldown_timer = 0
        self.jump_cooldown = 10
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
        self.DEDE = 4
        self.current_state = self.STILL
        self.last_state = self.STILL

        self.jump_snd = pygame.mixer.Sound('../sfx/jump.wav')
        self.coin_snd = pygame.mixer.Sound('../sfx/coin.wav')
        self.ghost_snd = pygame.mixer.Sound('../sfx/ghost.wav')
        self.dede_snd = pygame.mixer.Sound('../sfx/🦀mario🦀is🦀gone.wav')
        self.ghost_snd.play(-1)
        self.teleport_cooldown = 0

    def live(self, dt, surface, tiles):
        self.jump_cooldown_timer += dt
        self.horizontal_movement(dt)
        self.vertical_movement(dt)
        self.collision(tiles)
        self.grid_position = pygame.math.Vector2(round(self.position.x / self.size),
                                                 round(self.position.y / self.size))
        self.update_animation_state()
        self.set_correct_animation()
        self.animate(dt)
        self.draw(surface)
        self.detect_ghosts(tiles['ghosts'])

        if self.teleport_cooldown > 0:
            self.teleport_cooldown -= dt

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
            if tile_group == 'terrain' or tile_group == 'question_blocks':

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

                            # scare the ghosts when collision with question blocks
                            if tile_group == 'question_blocks':
                                tile.player_collided()
                                for ghost in tiles['ghosts']:
                                    ghost.scare()

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

            elif 'pipe_head_pair' in tile_group:
                for tile in tiles[tile_group]:
                    rect = pygame.Rect(tile.position, (tile.size, tile.size))
                    if rect.collidepoint(self.position):
                        if self.teleport_cooldown <= 0:
                            self.teleport_cooldown = 500
                            self.position = tile.get_paired_location()

            elif tile_group == 'coins':
                for tile in tiles[tile_group]:
                    if self.get_center().distance_to(tile.get_center()) < 10:
                        self.collected_coins += 1
                        tiles[tile_group].remove(tile)
                        self.coin_snd.play()

        # bottom of the screen
        if self.position.y + size > vertical_tile_number * global_tile_size > self.position.y:
            self.position.y = vertical_tile_number * global_tile_size - size
            self.velocity.y = 0
            self.grounded = True
            self.jumping = False
            found_floor = True

        if not found_floor:
            self.grounded = False

    def jump(self):
        if self.grounded and self.jump_cooldown_timer > self.jump_cooldown:
            self.jumping = True
            self.velocity.y = -self.max_ver_vel * self.jump_speed_multiplier
            self.grounded = False
            self.jump_snd.play()
            self.jump_cooldown_timer = 0

    def draw(self, surface):
        # overwriting super to incorporate flipping
        to_draw = pygame.transform.flip(self.image, self.flipped, 0)
        surface.blit(to_draw, self.position)

    def update_animation_state(self):
        if not self.AAAAAAAAAAAAAAA_IT_HURTS:
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
        else:
            self.current_state = self.DEDE

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
            case self.DEDE:
                self.animation = self.data['animation_dede']

    def detect_ghosts(self, ghosts):
        nearest_ghost = ghosts[0]
        for ghost in ghosts:
            if ghost.manhattan_dist_to_player < nearest_ghost.manhattan_dist_to_player:
                nearest_ghost = ghost

        if nearest_ghost.manhattan_dist_to_player < 2:
            if ghost.state == ghost.SCARED or ghost.state == ghost.DEAD:
                ghost.die()
            else:
                self.die()

        volume = 0.5 - nearest_ghost.manhattan_dist_to_player / ((horizontal_tile_number + vertical_tile_number) / 2)
        self.ghost_snd.set_volume(volume)

    def get_facing_direction(self):
        vector = pygame.math.Vector2(1 if self.right else -1, 0)
        return vector

    def die(self):
        if not self.AAAAAAAAAAAAAAA_IT_HURTS:
            self.AAAAAAAAAAAAAAA_IT_HURTS = True
            self.update_animation_state()
            self.dede_snd.play()
