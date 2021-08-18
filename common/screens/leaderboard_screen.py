import sys

import pygame
import pygame.gfxdraw

from common.button import Button
from common.enums import Screens
from common.game_manager import GameManager
from common.leaderboard import Leaderboard
from common.settings import Settings
from common.screens.screen import Screen
from utils.helpers import get_list_of_maps


class LeaderboardScreen(Screen):
    def __init__(self):
        super().__init__()
        self.settings = Settings()
        self.gm = GameManager()
        self.leaderboard = Leaderboard()
        self.buttons = list()
        self.selected_button = 0

        self.map_images = dict()
        self.current_map = 0

        self.max_loading = 2

    def load(self):
        # Create images for each leaderboard
        for file, name in zip(get_list_of_maps(), get_list_of_maps(False)):
            image = pygame.image.load(f'img/{file}').convert_alpha()
            scaled_image = pygame.transform.scale(image, (self.settings.internal_res_y, self.settings.internal_res_y))
            self.map_images[name] = scaled_image

        self.current_loading += 1

        # Create buttons
        button_width = 12
        button_height = 7
        left_button = Button(
            10,
            self.settings.internal_res_y / 2 - (button_height / 2),
            button_width,
            button_height,
            '<',
            (4, 132, 209),
            (255, 255, 255)
        )

        back_button = Button(
            0,
            self.settings.internal_res_y - (button_height * 2),
            self.settings.internal_res_x,
            button_height,
            'Back',
            (4, 132, 209),
            (255, 255, 255),
        )

        right_button = Button(
            self.settings.internal_res_x - button_width - 10,
            self.settings.internal_res_y / 2 - (button_height / 2),
            button_width,
            button_height,
            ' >',
            (4, 132, 209),
            (255, 255, 255)
        )

        self.buttons.append(left_button)
        self.buttons.append(back_button)
        self.buttons.append(right_button)

        self.current_loading += 1

        self.loaded = True

    def unload(self):
        super().unload()

        self.selected_button = 0
        self.current_map = 0
        self.buttons = list()

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
                if event.key == self.settings.rotate_left:
                    self.selected_button -= 1
                if event.key == self.settings.rotate_right:
                    self.selected_button += 1
                if event.key == self.settings.handbrake:
                    self.handle_selection()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.handle_selection()

        self.selected_button %= 3

        mouse_pos = pygame.mouse.get_pos()
        mouse_pos = (mouse_pos[0] / self.settings.res_width_ratio, mouse_pos[1] / self.settings.res_height_ratio)
        for x in range(len(self.buttons)):
            button = self.buttons[x]
            if button.rect.collidepoint(mouse_pos):
                self.selected_button = x

    def render(self, surface):
        surface.fill((0, 0, 0))

        # Draw the map
        map_img = self.map_images[list(self.map_images.keys())[self.current_map]]
        surface.blit(
            map_img,
            [self.settings.internal_res_x / 2 - map_img.get_width() / 2, 0]
        )

        # Draw black rectangle over map
        pygame.gfxdraw.box(
            surface,
            [self.settings.internal_res_x / 2 - map_img.get_width() / 2, 0, map_img.get_width(), map_img.get_height()],
            (0, 0, 0, 63 + 128)
        )

        # Draw the leaderboard text
        text_surf = self.gm.font.render('Leaderboard', False, (255, 255, 255))
        surface.blit(text_surf, (self.settings.internal_res_x / 2 - 33, 20))

        map_name = list(self.map_images.keys())[self.current_map]
        text_surf = self.gm.font.render(map_name, False, (255, 255, 255))
        text_length = len(map_name) * 6
        surface.blit(text_surf, (self.settings.internal_res_x / 2 - text_length / 2, 40))

        # Obtain leaderboard
        entries = self.leaderboard.leaderboard[map_name]
        entries = sorted(entries, key=lambda x: x['score'])[::-1]

        # Draw entries
        for x in range(len(entries)):
            entry = entries[x]
            text = f'{x + 1}: {entry["name"]} : {entry["score"]}'
            text_surf = self.gm.font.render(text, False, (255, 255, 255))
            text_length = len(text) * 6
            surface.blit(text_surf, (self.settings.internal_res_x / 2 - text_length / 2, 60 + x * 20))

        # Draw the buttons
        for button in self.buttons:
            button.render(surface)

            if button == self.buttons[self.selected_button]:
                pygame.gfxdraw.rectangle(surface, button.rect, (229, 59, 68))

    def handle_selection(self):
        if self.selected_button == 0:
            self.current_map -= 1
        elif self.selected_button == 1:
            self.gm.change_screens(Screens.main_menu)
        elif self.selected_button == 2:
            self.current_map += 1

        self.current_map %= len(self.map_images.keys())
