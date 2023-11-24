import math

import pygame

from common.point import Point
from common.settings import Settings


class Camera:
    def __init__(self, player, rotation=0, distance_from_player=15, horizon=120, scale_height=60):
        self.player = player
        self.position = Point()
        self.rotation = rotation
        self.v_rotation = 5.705
        self.distance = distance_from_player
        self.base_horizon = horizon
        self.horizon = horizon
        self.height = 0
        self.scale_height = scale_height
        self.settings = Settings()

    def handle_input(self, events):
        # Handle mouse wheel
        for event in events:
            if event.type == pygame.MOUSEWHEEL:
                if event.y != 0:
                    self.distance += 5 * -event.y
            if event.type == pygame.KEYDOWN:
                if event.key == self.settings.reset_camera:
                    self.rotation = self.player.rotation
                    self.v_rotation = 5.705

        self.distance = max(5, self.distance)

        # Handle mouse input for camera rotation
        mouse_x, mouse_y = pygame.mouse.get_rel()
        if mouse_x != 0:
            self.rotation += math.radians(-mouse_x) * self.settings.mouse_sensitivity
        if mouse_y != 0:
            self.v_rotation += math.radians(mouse_y) * self.settings.mouse_sensitivity

        self.rotation %= 2 * math.pi
        self.v_rotation = max(3 * math.pi / 2 + 0.05, min(self.v_rotation, int(2 * math.pi - 0.05)))

    def update(self, heightmap):
        # Set camera position and height based on current rotation and player position
        self.position.x = -self.distance * math.sin(self.rotation) * math.sin(self.v_rotation) + self.player.position.x
        self.position.y = -self.distance * math.cos(self.rotation) * math.sin(self.v_rotation) + self.player.position.y
        self.height = int(-self.distance * math.sin(self.v_rotation - (math.pi / 2)) + self.player.height)
        self.horizon = (0.42 * self.base_horizon) * -math.tan(self.v_rotation + (math.pi / 2)) + self.base_horizon

        # Clean up camera position
        self.position.x %= 1024
        self.position.y %= 1024

        self.height = max(self.height, heightmap[int(self.position.x), int(self.position.y)] + 1)
