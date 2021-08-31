import pygame

from utils.singleton import Singleton

from common.enums import Screens
from common.settings import Settings
from utils.thread import Thread


class GameManager(metaclass=Singleton):
    def __init__(self):
        self.settings = Settings()

        self.font = pygame.font.Font('visitor2.ttf', 12)
        self.big_font = pygame.font.Font('visitor2.ttf', 26)

        self.current_screen = Screens.main_menu
        self.previous_screen = Screens.game
        self.screens = None

        self.selected_map = None

        self.score = 0

        self.timer = 90
        self.timer_max = 0
        self.timer_started = False

        self.game_ended = False
        self.game_end_timer = 0
        self.game_end_max = 3

    def update(self):
        if not self.game_ended and self.timer_started:
            self.timer -= self.settings.delta_time

            self.timer = max(0, self.timer)

            if self.timer == self.timer_max:
                self.game_ended = True
        if self.game_ended:
            self.game_end_timer += self.settings.delta_time

            if self.game_end_timer >= self.game_end_max:
                self.change_screens(Screens.game_end)

    def change_screens(self, new_screen):
        self.previous_screen = self.current_screen
        self.current_screen = new_screen

    def unload_previous_screen(self):
        # Unload existing screen and replace the thread
        self.screens[self.previous_screen]['screen'].unload()
        thr = Thread(self.screens[self.previous_screen]['screen'].load, ())
        self.screens[self.previous_screen]['thread'] = thr

    def reset_game(self):
        self.score = 0

        self.timer = 90
        self.timer_started = False

        self.game_ended = False
        self.game_end_timer = 0
