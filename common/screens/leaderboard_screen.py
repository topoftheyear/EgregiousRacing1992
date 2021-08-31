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

        self.nav_list = [
            ['map_left', 'map_right'],
            ['back'],
        ]
        self.nav_x = 0
        self.nav_y = 0

        self.buttons = dict()

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
        self.buttons['map_left'] = Button(
            10,
            self.settings.internal_res_y / 2 - (button_height / 2),
            button_width,
            button_height,
            '<',
            (4, 132, 209),
            (255, 255, 255)
        )

        self.buttons['map_right'] = Button(
            self.settings.internal_res_x - button_width - 10,
            self.settings.internal_res_y / 2 - (button_height / 2),
            button_width,
            button_height,
            ' >',
            (4, 132, 209),
            (255, 255, 255)
        )

        self.buttons['back'] = Button(
            0,
            self.settings.internal_res_y - (button_height * 2),
            self.settings.internal_res_x,
            button_height,
            'Back',
            (4, 132, 209),
            (255, 255, 255),
        )

        self.current_loading += 1

        self.loaded = True

    def unload(self):
        super().unload()

        self.nav_x = 0
        self.nav_y = 0

        self.current_map = 0
        self.buttons = dict()

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
                    self.nav_y -= 1
                if event.key == self.settings.decelerate:
                    self.nav_y += 1
                if event.key == self.settings.rotate_left:
                    self.nav_x -= 1
                if event.key == self.settings.rotate_right:
                    self.nav_x += 1
                if event.key == self.settings.handbrake:
                    self.handle_selection()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.handle_selection()

        self.nav_y %= len(self.nav_list)
        self.nav_x %= len(self.nav_list[self.nav_y])

        mouse_pos = pygame.mouse.get_pos()
        mouse_pos = (mouse_pos[0] / self.settings.res_width_ratio, mouse_pos[1] / self.settings.res_height_ratio)
        for name, button in self.buttons.items():
            if button.rect.collidepoint(mouse_pos):
                for y in range(len(self.nav_list)):
                    for x in range(len(self.nav_list[y])):
                        if self.nav_list[y][x] == name:
                            self.nav_y = y
                            self.nav_x = x

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
        text_surf = self.gm.big_font.render('Leaderboard', False, (255, 255, 255))
        surface.blit(text_surf, (self.settings.internal_res_x / 2 - 66, 15))

        map_name = list(self.map_images.keys())[self.current_map]
        text_surf = self.gm.big_font.render(map_name, False, (255, 255, 255))
        text_length = len(map_name) * 12
        surface.blit(text_surf, (self.settings.internal_res_x / 2 - text_length / 2, 35))

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
        for name, button in self.buttons.items():
            button.render(surface)

            if button == self.buttons[self.nav_list[self.nav_y][self.nav_x]]:
                pygame.gfxdraw.rectangle(surface, button.rect, (229, 59, 68))

    def handle_selection(self):
        selected = self.nav_list[self.nav_y][self.nav_x]

        if selected == 'map_left':
            self.current_map -= 1
        elif selected == 'map_right':
            self.current_map += 1
        elif selected == 'back':
            self.gm.change_screens(Screens.main_menu)

        self.current_map %= len(self.map_images.keys())
