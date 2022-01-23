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
        square = pygame.Surface((self.size[0], self.size[1]))
        square.fill((0, 255, 0))
        square.set_alpha(100)
        surface.blit(square, self.position)
