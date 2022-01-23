import enum
from settings import *


class EventHandler:

    def __init__(self, game_instance):
        self.game = game_instance

    def emit(self, event_type):
        match event_type:
            case EventTypes.LEFT_DOWN:
                self.game.player.left = True
                self.game.player.flipped = True
            case EventTypes.RIGHT_DOWN:
                self.game.player.right = True
                self.game.player.flipped = False
            case EventTypes.JUMP_DOWN:
                self.game.player.jump()
            case EventTypes.RUN_DOWN:
                self.game.player.speed_multiplier = self.game.player.RUNNING_SPEED
                
            case EventTypes.LEFT_UP:
                self.game.player.left = False
            case EventTypes.RIGHT_UP:
                self.game.player.right = False
            case EventTypes.JUMP_UP:
                if self.game.player.jumping:
                    self.game.player.velocity.y *= 0.5
            case EventTypes.RUN_UP:
                self.game.player.speed_multiplier = self.game.player.DEFAULT_SPEED

            case EventTypes.DEBUG_RESET:
                self.game.player.position.x = tile_size * horizontal_tile_number / 2
                self.game.player.position.y = tile_size * vertical_tile_number / 2 - tile_size
            case EventTypes.FULLSCREEN:
                self.game.toggle_fullscreen()
                self.game.fix_screen_after_resize()
            case EventTypes.RESIZE:
                self.game.fix_screen_after_resize()
            case EventTypes.QUIT:
                self.game.is_running = False


class EventTypes(enum.Enum):
    QUIT = -1
    NONE = 0

    LEFT_DOWN = 1
    RIGHT_DOWN = 2
    JUMP_DOWN = 3
    RUN_DOWN = 4

    LEFT_UP = 5
    RIGHT_UP = 6
    JUMP_UP = 7
    RUN_UP = 8

    DEBUG_RESET = 9
    FULLSCREEN = 10
    RESIZE = 11

