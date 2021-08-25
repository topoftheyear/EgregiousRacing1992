import math
import sys

import pygame
import pygame.gfxdraw

from common.button import Button
from common.enums import Screens
from common.game_manager import GameManager
from common.settings import Settings
from common.screens.screen import Screen
from utils.helpers import get_list_of_maps


class MapSelectScreen(Screen):
    def __init__(self):
        super().__init__()
        self.settings = Settings()
        self.gm = GameManager()

        self.nav_list = [
            ['map_left', 'map_right'],
            ['start'],
            ['back'],
        ]
        self.nav_x = 0
        self.nav_y = 0

        self.buttons = dict()

        self.map_images = dict()
        self.current_map = 0

        self.map_rotation = 0

        self.max_loading = 2

    def load(self):
        # Create images for each leaderboard
        for file, name in zip(get_list_of_maps(), get_list_of_maps(False)):
            image = pygame.image.load(f'img/{file}').convert_alpha()
            scaled_image = pygame.transform.scale(image, (int(self.settings.internal_res_y / 2),
                                                          int(self.settings.internal_res_y / 2)))
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

        self.buttons['start'] = Button(
            0,
            self.settings.internal_res_y - (button_height * 3) - 2,
            self.settings.internal_res_x,
            button_height,
            'Start',
            (4, 132, 209),
            (255, 255, 255),
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

        self.map_rotation = 0

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

        self.map_rotation += math.pi / 64
        self.map_rotation %= 2 * math.pi

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
        temp_img = pygame.transform.rotate(map_img, 35 * math.sin(self.map_rotation))
        surface.blit(
            temp_img,
            [math.ceil(self.settings.internal_res_x / 2 - temp_img.get_width() / 2),
             math.ceil(self.settings.internal_res_y / 2 - temp_img.get_width() / 2)]
        )

        # Draw map select text
        text_surf = self.gm.font.render('Select a map:', False, (255, 255, 255))
        surface.blit(text_surf, (self.settings.internal_res_x / 2 - 39, 10))

        # Draw the map name text
        map_name = list(self.map_images.keys())[self.current_map]
        text_surf = self.gm.font.render(map_name, False, (255, 255, 255))
        text_length = len(map_name) * 6
        surface.blit(text_surf, (self.settings.internal_res_x / 2 - text_length / 2, 20))

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
        elif selected == 'start':
            self.gm.selected_map = list(self.map_images.keys())[self.current_map]
            self.gm.change_screens(Screens.game)
        elif selected == 'back':
            self.gm.change_screens(Screens.main_menu)

        self.current_map %= len(self.map_images.keys())
