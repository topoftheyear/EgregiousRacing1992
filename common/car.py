import math

import pygame

from common.point import Point
from common.settings import Settings
from utils.helpers import *


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

    def update(self, heightmap, camera):
        # Handle key results
        if self.moving_forward:
            self.x_velocity += self.acceleration_speed * math.sin(self.rotation - math.pi) * self.settings.delta_time
            self.y_velocity += self.acceleration_speed * math.cos(self.rotation - math.pi) * self.settings.delta_time
        if self.moving_backward:
            self.x_velocity += -self.acceleration_speed * math.sin(self.rotation - math.pi) * self.settings.delta_time
            self.y_velocity += -self.acceleration_speed * math.cos(self.rotation - math.pi) * self.settings.delta_time
        if self.rotating_left:
            amt = math.pi / 2 * self.settings.delta_time
            self.rotation += amt
            camera.rotation += amt
        if self.rotating_right:
            amt = -math.pi / 2 * self.settings.delta_time
            self.rotation += amt
            camera.rotation += amt

        # Clean up movement variables
        self.rotation %= 2 * math.pi

        # Gravity if not touching the ground
        if self.height > heightmap[math.floor(self.position.x), math.floor(self.position.y)]:
            self.z_velocity += -9.81 * self.settings.delta_time
        # Reset velocity to 0 if velocity is negative
        else:
            if self.z_velocity < 0:
                self.z_velocity = 0

        # Get points list based on velocity
        future_pos = Point(self.position.x, self.position.y)
        future_pos.x += self.x_velocity
        future_pos.y += self.y_velocity

        points_list = points_between(self.position, future_pos, True)

        if points_list is not None:
            # Derive z velocity based on supposed height gain
            height_list = list()
            for point in points_list:
                height_list.append(heightmap[point.x, point.y])

            if len(height_list) > 0:
                max_height = max(height_list)

                if max_height > self.height:
                    self.z_velocity += abs(self.x_velocity + self.y_velocity) * (max_height - self.height) * self.settings.delta_time

        # Set position based on velocity
        self.position.x += self.x_velocity
        self.position.y += self.y_velocity
        self.height += self.z_velocity

        # Clean up positions
        self.position.x %= 1024
        self.position.y %= 1024

        heightmap_num = heightmap[math.floor(self.position.x), math.floor(self.position.y)]
        if self.height <= heightmap_num:
            self.height = heightmap_num

            # Reduce velocities if touching ground
            self.x_velocity = reduce(self.x_velocity, 1 * self.settings.delta_time)
            self.y_velocity = reduce(self.y_velocity, 1 * self.settings.delta_time)
