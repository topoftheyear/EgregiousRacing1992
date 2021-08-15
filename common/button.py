import pygame
import pygame.gfxdraw

from common.game_manager import GameManager


class Button:
    def __init__(self, x, y, width, height, text='', color=(255, 255, 255), text_color=(0, 0, 0)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.gm = GameManager()

    def render(self, surface):
        pygame.gfxdraw.box(
            surface,
            self.rect,
            self.color
        )

        text_surf = self.gm.font.render(self.text, False, self.text_color)
        text_width = len(self.text) * 6
        x_offset = (self.rect.width - text_width) / 2
        y_offset = (self.rect.height - 8) / 2
        surface.blit(text_surf, (self.rect.x + x_offset, self.rect.y + y_offset))
