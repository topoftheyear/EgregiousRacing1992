import math

import pygame

from common.point import Point
from common.settings import Settings
from utils.helpers import reduce


class Car:
    def __init__(self, position, image, rotation=0, height=50):
        self.position = position
        self.image = image
        self.rotation = rotation
        self.height = height
        self.acceleration_speed = 2
        self.settings = Settings()

        self.x_velocity = 0
        self.y_velocity = 0
        self.z_velocity = 0

        # Input trackers
        self.moving_forward = False
        self.moving_backward = False
        self.rotating_left = False
        self.rotating_right = False

    def handle_input(self, events):
        # Check keys
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == self.settings.accelerate:
                    self.moving_forward = True
                if event.key == self.settings.decelerate:
                    self.moving_backward = True
                if event.key == self.settings.rotate_left:
                    self.rotating_left = True
                if event.key == self.settings.rotate_right:
                    self.rotating_right = True

            if event.type == pygame.KEYUP:
                if event.key == self.settings.accelerate:
                    self.moving_forward = False
                if event.key == self.settings.decelerate:
                    self.moving_backward = False
                if event.key == self.settings.rotate_left:
                    self.rotating_left = False
                if event.key == self.settings.rotate_right:
                    self.rotating_right = False

        # Handle key results
        if self.moving_forward:
            self.x_velocity += self.acceleration_speed * math.sin(self.rotation - math.pi) * self.settings.delta_time
            self.y_velocity += self.acceleration_speed * math.cos(self.rotation - math.pi) * self.settings.delta_time
        if self.moving_backward:
            self.x_velocity += -self.acceleration_speed * math.sin(self.rotation - math.pi) * self.settings.delta_time
            self.y_velocity += -self.acceleration_speed * math.cos(self.rotation - math.pi) * self.settings.delta_time
        if self.rotating_left:
            self.rotation += math.pi / 2 * self.settings.delta_time
        if self.rotating_right:
            self.rotation += -math.pi / 2 * self.settings.delta_time

        # Clean up movement variables
        self.rotation %= 2 * math.pi

    def update(self, heightmap):
        # Gravity
        self.z_velocity += -9.81 * self.settings.delta_time

        # Set position based on velocity
        self.position.x += self.x_velocity
        self.position.y += self.y_velocity
        self.height += self.z_velocity

        # Clean up positions
        self.position.x %= 1024
        self.position.y %= 1024

        self.height = max(self.height, heightmap[math.floor(self.position.x), math.floor(self.position.y)])

        # Reduce velocities
        self.x_velocity = reduce(self.x_velocity, 1 * self.settings.delta_time)
        self.y_velocity = reduce(self.y_velocity, 1 * self.settings.delta_time)
