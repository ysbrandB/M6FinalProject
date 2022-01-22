from tiles import AnimatableTile
import pygame


class QuestionBlock(AnimatableTile):
    def __init__(self, size, position, frames, data, scared_ghosts):
        super().__init__(size, position, frames, data)
        self.old_y = self.position.y
        self.gravity = 0.01
        self.velocity = pygame.Vector2(0, 0)
        self.acceleration = pygame.Vector2(0, self.gravity)
        self.hit = False
        self.inactive = False
        self.scared_ghosts = scared_ghosts

    def live(self, dt, surface):
        if self.hit:
            self.velocity.y += self.acceleration.y * dt
            self.position.y += self.velocity.y * dt + (self.acceleration.x * 0.5) * (dt * dt)

            if abs(self.position.y - self.old_y) < 1 and self.velocity.y > 0:
                self.position.y = self.old_y
                self.hit = False

        self.animate(dt)
        self.draw(surface)

    def player_collided(self):
        if not self.inactive:
            self.hit = True
            self.inactive = True
            self.velocity.y = -0.3
            self.animation = self.data['animation_hit']
