import sys

import pygame
import pygame.gfxdraw

from common.button import Button
from common.enums import Screens
from common.game_manager import GameManager
from common.settings import Settings
from common.screens.screen import Screen


class MainMenuScreen(Screen):
    def __init__(self):
        super().__init__()
        self.settings = Settings()
        self.gm = GameManager()
        self.selected = 0
        self.selections = [
            'Arcade Mode',
            'Leaderboards',
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

    def update(self, events):
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
        # Render buttons
        for button in self.buttons:
            button.render(surface)

            if button == self.buttons[self.selected]:
                pygame.gfxdraw.rectangle(surface, button.rect, (229, 59, 68))

    def handle_selection(self):
        if self.selected == 0:
            self.gm.current_screen = Screens.game
        elif self.selected == 1:
            self.gm.current_screen = None
        elif self.selected == 2:
            self.gm.current_screen = None
        elif self.selected == 3:
            pygame.display.quit()
            sys.exit()
