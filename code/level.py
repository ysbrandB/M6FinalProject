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
import copy


class Level:
    def __init__(self, level_data, surface):
        self.display_surface = surface
        self.level_data = level_data
        self.images = self.get_parsed_images()
        self.tiles = dict()
        self.tiles['ghosts'] = []
        self.tiles['coins'] = []
        self.tiles['question_blocks'] = []
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
        self.player = self.tiles['player'][0]
        self.player_start = copy.deepcopy(self.player.position)
        self.ghosts = self.tiles['ghosts'].copy()
        self.coins = self.tiles['coins'].copy()
        self.question_blocks = self.tiles['question_blocks'].copy()
        self.passages = self.tiles['ghost_passage']

        self.total_coins = len(self.coins)

        self.reset_countdown = 500
        self.reset_timer = 0

        self.intro_snd = pygame.mixer.Sound('../sfx/intro.wav')
        self.congratulations_snd = pygame.mixer.Sound('../sfx/wedidit.wav')
        self.intro_snd.play()

        self.RUNNING = 0
        self.SOFT_RESET = 1
        self.FULL_RESET = 2
        self.WE_WON = 3
        self.state = self.RUNNING

        for tile in self.passages:
            tile.find_neighbours(self.passages)

    # put the pipes in the pipe array and pair the pipe_blocks with the pipe_block in the same layer of the same type
        self.pipes = []
        for layer in self.tiles:
            if "pipe_head_pair" in layer:
                self.pipes.extend(self.tiles[layer])
                for pipe in self.tiles[layer]:
                    for possible_pair in self.tiles[layer]:
                        if possible_pair != pipe:
                            if possible_pair.tile_id == pipe.tile_id and possible_pair.paired_pipe is None and pipe.paired_pipe is None:
                                possible_pair.paired_pipe = pipe
                                pipe.paired_pipe = possible_pair
                                break

    def create_tile(self, _type, position, tile_id, tile_num):
        match _type:
            case 'static':
                image, flags = self.extract_image_and_flags(tile_id)
                return StaticTile(tile_size, position, image, flags)
            case 'passage':
                return PassageTile(tile_size, position)
            case 'player':
                frames = self.images['player']
                return Player(tile_size, position, frames, player_data)
            case 'ghosts':
                frames = self.images['ghosts']
                match (tile_num % 4):
                    case 0:
                        return Blinky(tile_size, position, frames, ghosts_data, tile_num)
                    case 1:
                        return Pinky(tile_size, position, frames, ghosts_data, tile_num)
                    case 2:
                        return Inky(tile_size, position, frames, ghosts_data, tile_num)
                    case 3:
                        return Clyde(tile_size, position, frames, ghosts_data, tile_num)
            case 'coin':
                frames = self.images['coins']
                return Coin(tile_size / 2, position, frames, coins_data)
            case 'question_block':
                frames = self.images['question_blocks']
                return QuestionBlock(tile_size, position, frames, question_block_data, self.ghost_scared)
            case 'pipe_head':
                image, flag = self.extract_image_and_flags(tile_id)
                return PipeHead(tile_size, position, image, flag, tile_id & 0x0fffffff)

        return _type

    def extract_image_and_flags(self, tile_id):
        return self.images['level'][tile_id & 0x0fffffff], tile_id >> 28

    def get_parsed_images(self):
        images = dict()
        images['level'] = import_cut_graphics(self.level_data['tiles_sheet_path'])
        images['player'] = import_cut_graphics(player_data['sprite_sheet_path'])
        images['ghosts'] = import_cut_graphics(ghosts_data['sprite_sheet_path'])
        images['coins'] = import_cut_graphics(coins_data['sprite_sheet_path'])
        images['question_blocks'] = import_cut_graphics(question_block_data['sprite_sheet_path'])
        images['pipe_heads'] = import_cut_graphics(pipe_head_data['sprite_sheet_path'])
        return images

    def run(self, dt):
        self.display_surface.fill(pygame.Color("#9494FF"))
        for tile_group in self.tiles:
            for tile in self.tiles[tile_group]:
                if tile.drawable and tile.static:
                    tile.draw(self.display_surface)
        if self.player.collected_coins >= self.total_coins and not self.player.frozen:
            self.player.frozen = True
            self.player.lives = 0
            self.congratulations_snd.play()
        if self.player.frozen:
            if self.player.lives > 0:
                self.state = self.SOFT_RESET
            elif self.player.collected_coins >= self.total_coins:
                self.state = self.WE_WON
            else:
                self.state = self.FULL_RESET
            self.do_reset_countdown(dt)
            if self.state == self.WE_WON:
                return
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

        for ghost in self.tiles['ghosts']:
            ghost.live(dt, self.display_surface, self.player, self.passages, self.tiles['ghosts'], self.ghost_chase)

        for coin in self.tiles['coins']:
            coin.live(dt, self.display_surface)

        for question_block in self.tiles['question_blocks']:
            question_block.live(dt, self.display_surface)

    def reset(self):
        self.player.position = copy.copy(self.player_start)
        self.tiles['ghosts'] = copy.copy(self.ghosts)
        self.player.frozen = False
        self.intro_snd.play()
        self.state = self.RUNNING

    def do_reset_countdown(self, dt):
        if not self.reset_timer >= self.reset_countdown:
            self.reset_timer += dt
        else:
            self.reset_timer = 0
            self.reset() if self.player.lives > 0 else self.game_over()

    def game_over(self):
        self.reset()
        self.tiles['coins'] = copy.copy(self.coins)
        # fix frame indices not lining up
        for coin in self.tiles['coins']:
            coin.frame_index = 0
        self.tiles['question_blocks'] = copy.copy(self.question_blocks)
        self.player.lives = 3
        self.player.collected_coins = 0
