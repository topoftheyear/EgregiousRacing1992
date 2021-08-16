import pygame

from utils.singleton import Singleton

from common.enums import Screens


class GameManager(metaclass=Singleton):
    def __init__(self):
        self.font = pygame.font.Font('visitor2.ttf', 12)

        self.current_screen = Screens.main_menu

        self.screens = None
