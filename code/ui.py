import pygame
from helpers import import_cut_graphics
from game_data import ui as ui_data


class UI:

    def __init__(self, ):
        self.font = pygame.font.Font("../fonts/PressStart2P-vaV7.ttf", 16)
        self.font_big = pygame.font.Font("../fonts/PressStart2P-vaV7.ttf", 32)
        self.ui_images = import_cut_graphics(ui_data['sprite_sheet_path'])

    def draw(self, level, screen, ui_width, trailing_space):
        # first clear the previous ui
        screen.blit(pygame.Surface((ui_width, screen.get_height())), (0, 0))

        if level.player.lives > 0:
            heart_scale = 64 if is_big_screen(screen) else 32
            heart_image = pygame.transform.scale(self.ui_images[0], (heart_scale, heart_scale))
            heart_surface = pygame.Surface((level.player.lives * (heart_scale + 6) - 6, heart_scale))
            for i in range(level.player.lives):
                heart_surface.blit(heart_image, (i * (heart_scale + 6), 0))
            heart_rect = heart_surface.get_rect(center=(ui_width / 2, screen.get_height() / 2 + heart_scale))
            screen.blit(heart_surface, heart_rect)

        ui_font = self.font_big if is_big_screen(screen) else self.font
        score_text = ui_font.render(f"SCORE {level.player.collected_coins * 50}", True, (255, 255, 255))
        score_text_rect = score_text.get_rect(center=(ui_width / 2, screen.get_height() / 2))
        screen.blit(score_text, score_text_rect)

        state_text = ""
        match level.state:
            case level.RUNNING:
                # fix trailing text on right side of screen
                if trailing_space > 0:
                    screen.blit(pygame.Surface((trailing_space, screen.get_height())),
                                     (screen.get_width() - trailing_space, 0))
                return
            case level.SOFT_RESET:
                if level.player.lives > 1:
                    state_text = f"YOU HAVE DIED! YOU STILL HAVE {level.player.lives} LIVES LEFT!"
                else:
                    state_text = f"YOU HAVE DIED! YOU STILL HAVE 1 LIFE LEFT!"
            case level.FULL_RESET:
                state_text = f"YOU ARE OUT OF LIVES! SCORE: {level.player.collected_coins * 50}"
            case level.WE_WON:
                state_text = "YOU WON! CONGRATULATIONS!"

        overlay_text = ui_font.render(state_text, True, (255, 255, 255))
        overlay_text_rect = overlay_text.get_rect(center=(screen.get_width() / 2, screen.get_height() / 2 - 150))
        screen.blit(pygame.Surface((overlay_text.get_width(), overlay_text.get_height())), overlay_text_rect)
        screen.blit(overlay_text, overlay_text_rect)



def is_big_screen(screen):
    return screen.get_height() > 900 and screen.get_width() > 1100
