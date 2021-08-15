import ctypes
import random

import cv2
import numpy as np
import pygame
import pygame.gfxdraw

from common.car import Car
from common.camera import Camera
from common.coin import Coin
from common.point import Point
from common.screens.screen import Screen
from common.settings import Settings
from utils.helpers import heightmap_to_ctypes, colormap_to_ctypes, distance


class GameScreen(Screen):
    def __init__(self):
        super().__init__()
        self.mouse_visible = False
        self.mouse_grab = True

        self.line_calculator = ctypes.CDLL('liblines.dll')
        self.line_calculator.get_lines.argtypes = [ctypes.POINTER(LineStruct)]
        self.line_calculator.get_lines.restype = None

        self.ls = LineStruct()

        self.selected_map = 'C1'
        self.heightmap = None
        self.colormap = None

        self.settings = Settings()

        self.object_list = dict()
        self.car = None
        self.camera = None

        self.max_loading = 4

    def load(self):
        self.current_loading = 0

        # Load in selected heightmap and colormap
        self.heightmap = cv2.imread(f'img/{self.selected_map}H.png', 0)
        self.colormap = cv2.imread(f'img/{self.selected_map}.png', -1)
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

        for _ in range(10):
            temp = Coin(Point(random.randint(0, 1023), random.randint(0, 1023)), height=0)
            self.object_list[temp.id] = temp
        self.current_loading += 1

        self.loaded = True

    def update(self, events):
        # Handle inputs
        self.car.handle_input(events)
        self.camera.handle_input(events)

        # Update objects
        for obj in self.object_list.values():
            obj.update(self.heightmap, self.camera)

        self.camera.update(self.heightmap)

        objects_to_remove = list()
        # Check for car collisions with coins
        for obj in self.object_list.values():
            if obj.id == self.car.id:
                continue

            carpy = np.array([self.car.position.x, self.car.position.y, self.car.height])
            objpy = np.array([obj.position.x, obj.position.y, obj.height])
            scale_distance = np.linalg.norm(carpy - objpy)

            # Remove coin from existence
            if scale_distance < 5:
                objects_to_remove.append(obj)

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
            campy = np.array([self.ls.currentX, self.ls.currentY, self.ls.height])
            objpy = np.array([obj.position.x, obj.position.y, obj.height])
            scale_distance = np.linalg.norm(campy - objpy)
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