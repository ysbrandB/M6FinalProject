import pygame
from helpers import import_cut_graphics

class Tile(pygame.sprite.Sprite):
    def __init__(self, size, x, y):
        super().__init__()
        self.image=pygame.Surface((size, size))
        self.rect=self.image.get_rect(topleft=(x,y))

    def update(self, shift):
        self.rect.x+=shift
class StaticTile(Tile):
    def __init__(self, size, x, y, id, tile_list):
        super().__init__(size, x, y)
        # not rotated
        if id<len(tile_list):
            self.image=tile_list[id]

        else:
            print(id)
        # # rotated 180
        # elif(id>3221225470):
        #     id -= 3221225472
        #     self.image = tile_list[id]
        #     self.image = pygame.transform.rotate(self.image, 180)
        # #  rotated 90
        # elif(id>2684354560):
        #     id-=2684354560
        #     self.image = tile_list[id]
        #     self.image = pygame.transform.rotate(self.image, 90)
        # # rotated 270:
        # elif(id>1610612736):
        #     id-=1610612736
        #     self.image = tile_list[id]
        #     self.image = pygame.transform.rotate(self.image, 270)