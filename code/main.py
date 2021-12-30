import pygame
import sys

from game_data import level_0
from level import Level
from settings import *

pygame.init()

screen = pygame.display.set_mode((screen_width, screen_height))
clock = pygame.time.Clock()

level = Level(level_0, screen)
player = level.player
intro = pygame.mixer.Sound('../sfx/intro.wav')
intro.play()

target_fps = 165

while 1:
    dt = clock.tick(target_fps) * 0.1
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
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
                case pygame.K_LSHIFT:
                    player.speed_multiplier = 1.5
        elif event.type == pygame.KEYUP:
            match event.key:
                case pygame.K_a:
                    player.left = False
                case pygame.K_d:
                    player.right = False
                case pygame.K_SPACE:
                    if player.jumping:
                        player.velocity.y *= 0.5
                        player.jumping = False
                case pygame.K_LSHIFT:
                    player.speed_multiplier = 1.0
    screen.fill('BLACK')
    level.run(dt)
    pygame.display.update()
