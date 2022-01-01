from helpers import import_cut_graphics
from game_data import coins
import pygame
class Coin:
    def __init__(self, x, y, level):
        self.x=x
        self.y=y
        self.sprites = import_cut_graphics(coins['sprite_sheet_path'])
        for i in range(len(self.sprites)):
            self.sprites[i] = pygame.transform.scale(self.sprites[i],(8,8))
        self.position=pygame.math.Vector2(x,y)
        self.surface=level.display_surface

        self.animation=coins["animation_idle"]
        self.frame_index = 0
        self.frame_time = 0

    def draw(self, dt):
    # reminder that dt has already been multiplied by 0.1, therefore we multiply by 0.01 to get seconds
        self.frame_time += dt * 0.01
        if self.frame_time >= 1 / self.animation['fps']:
            self.frame_time = 0
            self.frame_index += 1
            if self.frame_index > len(self.animation['frames']) - 1:
                self.frame_index = 0

        sprite = self.sprites[self.animation['frames'][self.frame_index]]

        self.surface.blit(sprite, (self.position.x+4, self.position.y+4))