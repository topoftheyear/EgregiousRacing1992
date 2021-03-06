import sys

import pygame
import pygame.gfxdraw

from common.button import Button
from common.enums import Screens
from common.game_manager import GameManager
from common.settings import Settings
from common.screens.screen import Screen
from version import version


class MainMenuScreen(Screen):
    def __init__(self):
        super().__init__()
        self.settings = Settings()
        self.gm = GameManager()
        self.selected = 0
        self.selections = [
            'Arcade Mode',
            'Leaderboard',
            'Settings',
            'Quit'
        ]
        self.buttons = list()

        self.max_loading = 1

    def load(self):
        # Create rects as buttons
        for x in range(len(self.selections)):
            selection = self.selections[x]
            button_width = self.settings.internal_res_x
            button_height = 7
            spacing = 2
            center_w_offset = self.settings.internal_res_x / 2 - button_width / 2

            temp = Button(
                center_w_offset,
                x * button_height + x * spacing + 2 * self.settings.internal_res_y / 3,
                button_width,
                button_height,
                selection,
                (4, 132, 209),
                (255, 255, 255),
            )
            self.buttons.append(temp)

        self.current_loading += 1

        self.loaded = True

    def unload(self):
        super().unload()

        self.selected = 0
        self.buttons = list()

    def update(self, events):
        self.gm.reset_game()

        # Check keys
        for event in events:
            if event.type == pygame.QUIT:
                pygame.display.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.display.quit()
                    sys.exit()
                if event.key == self.settings.accelerate:
                    self.selected -= 1
                if event.key == self.settings.decelerate:
                    self.selected += 1
                if event.key == self.settings.handbrake:
                    self.handle_selection()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.handle_selection()

        self.selected %= len(self.selections)

        mouse_pos = pygame.mouse.get_pos()
        mouse_pos = (mouse_pos[0] / self.settings.res_width_ratio, mouse_pos[1] / self.settings.res_height_ratio)
        for x in range(len(self.buttons)):
            button = self.buttons[x]
            if button.rect.collidepoint(mouse_pos):
                self.selected = x

    def render(self, surface):
        surface.fill((0, 0, 0))

        # Render title text
        text_surf = self.gm.big_font.render('Egregious Racing 1992', False, (229, 59, 68))
        surface.blit(text_surf, (self.settings.internal_res_x / 2 - 116, 40))

        # Render buttons
        for button in self.buttons:
            button.render(surface)

            if button == self.buttons[self.selected]:
                pygame.gfxdraw.rectangle(surface, button.rect, (229, 59, 68))
                
        # Render version number
        text_surf = self.gm.font.render(version, False, (255, 255, 255))
        text_width = len(version) * 6
        surface.blit(text_surf, (self.settings.internal_res_x - text_width, self.settings.internal_res_y - 10))

    def handle_selection(self):
        if self.selected == 0:
            self.gm.change_screens(Screens.map_select)
        elif self.selected == 1:
            self.gm.change_screens(Screens.leaderboard)
        elif self.selected == 2:
            self.gm.change_screens(Screens.settings)
        elif self.selected == 3:
            pygame.display.quit()
            sys.exit()
