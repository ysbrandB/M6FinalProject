import sys
import pygame

from game_data import level_0
from level import Level
from settings import *

# M4 Final programming project Max Liebe and Ysbrand Burgstede
# A mashup of pacman and mario. The goal is to collect all the coins without being hit by a ghost!
# Control with WASD or 'SPACE'ASD, fullscreen mode accessible by f11 

pygame.init()

# make the screen and save the dimensions of your screen for fullscreen mode and resizing
game_screen_ratio = game_screen_width / game_screen_height
infoObject = pygame.display.Info()
screen = pygame.display.set_mode((1.5 * 432, 1.5 * 480), pygame.RESIZABLE)
fullscreen = False
game_screen = pygame.Surface((game_screen_width, game_screen_height))

resized_width = screen.get_height() * game_screen_ratio
resized_height = screen.get_height()
resized_x_offset = (screen.get_width() - resized_width) / 2
resized_y_offset = 0

# initialize the game and all its necessary components
clock = pygame.time.Clock()

level = Level(level_0, game_screen)
player = level.player
ghosts = level.ghosts
intro = pygame.mixer.Sound('../sfx/intro.wav')
intro.play()

# our gameloop
while 1:
    dt = min(clock.tick(target_fps) * 0.1, max_delta_time)
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            match event.key:
                # player movement
                case pygame.K_a:
                    player.left = True
                    player.flipped = True
                case pygame.K_d:
                    player.right = True
                    player.flipped = False
                case pygame.K_SPACE:
                    player.jump()
                case pygame.K_w:
                    player.jump()
                case pygame.K_LSHIFT:
                    player.speed_multiplier = player.RUNNING_SPEED
                case pygame.K_e:
                    player.position.x = tile_size * horizontal_tile_number / 2
                    player.position.y = tile_size * vertical_tile_number / 2 - tile_size
                # fullscreen
                case pygame.K_F11:
                    if fullscreen:
                        pygame.display.set_mode((1.5 * 432, 1.5 * 480), pygame.RESIZABLE)
                        screen = pygame.display.set_mode((1.5 * 432, 1.5 * 480),
                                                         pygame.RESIZABLE)
                        fullscreen = False
                    else:
                        fullscreen = True
                        screen = pygame.display.set_mode((infoObject.current_w, infoObject.current_h), pygame.FULLSCREEN)
                        # pygame.display.set_mode((infoObject.current_w, infoObject.current_h), pygame.FULLSCREEN)
                    # calculate the offsets our gamescreen needs inside the real screen (seen as black bars)
                    resized_width = screen.get_height() * (game_screen_width / game_screen_height)
                    resized_height = screen.get_height()
                    resized_y_offset = 0
                    if resized_width > screen.get_width():
                        resized_width = screen.get_width()
                        resized_height = resized_width / game_screen_ratio
                        resized_y_offset = (screen.get_height() - resized_height) / 2
                    resized_x_offset = (screen.get_width() - resized_width) / 2

        elif event.type == pygame.KEYUP:
            # more player movement
            match event.key:
                case pygame.K_a:
                    player.left = False
                case pygame.K_d:
                    player.right = False
                case pygame.K_SPACE:
                    if player.jumping:
                        player.velocity.y *= 0.5
                case pygame.K_LSHIFT:
                    player.speed_multiplier = player.DEFAULT_SPEED

        elif event.type == pygame.VIDEORESIZE:
            # calculate the offsets our gamescreen needs inside the real screen (seen as black bars)
            resized_width = screen.get_height() * (game_screen_width / game_screen_height)
            resized_height = screen.get_height()
            resized_y_offset = 0
            if resized_width > screen.get_width():
                resized_width = screen.get_width()
                resized_height = resized_width / game_screen_ratio
                resized_y_offset = (screen.get_height() - resized_height) / 2
            resized_x_offset = (screen.get_width() - resized_width) / 2

    # update the level
    level.run(dt)
    # resize the game screen and put it onto the screen and update it
    resized_screen = pygame.transform.scale(game_screen, (resized_width, resized_height))
    screen.blit(resized_screen, (resized_x_offset, resized_y_offset))
    pygame.display.update()
