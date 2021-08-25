import pygame

from utils.singleton import Singleton

from common.enums import Screens
from utils.thread import Thread


class GameManager(metaclass=Singleton):
    def __init__(self):
        self.font = pygame.font.Font('visitor2.ttf', 12)

        self.current_screen = Screens.main_menu
        self.previous_screen = Screens.game
        self.screens = None

        self.selected_map = None

    def change_screens(self, new_screen):
        self.previous_screen = self.current_screen
        self.current_screen = new_screen

    def unload_previous_screen(self):
        # Unload existing screen and replace the thread
        self.screens[self.previous_screen]['screen'].unload()
        thr = Thread(self.screens[self.previous_screen]['screen'].load, ())
        self.screens[self.previous_screen]['thread'] = thr
