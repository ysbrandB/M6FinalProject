from tiles import *
from helpers import *
from settings import tile_size
from player import Player
from ghosts.pinky import Pinky
from ghosts.inky import Inky
from ghosts.blinky import Blinky
from ghosts.clyde import Clyde
from coin import Coin
from questionblock import QuestionBlock
from pipe_head import PipeHead
from game_data import player as player_data, ghosts as ghosts_data, coins as coins_data, \
    question_block as question_block_data, pipe_head as pipe_head_data


class Level:
    def __init__(self, level_data, surface):
        self.display_surface = surface
        self.level_data = level_data
        self.images = self.get_parsed_images()
        self.tiles = dict()
        self.tiles['ghosts'] = []
        self.tiles['coins'] = []
        self.tiles['question_blocks'] = []
        self.tiles['pipe_heads'] = []
        self.font = pygame.font.SysFont(None, 24)
        self.ghost_timer = 0
        self.ghost_chase = True
        self.ghost_scared = False
        layers = level_data['layers']
        for layer in layers:
            layer_dict = layers[layer]
            layer_layout = import_csv_layout(layer_dict['path'])
            layer_type = layer_dict['type']
            layer_tiles = []
            tile_num = 0
            for row_index, row in enumerate(layer_layout):
                for column_index, value in enumerate(row):
                    tile_id = int(value)
                    if tile_id != -1:
                        grid_position = pygame.Vector2(column_index, row_index)
                        layer_tiles.append(self.create_tile(layer_type, grid_position, tile_id, tile_num))
                        tile_num += 1
            self.tiles[layer] = layer_tiles
        self.total_coins = len(self.tiles['coins'])
        self.player = self.tiles['player'][0]
        self.ghosts = self.tiles['ghosts']
        self.coins = self.tiles['coins']
        self.pipe_heads = self.tiles['pipe_heads']
        self.question_blocks = self.tiles['question_blocks']
        self.passages = self.tiles['ghost_passage']

        for tile in self.passages:
            tile.find_neighbours(self.passages)

    def create_tile(self, _type, position, tile_id, tile_num):
        match _type:
            case 'static':
                image, flags = self.extract_image_and_flags(tile_id)
                return StaticTile((tile_size, tile_size), position, image, flags)
            case 'passage':
                return PassageTile((tile_size, tile_size), position)
            case 'player':
                frames = self.images['player']
                return Player((tile_size, tile_size), position, frames, player_data)
            case 'ghosts':
                frames = self.images['ghosts']
                match (tile_num % 4):
                    case 0:
                        return Blinky((tile_size, tile_size), position, frames, ghosts_data, tile_num)
                    case 1:
                        return Pinky((tile_size, tile_size), position, frames, ghosts_data, tile_num)
                    case 2:
                        return Inky((tile_size, tile_size), position, frames, ghosts_data, tile_num)
                    case 3:
                        return Clyde((tile_size, tile_size), position, frames, ghosts_data, tile_num)
            case 'coin':
                frames = self.images['coins']
                return Coin((tile_size/2, tile_size/2), position, frames, coins_data)
            case 'question_block':
                frames = self.images['question_blocks']
                return QuestionBlock((tile_size, tile_size), position, frames, question_block_data, self.ghost_scared)
            case 'pipe_head':
                image = self.images['pipe_heads'][0]
                return PipeHead((tile_size*2, tile_size), position, image, tile_id >> 28)

        return _type

    def extract_image_and_flags(self, tile_id):
        return self.images['level'][tile_id & 0x0fffffff], tile_id >> 28

    def get_parsed_images(self):
        images = dict()
        images['level'] = import_cut_graphics(self.level_data['tiles_sheet_path'], self.level_data['sprite_size'])
        images['player'] = import_cut_graphics(player_data['sprite_sheet_path'], player_data['sprite_size'])
        images['ghosts'] = import_cut_graphics(ghosts_data['sprite_sheet_path'], ghosts_data['sprite_size'])
        images['coins'] = import_cut_graphics(coins_data['sprite_sheet_path'], coins_data['sprite_size'])
        images['question_blocks'] = import_cut_graphics(question_block_data['sprite_sheet_path'],
                                                        question_block_data['sprite_size'])
        images['pipe_heads'] = import_cut_graphics(pipe_head_data['sprite_sheet_path'], pipe_head_data['sprite_size'])
        return images

    def run(self, dt):
        self.display_surface.fill(pygame.Color("#9494FF"))
        for tile_group in self.tiles:
            for tile in self.tiles[tile_group]:
                if tile.drawable and tile.static:
                    tile.draw(self.display_surface)
        self.player.live(dt, self.display_surface, self.tiles)

        if self.ghost_timer <= 0:
            if self.ghost_chase:
                self.ghost_timer = ghosts_data['seconds_spreading']
                self.ghost_chase = False
            else:
                self.ghost_timer = ghosts_data['seconds_following']
                self.ghost_chase = True
        else:
            self.ghost_timer -= dt / 100

        for ghost in self.ghosts:
            ghost.live(dt, self.display_surface, self.player, self.passages, self.ghosts, self.ghost_chase,
                       self.ghost_scared)

        for coin in self.coins:
            coin.live(dt, self.display_surface)

        for question_block in self.question_blocks:
            question_block.live(dt, self.display_surface)

        txt = self.font.render(f"{self.player.collected_coins}/{self.total_coins}", True, (255, 255, 255))
        self.display_surface.blit(txt, (
            self.display_surface.get_width() - 7 * tile_size, self.display_surface.get_height() - tile_size))
