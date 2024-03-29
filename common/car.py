import math

import pygame

from common.enums import CarAnimStates
from common.game_manager import GameManager
from common.game_object import GameObject
from common.point import Point
from common.settings import Settings
from common.spritesheet import Spritesheet
from utils.helpers import *


class Car(GameObject):
    def __init__(self, position, rotation=0, height=50):
        super().__init__(position, height)
        self.gm = GameManager()

        self.rotation = rotation
        self.air_rotation_speed_multiplier = 1.5
        self.acceleration_speed = 3
        self.settings = Settings()

        self.establish_frames()

        self.x_velocity = 0
        self.y_velocity = 0
        self.z_velocity = 0

        # Input trackers
        self.moving_forward = False
        self.moving_backward = False
        self.rotating_left = False
        self.rotating_right = False
        self.braking = False

        self.air_time = 0
        self.in_air_rotation = 0

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
                if event.key == self.settings.handbrake:
                    self.braking = True

            if event.type == pygame.KEYUP:
                if event.key == self.settings.accelerate:
                    self.moving_forward = False
                if event.key == self.settings.decelerate:
                    self.moving_backward = False
                if event.key == self.settings.rotate_left:
                    self.rotating_left = False
                if event.key == self.settings.rotate_right:
                    self.rotating_right = False
                if event.key == self.settings.handbrake:
                    self.braking = False

    def update(self, heightmap, camera):
        # Start timer when touching the ground
        if self.height <= heightmap[math.floor(self.position.x), math.floor(self.position.y)]:
            self.gm.timer_started = True

            if self.air_time >= 1:
                rotation_mult = 1 + (0.1 * int(abs(math.degrees(self.in_air_rotation)) / 90))
                self.gm.score += int(self.air_time * 15 * rotation_mult)

            self.air_time = 0
            self.in_air_rotation = 0
        else:
            if self.gm.timer_started:
                self.air_time += self.settings.delta_time

        # Create total move vector strength
        move_strength = 0

        # Handle key results
        # Major velocity changes shouldn't be able to happen in the air
        if self.height <= heightmap[math.floor(self.position.x), math.floor(self.position.y)]:
            if self.moving_forward:
                move_strength += -self.acceleration_speed
            if self.moving_backward:
                move_strength += self.acceleration_speed
        # Allow slight velocity changes in the air to make moving downhill easier
        else:
            if self.moving_forward:
                move_strength += -(self.acceleration_speed / 4)
            if self.moving_backward:
                move_strength += (self.acceleration_speed / 4)
        if self.rotating_left:
            amt = math.pi / 2 * self.settings.delta_time
            if self.air_time > 0:
                amt *= self.air_rotation_speed_multiplier
                self.in_air_rotation += amt
            self.rotation += amt
            camera.rotation += amt
        if self.rotating_right:
            amt = -math.pi / 2 * self.settings.delta_time
            if self.air_time > 0:
                amt *= self.air_rotation_speed_multiplier
                self.in_air_rotation += amt
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

        move_reduction = 0

        total_velocity = (abs(self.x_velocity) + abs(self.y_velocity)) / self.settings.delta_time
        momentum_angle = 2 * math.pi - (math.atan2(self.y_velocity, self.x_velocity) + math.pi / 2) % (2 * math.pi)

        # Total velocity reductions
        heightmap_num = heightmap[math.floor(self.position.x), math.floor(self.position.y)]
        if self.height <= heightmap_num:
            self.height = heightmap_num

            # Reduce velocities if touching ground (traditional friction), dependent on car direction
            if total_velocity != 0:
                angle = (self.rotation - momentum_angle) % math.pi
                working_angle = min(angle, math.pi - angle)
                ratio = working_angle / (math.pi / 2)

                move_reduction = ratio * 5 + 0.5

            # Add braking if on the ground
            if self.braking:
                move_reduction += 2

        # Reduce velocities by a set amount anyway (air friction)
        move_reduction += 0.5

        self.x_velocity += move_strength * math.sin(self.rotation) * self.settings.delta_time
        self.y_velocity += move_strength * math.cos(self.rotation) * self.settings.delta_time

        x_reduce = abs(move_reduction * math.sin(momentum_angle) * self.settings.delta_time)
        y_reduce = abs(move_reduction * math.cos(momentum_angle) * self.settings.delta_time)

        self.x_velocity = reduce(self.x_velocity, x_reduce)
        self.y_velocity = reduce(self.y_velocity, y_reduce)

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
                    self.z_velocity += (abs(self.x_velocity) + abs(self.y_velocity)) * (max_height - self.height) * 1.25 * self.settings.delta_time

        # Set position based on velocity
        self.position.x += self.x_velocity
        self.position.y += self.y_velocity
        self.height += self.z_velocity

        # Clean up positions
        self.position.x %= 1024
        self.position.y %= 1024

        # Animation business
        # Determine camera facing direction relative to car
        relative_rotation = (camera.rotation - self.rotation) % (2 * math.pi)
        direction = ''
        if relative_rotation > 7 * math.pi / 4 or relative_rotation <= math.pi / 4:
            direction = 'back'
        elif math.pi / 4 < relative_rotation <= 3 * math.pi / 4:
            direction = 'right'
        elif 3 * math.pi / 4 < relative_rotation <= 5 * math.pi / 4:
            direction = 'front'
        elif 5 * math.pi / 4 < relative_rotation <= 7 * math.pi / 4:
            direction = 'left'

        # Determine movement state
        if self.x_velocity != 0 or self.y_velocity != 0:
            direction += 'on'
        else:
            direction += 'off'

        # Set animation speed
        self.sprite_sheet.animation_speed = (abs(self.x_velocity) + abs(self.y_velocity)) * 10

        state_dict = {
            'backoff': CarAnimStates.back_view_off,
            'leftoff': CarAnimStates.left_view_off,
            'frontoff': CarAnimStates.front_view_off,
            'rightoff': CarAnimStates.right_view_off,
            'backon': CarAnimStates.back_view_on,
            'lefton': CarAnimStates.left_view_on,
            'fronton': CarAnimStates.front_view_on,
            'righton': CarAnimStates.right_view_on,
        }

        self.sprite_sheet.current_state = state_dict[direction]
        self.sprite_sheet.update()

    def establish_frames(self):
        states = dict()
        states[CarAnimStates.back_view_off] = [
            (0, 0, 64, 64)
        ]
        states[CarAnimStates.back_view_on] = [
            (64, 0, 64, 64), (128, 0, 64, 64), (192, 0, 64, 64), (256, 0, 64, 64)
        ]
        states[CarAnimStates.left_view_off] = [
            (0, 64, 64, 64)
        ]
        states[CarAnimStates.left_view_on] = [
            (64, 64, 64, 64), (128, 64, 64, 64), (192, 64, 64, 64), (256, 64, 64, 64)
        ]
        states[CarAnimStates.front_view_off] = [
            (0, 128, 64, 64)
        ]
        states[CarAnimStates.front_view_on] = [
            (64, 128, 64, 64), (128, 128, 64, 64), (192, 128, 64, 64), (256, 128, 64, 64)
        ]
        states[CarAnimStates.right_view_off] = [
            (0, 192, 64, 64)
        ]
        states[CarAnimStates.right_view_on] = [
            (64, 192, 64, 64), (128, 192, 64, 64), (192, 192, 64, 64), (256, 192, 64, 64)
        ]
        self.sprite_sheet = Spritesheet('img/car.png', states, 8)
