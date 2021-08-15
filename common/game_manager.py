import pygame

from utils.singleton import Singleton


class GameManager(metaclass=Singleton):
    def __init__(self):
        self.font = pygame.font.Font('visitor2.ttf', 12)
