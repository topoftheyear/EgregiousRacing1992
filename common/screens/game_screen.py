import ctypes
import math
import random

import cv2
import pygame
import pygame.gfxdraw

from common.car import Car
from common.camera import Camera
from common.coin import Coin
from common.game_manager import GameManager
from common.point import Point
from common.screens.screen import Screen
from common.settings import Settings
from utils.helpers import heightmap_to_ctypes, colormap_to_ctypes, distance, wrapping_distance


class GameScreen(Screen):
    def __init__(self):
        super().__init__()
        self.mouse_visible = False
        self.mouse_grab = True

        self.line_calculator = ctypes.CDLL('dll/liblines.dll')
        self.line_calculator.get_lines.argtypes = [ctypes.POINTER(LineStruct)]
        self.line_calculator.get_lines.restype = None

        self.ls = LineStruct()

        self.heightmap = None
        self.colormap = None

        self.settings = Settings()
        self.gm = GameManager()

        self.object_list = dict()
        self.car = None
        self.camera = None

        self.num_coins = 0
        self.max_coins = 10

        self.air_color_selector = 0
        self.air_colors = [
            (255, 231, 98),
            (251, 146, 43),
            (229, 59, 68),
            (158, 40, 53),
            (4, 132, 209),
            (44, 232, 244),
            (255, 255, 255),
            (175, 191, 210),
            (79, 103, 129),
            (50, 115, 69),
            (99, 198, 77)
        ]
        self.descriptor = ''

        self.air_timer = 0

        self.max_loading = 4

    def load(self):
        self.current_loading = 0

        # Load in selected heightmap and colormap
        self.heightmap = cv2.imread(f'img/C{self.gm.selected_map}H.png', 0)
        self.colormap = cv2.imread(f'img/C{self.gm.selected_map}.png', -1)
        self.colormap = cv2.cvtColor(self.colormap, cv2.COLOR_BGR2RGB)
        self.current_loading += 1

        # Resize images
        self.heightmap = cv2.resize(self.heightmap, (1024, 1024))
        self.colormap = cv2.resize(self.colormap, (1024, 1024))
        self.current_loading += 1

        # Convert maps to ctypes and set to ls, set other one-time struct variables
        heightmap_to_ctypes(self.ls.heightMap, self.heightmap)
        colormap_to_ctypes(self.ls.colorMap, self.colormap)
        self.ls.screenWidth = self.settings.internal_res_x
        self.ls.screenHeight = self.settings.internal_res_y
        self.ls.quality = self.settings.quality
        self.current_loading += 1

        # Generate necessary objects
        self.car = Car(Point(512, 512), height=1000)
        self.camera = Camera(self.car)
        self.object_list[self.car.id] = self.car

        self.current_loading += 1

        self.loaded = True

    def unload(self):
        super().unload()

        self.heightmap = None
        self.colormap = None

        self.object_list = dict()
        self.car = None
        self.camera = None

        self.num_coins = 0

        self.air_color_selector = 0
        self.descriptor = ''

        self.air_timer = 0

    def update(self, events):
        self.gm.update()

        if not self.gm.game_ended:
            if self.gm.timer_started:
                # Handle inputs
                self.car.handle_input(events)
                self.camera.handle_input(events)

            # Spawn coins if necessary
            if self.num_coins < self.max_coins:
                for _ in range(self.max_coins - self.num_coins):
                    self.num_coins += 1
                    temp = Coin(Point(random.randint(0, 1023), random.randint(0, 1023)), height=500)
                    self.object_list[temp.id] = temp

            # Update objects
            for obj in self.object_list.values():
                obj.update(self.heightmap, self.camera)

            self.camera.update(self.heightmap)

            objects_to_remove = list()
            # Check for car collisions with coins
            for obj in self.object_list.values():
                if obj.id == self.car.id:
                    continue

                scale_distance = wrapping_distance(self.car.position.x, self.car.position.y, self.car.height,
                                                   obj.position.x, obj.position.y, obj.height)

                # Remove coin from existence
                if scale_distance < 6:
                    self.gm.score += 100
                    objects_to_remove.append(obj)
                    self.num_coins -= 1

            # Delete objects
            for obj in objects_to_remove:
                self.object_list.pop(obj.id)
                del obj

            # Set per-frame struct variables
            self.ls.currentX = self.camera.position.x
            self.ls.currentY = self.camera.position.y
            self.ls.rotation = self.camera.rotation
            self.ls.height = self.camera.height
            self.ls.horizon = self.camera.horizon / self.settings.res_width_ratio
            self.ls.scaleHeight = self.camera.scale_height / self.settings.res_height_ratio
            self.ls.distance = self.settings.view_distance
            self.ls.numObjects = len(self.object_list.keys())
            x = 0
            for obj in self.object_list.values():
                self.ls.objects[x][0] = obj.id
                self.ls.objects[x][1] = int(obj.position.x)
                self.ls.objects[x][2] = int(obj.position.y)
                self.ls.objects[x][3] = int(obj.height)
                self.ls.objects[x][4] = 0
                self.ls.objects[x][5] = 0

                x += 1

        self.air_timer -= self.settings.delta_time

    def render(self, surface):
        surface.fill((135, 206, 235))

        self.line_calculator.get_lines(ctypes.byref(self.ls))

        for x in range(self.ls.numLines):
            line = self.ls.lines[x]

            pygame.gfxdraw.vline(
                surface,
                line[0],
                line[1],
                line[2],
                [line[3], line[4], line[5]],
            )

        # Get sorted object_list by distance from camera
        temp_dict = dict()
        for key, value in self.object_list.items():
            temp_dict[key] = distance(value.position, self.camera.position)
        sorted_objects = dict(sorted(temp_dict.items(), key=lambda item: item[1])[::-1])

        for key in sorted_objects.keys():
            obj = self.object_list[key]

            pos = [0, 0]
            for x in range(self.ls.numObjects):
                if key == self.ls.objects[x][0]:
                    pos = [self.ls.objects[x][4], self.ls.objects[x][5]]

            if pos[0] == 0 and pos[1] == 0:
                continue

            if pos[0] < 0 or pos[0] >= 1023 and pos[1] < 0 or pos[1] >= 1023:
                continue

            # Scale based on distance from camera
            scale_distance = wrapping_distance(self.ls.currentX, self.ls.currentY, self.ls.height,
                                               obj.position.x, obj.position.y, obj.height)
            scale_ratio = (1 / (scale_distance / self.settings.view_distance)) / 50
            scaled_obj = obj.sprite_sheet.get_image()
            scaled_obj = pygame.transform.scale(scaled_obj, (int(scaled_obj.get_width() * scale_ratio),
                                                             int(scaled_obj.get_height() * scale_ratio)))

            shifted_width = int(pos[0] - (scaled_obj.get_width() / 2))
            shifted_height = int(pos[1] - (scaled_obj.get_height() / 2))

            surface.blit(
                scaled_obj,
                [shifted_width, shifted_height]
            )

        # Draw UI
        if self.gm.timer == 90:
            text_surf = self.gm.big_font.render('Ready?', False, (0, 0, 0))
            surface.blit(text_surf, (self.settings.internal_res_x / 2 - 36 + 1, 10 + 1))

            text_surf = self.gm.big_font.render('Ready?', False, (255, 255, 255))
            surface.blit(text_surf, (self.settings.internal_res_x / 2 - 36, 10))
        elif self.gm.timer >= 89:
            text_surf = self.gm.big_font.render('Go!', False, (0, 0, 0))
            surface.blit(text_surf, (self.settings.internal_res_x / 2 - 18 + 1, 10 + 1))

            text_surf = self.gm.big_font.render('Go!', False, (255, 255, 255))
            surface.blit(text_surf, (self.settings.internal_res_x / 2 - 18, 10))
        elif self.gm.timer == 0:
            text_surf = self.gm.big_font.render('Time!', False, (0, 0, 0))
            surface.blit(text_surf, (self.settings.internal_res_x / 2 - 30 + 1, 10 + 1))

            text_surf = self.gm.big_font.render('Time!', False, (255, 255, 255))
            surface.blit(text_surf, (self.settings.internal_res_x / 2 - 30, 10))
        else:
            text = str(int(self.gm.timer * 100) / 100)
            ones, decimals = text.split('.')
            if len(decimals) < 2:
                decimals += '0'
            ones_length = len(ones) * 12
            text_surf = self.gm.big_font.render(ones, False, (0, 0, 0))
            surface.blit(text_surf, (self.settings.internal_res_x / 2 - ones_length / 2 + 1, 10 + 1))
            text_surf = self.gm.font.render(decimals, False, (0, 0, 0))
            surface.blit(text_surf, (self.settings.internal_res_x / 2 + ones_length / 2 + 1, 17 + 1))

            ratio = 1 - (self.gm.timer / 90)
            color_lerp = (
                (ratio * 229) + ((1 - ratio) * 255),
                (ratio * 59) + ((1 - ratio) * 255),
                (ratio * 68) + ((1 - ratio) * 255),
            )
            text_surf = self.gm.big_font.render(ones, False, color_lerp)
            surface.blit(text_surf, (self.settings.internal_res_x / 2 - ones_length / 2, 10))
            text_surf = self.gm.font.render(decimals, False, color_lerp)
            surface.blit(text_surf, (self.settings.internal_res_x / 2 + ones_length / 2, 17))

        # Draw score
        text = str(self.gm.score)
        text_length = len(text) * 12
        text_surf = self.gm.big_font.render(text, False, (0, 0, 0))
        surface.blit(text_surf, (self.settings.internal_res_x - text_surf.get_width() - 10 + 1, 10 + 1))
        text_surf = self.gm.big_font.render(text, False, (255, 255, 255))
        surface.blit(text_surf, (self.settings.internal_res_x - text_surf.get_width() - 10, 10))

        # Draw airtime
        air_score = int(self.car.air_time * 15)
        if air_score >= 10:
            text = '+' + str(air_score)

            text_surf = self.gm.font.render(text, False, (0, 0, 0))
            surface.blit(text_surf, (self.settings.internal_res_x - text_surf.get_width() - 10 + 1, 30 + 1))
            text_surf = self.gm.font.render(text, False, (255, 255, 255))
            surface.blit(text_surf, (self.settings.internal_res_x - text_surf.get_width() - 10, 30))

            if abs(self.car.in_air_rotation) >= math.pi / 2:
                text = 'x' + str(1 + (0.1 * int(abs(math.degrees(self.car.in_air_rotation)) / 90)))
                text_surf = self.gm.font.render(text, False, (0, 0, 0))
                surface.blit(text_surf, (self.settings.internal_res_x - text_surf.get_width() - 10 + 1, 38 + 1))
                text_surf = self.gm.font.render(text, False, (229, 59, 68))
                surface.blit(text_surf, (self.settings.internal_res_x - text_surf.get_width() - 10, 38))

            if air_score > 1000:
                self.descriptor = 'How'
            elif air_score > 500:
                self.descriptor = 'Mega Mondo Extreme Air'
            elif air_score > 100:
                self.descriptor = 'WTF'
            elif air_score > 50:
                self.descriptor = 'Colossal Air'
            elif air_score > 35:
                self.descriptor = 'Massive Air'
            elif air_score > 20:
                self.descriptor = 'Huge Air'
            elif air_score > 10:
                self.descriptor = 'Nice Air'
            else:
                self.descriptor = ''

            self.air_timer = 1

            if abs(self.car.in_air_rotation) >= math.pi / 2:
                self.descriptor += ' + ' + str(int(abs(math.degrees(self.car.in_air_rotation)) / 90 * 90)) + '°'

        if self.air_timer > 0:
            if self.air_timer != 1:
                self.descriptor += '  '

            text_length = len(self.descriptor) * 6
            text_surf = self.gm.font.render(self.descriptor, False, (0, 0, 0))
            surface.blit(text_surf, (self.settings.internal_res_x / 2 - text_length / 2 + 1, 30 + 1))
            text_surf = self.gm.font.render(self.descriptor, False, self.air_colors[int(self.air_color_selector)])
            surface.blit(text_surf, (self.settings.internal_res_x / 2 - text_length / 2, 30))

            self.air_color_selector += 0.5
            self.air_color_selector %= len(self.air_colors)

        # Draw speed
        text = str(int((abs(self.car.x_velocity) + abs(self.car.y_velocity)) * 12)) + ' mph'
        text_surf = self.gm.big_font.render(text, False, (0, 0, 0))
        surface.blit(text_surf, (self.settings.internal_res_x - text_surf.get_width() + 1, self.settings.internal_res_y - 20 + 1))
        text_surf = self.gm.big_font.render(text, False, (255, 255, 255))
        surface.blit(text_surf, (self.settings.internal_res_x - text_surf.get_width(), self.settings.internal_res_y - 20))


class LineStruct(ctypes.Structure):
    _fields_ = [
        ('lines', (ctypes.c_int * 6) * 1000000),
        ('numLines', ctypes.c_int),
        ('objects', (ctypes.c_int * 6) * 10000),
        ('numObjects', ctypes.c_int),
        ('heightMap', (ctypes.c_int * 1024) * 1024),
        ('colorMap', ((ctypes.c_int * 3) * 1024) * 1024),
        ('currentX', ctypes.c_float),
        ('currentY', ctypes.c_float),
        ('rotation', ctypes.c_float),
        ('height', ctypes.c_int),
        ('horizon', ctypes.c_float),
        ('scaleHeight', ctypes.c_float),
        ('distance', ctypes.c_int),
        ('screenWidth', ctypes.c_int),
        ('screenHeight', ctypes.c_int),
        ('quality', ctypes.c_float),
    ]