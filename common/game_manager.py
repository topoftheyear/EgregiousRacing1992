import pygame

from utils.singleton import Singleton

from common.enums import Screens
from utils.thread import Thread


class GameManager(metaclass=Singleton):
    def __init__(self):
        self.font = pygame.font.Font('visitor2.ttf', 12)

        self.current_screen = Screens.main_menu

        self.screens = None

    def change_screens(self, new_screen):
        # Unload existing screen and replace the thread
        self.screens[self.current_screen]['screen'].unload()
        thr = Thread(self.screens[self.current_screen]['screen'].load, ())
        self.screens[self.current_screen]['thread'] = thr

        self.current_screen = new_screen
