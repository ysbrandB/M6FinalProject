import pygame
from helpers import import_cut_graphics
from game_data import ui as ui_data

class UI:

    def __init__(self, ):
        self.font = pygame.font.Font("../fonts/PressStart2P-vaV7.ttf", 16)
        self.font_big = pygame.font.Font("../fonts/PressStart2P-vaV7.ttf", 32)
        self.ui_images = import_cut_graphics(ui_data['sprite_sheet_path'])

    def draw(self, level, screen, ui_width):
        # first clear the previous ui
        screen.blit(pygame.Surface((ui_width, screen.get_height())), (0, 0))
        
        heart_image = self.ui_images[0]
        screen.blit(heart_image, (0, 0))
        ui_font = self.font if (screen.get_height() < 900 and screen.get_width() < 1100) else self.font_big
        score_text = ui_font.render(f"SCORE {level.player.collected_coins * 50}", True, (255, 255, 255))
        score_text_rect = score_text.get_rect(center=(ui_width / 2, screen.get_height() / 2))
        screen.blit(score_text, score_text_rect)
