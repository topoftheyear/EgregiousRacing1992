import math

from common.point import Point
from common.settings import Settings


class Car:
    def __init__(self, position, image, rotation=0, height=50):
        self.position = position
        self.image = image
        self.rotation = rotation
        self.height = height
        self.settings = Settings()

        self.x_velocity = 0
        self.y_velocity = 0
        self.z_velocity = 0

    def update(self, heightmap):
        # Gravity
        self.z_velocity += -9.81 / self.settings.fps_cap

        # Set position based on velocity
        self.position.x += self.x_velocity
        self.position.y += self.y_velocity
        self.height += self.z_velocity

        self.height = max(self.height, heightmap[math.floor(self.position.x), math.floor(self.position.y)])
