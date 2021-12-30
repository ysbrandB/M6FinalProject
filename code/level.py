import pygame
from tiles import Tile, StaticTile
from helpers import *
from settings import tile_size
from player import Player


class Level:
    def __init__(self, level_data, surface):
        self.display_surface = surface
        self.tile_list = import_cut_graphics('../imgs/terrain/mario_terrain.png')
        self.static_sprites = dict()
        for layer in level_data:
            layer_dict = level_data[layer]
            layer_layout = import_csv_layout(layer_dict['path'])
            layer_type = layer_dict['type']
            if layer_type == 'static':
                self.static_sprites[layer] = self.create_tile_group(layer_layout, 'static')
            elif layer_type == 'player':
                self.player = self.create_player(layer_layout)

    def create_tile_group(self, layout, _type):
        sprite_group = pygame.sprite.Group()
        for row_index, row in enumerate(layout):
            for column_index, value in enumerate(row):
                value = int(value)
                if value != -1:
                    x = column_index * tile_size
                    y = row_index * tile_size
                    if _type == 'static':
                        sprite = StaticTile(tile_size, x, y, value, self.tile_list)
                        sprite_group.add(sprite)
        return sprite_group

    def create_player(self, layout):
        for row_index, row in enumerate(layout):
            for column_index, value in enumerate(row):
                value = int(value)
                if value != -1:
                    x = column_index * tile_size
                    y = row_index * tile_size
                    player = Player(x, y, self)
                    return player

    def run(self, dt):
        for sprite_group in self.static_sprites:
            self.static_sprites[sprite_group].draw(self.display_surface)
        if self.player:
            self.player.live(dt)
