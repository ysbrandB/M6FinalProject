from helpers import import_cut_graphics
from game_data import ghosts
import pygame
class Ghost:
    def __init__(self, x, y, level, value):
        self.x = x
        self.y =y
        self.value = value % 8
        self.sprites = import_cut_graphics(ghosts['sprite_sheet_path'])
        sprite_row_start = int(value / 7) * 8
        self.sprites = self.sprites[sprite_row_start:sprite_row_start + 8]
        self.position = pygame.Vector2(x, y)
        self.surface = level.display_surface

        self.animation = ghosts["animation_left"]
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
        self.surface.blit(sprite, (self.position.x, self.position.y))
