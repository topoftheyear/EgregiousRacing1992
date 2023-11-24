import math
import sys

import pygame
import pygame.gfxdraw

from common.button import Button
from common.enums import Screens
from common.game_manager import GameManager
from common.settings import Settings
from common.screens.screen import Screen


class SettingsScreen(Screen):
    def __init__(self):
        super().__init__()
        self.settings = Settings()
        self.gm = GameManager()

        self.nav_list = [
            ['res_left', 'res_right'],
            ['mouse_left', 'mouse_right'],
            ['accelerate'],
            ['decelerate'],
            ['rotate_left'],
            ['rotate_right'],
            ['handbrake'],
            ['reset_camera'],
            ['back', 'save', 'default']
        ]
        self.nav_x = 0
        self.nav_y = 0

        self.res_list = [
            '1280x720',
            '1600x900',
            '1920x1080',
            '2560x1440'
        ]
        self.res_selector = self.res_list.index(f'{self.settings.res_x}x{self.settings.res_y}')

        self.rebinding = False
        self.rebind_selection = None

        self.buttons = dict()

        self.info_text = {
            'res_left': 'Changes window resolution',
            'res_right': 'Changes window resolution',
            'mouse_left': 'Changes mouse sensitivity',
            'mouse_right': 'Changes mouse sensitivity',
            'accelerate': 'Select to rebind',
            'decelerate': 'Select to rebind',
            'rotate_left': 'Select to rebind',
            'rotate_right': 'Select to rebind',
            'handbrake': 'Select to rebind',
            'reset_camera': 'Select to rebind',
            'back': 'Exit without saving',
            'save': 'Save changes',
            'default': 'Revert settings to default'
        }

        self.max_loading = 13

    def load(self):
        # Create some buttons
        self.buttons['res_left'] = Button(
            4 * self.settings.internal_res_x / 6,
            30,
            20,
            7,
            '<',
            (4, 132, 209),
            (255, 255, 255),
        )

        self.current_loading += 1

        self.buttons['res_right'] = Button(
            4 * self.settings.internal_res_x / 6 + 20,
            30,
            20,
            7,
            ' >',
            (4, 132, 209),
            (255, 255, 255),
        )

        self.current_loading += 1

        self.buttons['mouse_left'] = Button(
            4 * self.settings.internal_res_x / 6,
            40,
            20,
            7,
            '<',
            (4, 132, 209),
            (255, 255, 255),
        )

        self.current_loading += 1

        self.buttons['mouse_right'] = Button(
            4 * self.settings.internal_res_x / 6 + 20,
            40,
            20,
            7,
            ' >',
            (4, 132, 209),
            (255, 255, 255),
        )

        self.current_loading += 1

        self.buttons['accelerate'] = Button(
            4 * self.settings.internal_res_x / 6,
            50,
            40,
            7,
            'Rebind',
            (4, 132, 209),
            (255, 255, 255),
        )

        self.current_loading += 1

        self.buttons['decelerate'] = Button(
            4 * self.settings.internal_res_x / 6,
            60,
            40,
            7,
            'Rebind',
            (4, 132, 209),
            (255, 255, 255),
        )

        self.current_loading += 1

        self.buttons['rotate_left'] = Button(
            4 * self.settings.internal_res_x / 6,
            70,
            40,
            7,
            'Rebind',
            (4, 132, 209),
            (255, 255, 255),
        )

        self.current_loading += 1

        self.buttons['rotate_right'] = Button(
            4 * self.settings.internal_res_x / 6,
            80,
            40,
            7,
            'Rebind',
            (4, 132, 209),
            (255, 255, 255),
        )

        self.current_loading += 1

        self.buttons['handbrake'] = Button(
            4 * self.settings.internal_res_x / 6,
            90,
            40,
            7,
            'Rebind',
            (4, 132, 209),
            (255, 255, 255),
        )

        self.current_loading += 1

        self.buttons['reset_camera'] = Button(
            4 * self.settings.internal_res_x / 6,
            100,
            40,
            7,
            'Rebind',
            (4, 132, 209),
            (255, 255, 255),
        )

        self.current_loading += 1

        self.buttons['back'] = Button(
            self.settings.internal_res_x / 8,
            self.settings.internal_res_y - 14,
            self.settings.internal_res_x / 4 - 1,
            7,
            'Back',
            (4, 132, 209),
            (255, 255, 255),
        )

        self.current_loading += 1

        self.buttons['save'] = Button(
            3 * self.settings.internal_res_x / 8,
            self.settings.internal_res_y - 14,
            self.settings.internal_res_x / 4 - 1,
            7,
            'Save',
            (4, 132, 209),
            (255, 255, 255),
        )

        self.current_loading += 1

        self.buttons['default'] = Button(
            5 * self.settings.internal_res_x / 8,
            self.settings.internal_res_y - 14,
            self.settings.internal_res_x / 4 - 1,
            7,
            'Default',
            (4, 132, 209),
            (255, 255, 255),
        )

        self.current_loading += 1

        self.loaded = True

    def unload(self):
        super().unload()

        self.nav_x = 0
        self.nav_y = 0

        self.rebinding = False
        self.rebind_selection = None

        self.buttons = dict()

    def update(self, events):
        # Check keys
        for event in events:
            if not self.rebinding:
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
            else:
                if event.type == pygame.KEYDOWN:
                    selected = self.nav_list[self.nav_y][self.nav_x]
                    if selected == 'accelerate':
                        self.settings.accelerate = event.key
                    elif selected == 'decelerate':
                        self.settings.decelerate = event.key
                    elif selected == 'rotate_left':
                        self.settings.rotate_left = event.key
                    elif selected == 'rotate_right':
                        self.settings.rotate_right = event.key
                    elif selected == 'handbrake':
                        self.settings.handbrake = event.key
                    elif selected == 'reset_camera':
                        self.settings.reset_camera = event.key

                    self.rebinding = False

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
        c_white = (255, 255, 255)

        # Draw text
        text_surf = self.gm.font.render('Settings', False, c_white)
        surface.blit(text_surf, (self.settings.internal_res_x / 2 - 24, 20))

        # Draw resolution text
        text_surf = self.gm.font.render('Resolution:', False, c_white)
        surface.blit(text_surf, (self.settings.internal_res_x / 6, 30))

        text = self.res_list[self.res_selector]
        text_len = len(text) * 6
        text_surf = self.gm.font.render(text, False, c_white)
        surface.blit(text_surf, (3 * self.settings.internal_res_x / 6 - text_len / 2, 30))

        # Draw mouse sensitivity text
        text_surf = self.gm.font.render('Sensitivity:', False, c_white)
        surface.blit(text_surf, (self.settings.internal_res_x / 6, 40))

        text = str(self.settings.mouse_sensitivity)
        text_len = len(text) * 6
        text_surf = self.gm.font.render(text, False, c_white)
        surface.blit(text_surf, (3 * self.settings.internal_res_x / 6 - text_len / 2, 40))

        # Draw acceleration text
        text_surf = self.gm.font.render('Accelerate:', False, c_white)
        surface.blit(text_surf, (self.settings.internal_res_x / 6, 50))

        text = str(chr(self.settings.accelerate))
        text_len = len(text) * 6
        text_surf = self.gm.font.render(text, False, c_white)
        surface.blit(text_surf, (3 * self.settings.internal_res_x / 6 - text_len / 2, 50))

        # Draw deceleration text
        text_surf = self.gm.font.render('Decelerate:', False, c_white)
        surface.blit(text_surf, (self.settings.internal_res_x / 6, 60))

        text = str(chr(self.settings.decelerate))
        text_len = len(text) * 6
        text_surf = self.gm.font.render(text, False, c_white)
        surface.blit(text_surf, (3 * self.settings.internal_res_x / 6 - text_len / 2, 60))

        # Draw rotate left text
        text_surf = self.gm.font.render('Rotate Left:', False, c_white)
        surface.blit(text_surf, (self.settings.internal_res_x / 6, 70))

        text = str(chr(self.settings.rotate_left))
        text_len = len(text) * 6
        text_surf = self.gm.font.render(text, False, c_white)
        surface.blit(text_surf, (3 * self.settings.internal_res_x / 6 - text_len / 2, 70))

        # Draw rotate right text
        text_surf = self.gm.font.render('Rotate Right:', False, c_white)
        surface.blit(text_surf, (self.settings.internal_res_x / 6, 80))

        text = str(chr(self.settings.rotate_right))
        text_len = len(text) * 6
        text_surf = self.gm.font.render(text, False, c_white)
        surface.blit(text_surf, (3 * self.settings.internal_res_x / 6 - text_len / 2, 80))

        # Draw handbrake text
        text_surf = self.gm.font.render('Handbrake:', False, c_white)
        surface.blit(text_surf, (self.settings.internal_res_x / 6, 90))

        text = str(chr(self.settings.handbrake))
        if text == ' ':
            text = 'SPACE'
        text_len = len(text) * 6
        text_surf = self.gm.font.render(text, False, c_white)
        surface.blit(text_surf, (3 * self.settings.internal_res_x / 6 - text_len / 2, 90))

        # Draw reset camera text
        text_surf = self.gm.font.render('Reset Camera:', False, c_white)
        surface.blit(text_surf, (self.settings.internal_res_x / 6, 100))

        text = str(chr(self.settings.reset_camera))
        text_len = len(text) * 6
        text_surf = self.gm.font.render(text, False, c_white)
        surface.blit(text_surf, (3 * self.settings.internal_res_x / 6 - text_len / 2, 100))

        # Draw info text
        selected = self.nav_list[self.nav_y][self.nav_x]
        text = self.info_text[selected]
        if selected in ['accelerate', 'decelerate', 'rotate_left', 'rotate_right', 'handbrake', 'reset_camera'] \
                and self.rebinding:
            text = 'Press any key...'
        text_len = len(text) * 6
        text_surf = self.gm.font.render(text, False, (4, 132, 209))
        surface.blit(text_surf, (self.settings.internal_res_x / 2 - text_len / 2, 120))

        for name, button in self.buttons.items():
            button.render(surface)

            if button == self.buttons[self.nav_list[self.nav_y][self.nav_x]]:
                pygame.gfxdraw.rectangle(surface, button.rect, (229, 59, 68))

    def handle_selection(self):
        selected = self.nav_list[self.nav_y][self.nav_x]

        if selected == 'res_left':
            self.res_selector -= 1
        elif selected == 'res_right':
            self.res_selector += 1
        elif selected == 'mouse_left':
            self.settings.mouse_sensitivity -= 0.05
        elif selected == 'mouse_right':
            self.settings.mouse_sensitivity += 0.05
        elif selected in ['accelerate', 'decelerate', 'rotate_left', 'rotate_right', 'handbrake', 'reset_camera']:
            self.rebinding = True

        self.res_selector %= len(self.res_list)
        self.settings.res_x, self.settings.res_y = self.res_list[self.res_selector].split('x')
        self.settings.res_x = int(self.settings.res_x)
        self.settings.res_y = int(self.settings.res_y)
        self.settings.mouse_sensitivity = max(0.0, min(self.settings.mouse_sensitivity, 1.0))
        self.settings.mouse_sensitivity = int(round(self.settings.mouse_sensitivity * 100)) / 100

        if selected == 'back':
            self.gm.change_screens(Screens.main_menu)
        elif selected == 'save':
            self.settings.save()
            pygame.event.post(pygame.event.Event(pygame.WINDOWRESIZED))
        elif selected == 'default':
            self.settings.default()
            self.res_selector = 0
            pygame.event.post(pygame.event.Event(pygame.WINDOWRESIZED))
