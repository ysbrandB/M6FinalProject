import pygame
from tiles import Tile, StaticTile
from helpers import *
from settings import tile_size
from player import Player
from ghost import Ghost
from coin import Coin

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
            elif layer_type == 'ghosts':
                self.ghosts = self.create_ghosts(layer_layout)
            elif layer_type == 'coin':
                self.coins = self.create_coins(layer_layout)

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

    def create_ghosts(self, layout):
        ghosts = []
        for row_index, row in enumerate(layout):
            for column_index, value in enumerate(row):
                value = int(value)
                if value != -1:
                    x = column_index * tile_size
                    y = row_index * tile_size
                    ghost = Ghost(x, y, self, value)
                    ghosts.append(ghost)
        return ghosts

    def create_coins(self, layout):
        coins = []
        for row_index, row in enumerate(layout):
            for column_index, value in enumerate(row):
                value = int(value)
                if value != -1:
                    x = column_index * tile_size
                    y = row_index * tile_size
                    coin = Coin(x, y, self)
                    coins.append(coin)
        return coins

    def run(self, dt):
        for sprite_group in self.static_sprites:
            self.static_sprites[sprite_group].draw(self.display_surface)
        if self.player:
            self.player.live(dt, self.static_sprites)
        if self.ghosts:
            for ghost in self.ghosts:
                ghost.draw(dt)
        if self.coins:
            for coin in self.coins:
                coin.draw(dt)
