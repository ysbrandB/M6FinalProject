from tiles import StaticTile
import pygame
import copy


class PipeHead(StaticTile):
    def __init__(self, size, grid_position, image, flags):
        super().__init__(size, grid_position, image, flags)
        self.paired_pipe = None

    def set_paired_pipe(self, pipe):
        self.paired_pipe = pipe

    def get_paired_location(self):
        return copy.copy(self.paired_pipe.position)

    def draw_debug(self, surface):
        square = pygame.Rect(self.position, (self.size[0], self.size[1]))
        pygame.draw.rect(surface, (255, 0, 0, 100), square)
