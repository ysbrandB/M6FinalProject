import sys

import pygame

from game_data import level_0
from level import Level
from settings import *
pygame.init()

game_screen_ratio = game_screen_width / game_screen_height
infoObject = pygame.display.Info()

screen = pygame.display.set_mode((1.5*432, 1.5*480), pygame.RESIZABLE)
game_screen = pygame.Surface((game_screen_width, game_screen_height))
clock = pygame.time.Clock()

resized_width = screen.get_height() * game_screen_ratio
resized_height = screen.get_height()
resized_x_offset = (screen.get_width() - resized_width) / 2
resized_y_offset = 0

level = Level(level_0, game_screen)
player = level.player
ghosts = level.ghosts
intro = pygame.mixer.Sound('../sfx/intro.wav')
intro.play()

while 1:
    dt = clock.tick(target_fps) * 0.1
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            match event.key:
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

        elif event.type == pygame.KEYUP:
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
            resized_width = screen.get_height() * (game_screen_width / game_screen_height)
            resized_height = screen.get_height()
            resized_y_offset = 0
            if resized_width > screen.get_width():
                resized_width = screen.get_width()
                resized_height = resized_width / game_screen_ratio
                resized_y_offset = (screen.get_height() - resized_height) / 2
            resized_x_offset = (screen.get_width() - resized_width) / 2
    game_screen.fill(pygame.Color("#9494FF"))
    level.run(dt)
    resized_screen = pygame.transform.scale(game_screen, (resized_width, resized_height))
    screen.blit(resized_screen, (resized_x_offset, resized_y_offset))
    pygame.display.update()
