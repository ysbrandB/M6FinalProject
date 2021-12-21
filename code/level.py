import pygame
from tiles import Tile, StaticTile
from helpers import *
from settings import tile_size

class Level:
    def __init__(self, level_data, surface):
        self.display_surface=surface

        terrain_layout=import_csv_layout(level_data['terrain'])
        self.terrain_sprites=self.create_tile_group(terrain_layout, 'terrain')

    def create_tile_group(self, layout, type):
        sprite_group=pygame.sprite.Group()
        for row_index, row in enumerate(layout):
            for column_index, value in enumerate(row):
                if value!='-1':
                    x= column_index*tile_size
                    y=row_index*tile_size
                if type=='terrain' or type=='scenery':
                    terrain_tile_list=import_cut_graphics('../imgs/terrain/mario_terrain.png')
                    if(int(value)<len(terrain_tile_list)):
                        tile_surface=terrain_tile_list[int(value)]
                        sprite=StaticTile(tile_size, x, y, tile_surface)
                        sprite_group.add(sprite)
        return sprite_group


    def run(self):
        self.terrain_sprites.draw(self.display_surface)

if(__name__=='__main__'):
    print('main')
    from game_data import level_0
    screen=pygame.display.set_mode((10,10))
    level=Level(level_0,screen)