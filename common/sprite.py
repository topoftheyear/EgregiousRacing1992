import pygame

from common.point import Point
from common.settings import Settings


class Sprite:
    def __init__(self, file, position=Point()):
        image = pygame.image.load(file).convert_alpha()
        self.position = position
        self.settings = Settings()

        # Scale image surface to correct resolution
        self.image = pygame.transform.scale(image,
                                            (int(image.get_width() / self.settings.res_width_ratio),
                                             int(image.get_height() / self.settings.res_height_ratio)))
