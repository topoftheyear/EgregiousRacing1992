import sys

import pygame
import pygame.gfxdraw

from common.button import Button
from common.settings import Settings
from common.screens.screen import Screen


class MainMenuScreen(Screen):
    def __init__(self):
        super().__init__()
        self.settings = Settings()
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
                    # user selected their selection
                    pass
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    # user selected their selection
                    pass

        self.selected %= len(self.selections)

    def render(self, surface):
        # Render buttons
        for button in self.buttons:
            button.render(surface)

            if button == self.buttons[self.selected]:
                pygame.gfxdraw.rectangle(surface, button.rect, (229, 59, 68))
