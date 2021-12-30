import pygame
from helpers import import_cut_graphics


class Tile(pygame.sprite.Sprite):
    def __init__(self, size, x, y):
        super().__init__()
        self.image = pygame.Surface((size, size))
        self.rect = self.image.get_rect(topleft=(x, y))

    def update(self, shift):
        self.rect.x += shift


class StaticTile(Tile):
    def __init__(self, size, x, y, tile_id, tile_list):
        super().__init__(size, x, y)

        # get flipping/rotation flags
        flags = tile_id >> 28

        # remove the flag bits
        raw_tile_id = tile_id & 0x0fffffff
        self.image = tile_list[raw_tile_id]

        # flips and rotations
        flip_horizontal = bool(flags & 0b1000)
        flip_vertical = bool(flags & 0b0100)
        rotate = bool(flags & 0b0010)
        self.image = pygame.transform.rotate(self.image, -90 * rotate)
        self.image = pygame.transform.flip(self.image, flip_horizontal != rotate, flip_vertical)
