import sys

import pygame
import pygame.gfxdraw

from common.button import Button
from common.enums import Screens
from common.game_manager import GameManager
from common.leaderboard import Leaderboard
from common.settings import Settings
from common.screens.screen import Screen


class GameEndScreen(Screen):
    def __init__(self):
        super().__init__()
        self.settings = Settings()
        self.gm = GameManager()
        self.leaderboard = Leaderboard()
        self.board = None
        self.selected = 0
        self.selections = [
            'Back'
        ]
        self.buttons = list()

        self.entering = False
        self.entry_name = ''

        self.max_loading = 2

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
                self.settings.internal_res_y - 20,
                button_width,
                button_height,
                selection,
                (4, 132, 209),
                (255, 255, 255),
            )
            self.buttons.append(temp)

        self.current_loading += 1

        # Get the leaderboard
        self.board = self.leaderboard.leaderboard[self.gm.selected_map]

        # Determine if score should be in the leaderboard
        for entry in self.board:
            if self.gm.score > entry['score']:
                self.entering = True

        self.current_loading += 1

        self.loaded = True

    def unload(self):
        super().unload()

        self.entering = False
        self.entry_name = ''

        self.selected = 0
        self.buttons = list()

    def update(self, events):
        # Check keys
        for event in events:
            if not self.entering:
                if event.type == pygame.QUIT:
                    pygame.display.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.display.quit()
                        sys.exit()
                    if event.key == self.settings.handbrake:
                        self.handle_selection()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.handle_selection()
            else:
                if event.type == pygame.KEYDOWN:
                    try:
                        if event.key == pygame.K_BACKSPACE:
                            self.entry_name = self.entry_name[:-1]
                        else:
                            self.entry_name += chr(event.key)
                    except ValueError:
                        print(f'{event.key} not acceptable entry')
                # Finalize leaderboard entry
                if len(self.entry_name) >= 3:
                    self.entering = False

                    self.board.append(
                        {'name': self.entry_name, 'score': self.gm.score}
                    )

                    self.board = sorted(self.board, key=lambda n: n['score'])[::-1]
                    self.board.pop()
                    self.leaderboard.leaderboard[self.gm.selected_map] = self.board
                    self.leaderboard.save()

        self.selected %= len(self.selections)

        mouse_pos = pygame.mouse.get_pos()
        mouse_pos = (mouse_pos[0] / self.settings.res_width_ratio, mouse_pos[1] / self.settings.res_height_ratio)
        for x in range(len(self.buttons)):
            button = self.buttons[x]
            if button.rect.collidepoint(mouse_pos):
                self.selected = x

    def render(self, surface):
        surface.fill((0, 0, 0))

        # Screen for taking leaderboard input
        if self.entering:
            # Draw high score text
            text_surf = self.gm.big_font.render('High Score!', False, (255, 255, 255))
            surface.blit(text_surf, (self.settings.internal_res_x / 2 - 66, 30))

            # Draw enter name text
            text_surf = self.gm.big_font.render('Enter Name:', False, (255, 255, 255))
            surface.blit(text_surf, (self.settings.internal_res_x / 2 - 66, 50))

            text = self.entry_name
            text += '-' * (3 - len(self.entry_name))
            text_length = len(text) * 12
            text_surf = self.gm.big_font.render(text, False, (255, 231, 98))
            surface.blit(text_surf, (self.settings.internal_res_x / 2 - text_length / 2, 70))

            # Draw score
            text = str(self.gm.score)
            text_length = len(text) * 12
            text_surf = self.gm.big_font.render(text, False, (255, 231, 98))
            surface.blit(text_surf, (self.settings.internal_res_x / 2 - text_length / 2, 90))

        # Screen for showing the leaderboard
        else:
            # Draw map name
            map_name = self.gm.selected_map
            text_surf = self.gm.big_font.render(map_name, False, (255, 255, 255))
            text_length = len(map_name) * 12
            surface.blit(text_surf, (self.settings.internal_res_x / 2 - text_length / 2, 35))

            # Obtain leaderboard
            entries = sorted(self.board, key=lambda x: x['score'])[::-1]
            # Draw entries
            for x in range(len(entries)):
                entry = entries[x]
                color = (255, 255, 255)
                if self.gm.score == entry['score']:
                    color = (255, 231, 98)
                text = f'{x + 1}: {entry["name"]} : {entry["score"]}'
                text_surf = self.gm.font.render(text, False, color)
                text_length = len(text) * 6
                surface.blit(text_surf, (self.settings.internal_res_x / 2 - text_length / 2, 60 + x * 20))

            # Render buttons
            for button in self.buttons:
                button.render(surface)

                if button == self.buttons[self.selected]:
                    pygame.gfxdraw.rectangle(surface, button.rect, (229, 59, 68))

    def handle_selection(self):
        self.gm.change_screens(Screens.main_menu)
