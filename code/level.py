import pygame
from tiles import Tile, StaticTile
from helpers import *
from settings import tile_size

class Level:
    def __init__(self, level_data, surface):
        self.display_surface=surface
        self.tile_list = import_cut_graphics('../imgs/terrain/mario_terrain.png')
        terrain_layout=import_csv_layout(level_data['terrain'])
        self.terrain_sprites=self.create_tile_group(terrain_layout, 'static')

        scenery_layout = import_csv_layout(level_data['scenery'])
        print(scenery_layout)
        self.scenery_sprites=self.create_tile_group(scenery_layout, 'scenery')


    def create_tile_group(self, layout, type):
        sprite_group=pygame.sprite.Group()
        for row_index, row in enumerate(layout):
            for column_index, value in enumerate(row):
                value=int(value)
                if value!=-1:
                    x= column_index*tile_size
                    y=row_index*tile_size
                    if type=='static':
                        sprite=StaticTile(tile_size, x, y, value, self.tile_list)
                        sprite_group.add(sprite)
        return sprite_group


    def run(self):

        self.scenery_sprites.draw(self.display_surface)
        print(self.scenery_sprites)
        self.terrain_sprites.draw(self.display_surface)

if(__name__=='__main__'):
    print('main')
    from game_data import level_0
    screen=pygame.display.set_mode((10,10))
    level=Level(level_0,screen)