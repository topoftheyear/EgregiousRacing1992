import math

import pygame

from common.point import Point
from common.settings import Settings


class Camera:
    def __init__(self, position=Point(), rotation=0, height=50, speed=4, horizon=120, scale_height=240):
        self.position = position
        self.rotation = rotation
        self.height = height
        self.speed = speed
        self.horizon = horizon
        self.scale_height = scale_height
        self.settings = Settings()

        self.moving_forward = False
        self.moving_backward = False
        self.moving_right = False
        self.moving_left = False
        self.moving_up = False
        self.moving_down = False

    def handle_input(self, events, heightmap):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == self.settings.move_right:
                    self.moving_right = True
                if event.key == self.settings.move_left:
                    self.moving_left = True
                if event.key == self.settings.move_forward:
                    self.moving_forward = True
                if event.key == self.settings.move_backward:
                    self.moving_backward = True

                if event.key == self.settings.move_up:
                    self.moving_up = True
                if event.key == self.settings.move_down:
                    self.moving_down = True

            if event.type == pygame.KEYUP:
                if event.key == self.settings.move_right:
                    self.moving_right = False
                if event.key == self.settings.move_left:
                    self.moving_left = False
                if event.key == self.settings.move_forward:
                    self.moving_forward = False
                if event.key == self.settings.move_backward:
                    self.moving_backward = False

                if event.key == self.settings.move_up:
                    self.moving_up = False
                if event.key == self.settings.move_down:
                    self.moving_down = False

        mouse_x, mouse_y = pygame.mouse.get_rel()
        if mouse_x != 0:
            self.rotation += math.radians(-mouse_x) * self.settings.mouse_sensitivity
        if mouse_y != 0:
            self.horizon += -mouse_y * self.settings.mouse_sensitivity * 10

        self.horizon = max(-4 * self.settings.internal_res_y, min(self.horizon, 8 * self.settings.internal_res_y))

        self.rotation %= 2 * math.pi

        if self.moving_forward:
            self.position.move(self.speed, self.rotation)
        if self.moving_backward:
            self.position.move(-self.speed, self.rotation)
        if self.moving_left:
            self.position.move(self.speed, self.rotation + (math.pi / 2))
        if self.moving_right:
            self.position.move(self.speed, self.rotation - (math.pi / 2))

        if self.moving_up:
            self.height += self.speed
        if self.moving_down:
            self.height -= self.speed

        self.position.x = min(self.position.x % 1024, 1023)
        self.position.y = min(self.position.y % 1024, 1023)

        self.height = max(self.height, heightmap[math.floor(self.position.x), math.floor(self.position.y)] + 1)
        self.height = min(self.height, 1000)
