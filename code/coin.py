from tiles import AnimatableTile
import pygame


class Coin(AnimatableTile):
    def __init__(self, size, position, frames, data):
        super().__init__(size, position, frames, data)
        for i in range(len(self.frames)):
            self.frames[i] = pygame.transform.scale(self.frames[i], (8, 8))
        self.position.x += size / 2
        self.position.y += size / 2

    def live(self, dt, surface):
        self.animate(dt)
        self.draw(surface)
