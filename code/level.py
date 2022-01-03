import pygame
from tiles import StaticTile
from helpers import *
from settings import tile_size, vertical_tile_number, horizontal_tile_number
from player import Player
from ghost import Ghost
from coin import Coin
from empty_path_element import Empty_element

class Level:
    def __init__(self, level_data, surface):
        self.display_surface = surface
        self.tile_list = import_cut_graphics('../imgs/terrain/mario_terrain.png')
        self.static_sprites = dict()
        self.font = pygame.font.SysFont(None, 24)
        self.coins = []
        self.ghosts = []
        self.empty_squares = set()

        for layer in level_data:
            layer_dict = level_data[layer]
            layer_layout = import_csv_layout(layer_dict['path'])
            layer_type = layer_dict['type']
            if layer_type == 'static':
                self.static_sprites[layer] = self.create_tile_group(layer_layout)
            else:
                self.parse_other(layer_layout, layer_type)
        self.total_coins = len(self.coins)

    def create_tile_group(self, layout):
        sprite_group = pygame.sprite.Group()
        for row_index, row in enumerate(layout):
            for column_index, value in enumerate(row):
                value = int(value)
                if value != -1:
                    x = column_index * tile_size
                    y = row_index * tile_size
                    sprite = StaticTile(tile_size, x, y, value, self.tile_list)
                    sprite_group.add(sprite)
                else:
                    self.empty_squares.add(Empty_element(pygame.math.Vector2(row_index,column_index)))
        return sprite_group

    def parse_other(self, layout, _type):
        for row_index, row in enumerate(layout):
            for column_index, value in enumerate(row):
                value = int(value)
                if value != -1:
                    x = column_index * tile_size
                    y = row_index * tile_size
                    if _type == 'player':
                        self.player = Player(x, y, self)
                    elif _type == 'ghosts':
                        self.ghosts.append(Ghost(x, y, self, value, self.empty_squares))
                    elif _type == 'coin':
                        self.coins.append(Coin(x, y, self))

    def run(self, dt):
        for sprite_group in self.static_sprites:
            self.static_sprites[sprite_group].draw(self.display_surface)
        if self.player:
            self.player.live(dt, self.static_sprites, self.coins)
        if self.ghosts:
            for ghost in self.ghosts:
                ghost.update(dt)
        if self.coins:
            for coin in self.coins:
                coin.draw(dt)
        if self.player:
            img = self.font.render(f"{self.player.collected_coins}/{self.total_coins}", True, (255, 255, 255))
            self.display_surface.blit(img, (self.display_surface.get_width() - 7 * tile_size, self.display_surface.get_height() - tile_size))

