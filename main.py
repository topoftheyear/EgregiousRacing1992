import math
import random
import sys
import time

import ctypes
import cv2
import numpy as np
import pygame
import pygame.gfxdraw

from common.camera import Camera
from common.car import Car
from common.coin import Coin
from common.settings import Settings
from common.point import Point
from utils.helpers import *

pygame.init()
settings = Settings()

flags = pygame.DOUBLEBUF
screen = pygame.display.set_mode((settings.res_x, settings.res_y), flags)
pygame.display.set_caption('Egregious Racing 1992')

surface = pygame.Surface((settings.internal_res_x, settings.internal_res_y))
scaled_surface = pygame.Surface(screen.get_size())

clock = pygame.time.Clock()

heightmap = cv2.imread('img/D1.png', 0)
colormap = cv2.imread('img/C1.png', -1)
colormap = cv2.cvtColor(colormap, cv2.COLOR_BGR2RGB)

# Resize images
heightmap = cv2.resize(heightmap, (1024, 1024))
colormap = cv2.resize(colormap, (1024, 1024))

pygame.mouse.set_visible(False)
pygame.event.set_grab(True)


# establish c function
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


line_calculator = ctypes.CDLL('liblines.dll')
line_calculator.get_lines.argtypes = [ctypes.POINTER(LineStruct)]
line_calculator.get_lines.restype = None

ls = LineStruct()

object_list = dict()

car = Car(Point(955, 73), height=1000)
camera = Camera(car)

object_list[car.id] = car

for _ in range(10):
    temp = Coin(Point(random.randint(0, 1023), random.randint(0, 1023)), height=0)
    object_list[temp.id] = temp


def main():
    quality = settings.start_quality

    # Set one-time struct variables
    ls.heightMap = heightmap_to_ctypes(ls.heightMap, heightmap)
    ls.colorMap = colormap_to_ctypes(ls.colorMap, colormap)
    ls.screenWidth = surface.get_width()
    ls.screenHeight = surface.get_height()

    print("Starting loop")
    while 1:
        start = time.time()

        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                pygame.display.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_EQUALS:
                    quality -= settings.quality_chunks
                if event.key == pygame.K_MINUS:
                    quality += settings.quality_chunks

                if event.key == pygame.K_ESCAPE:
                    pygame.display.quit()
                    sys.exit()

        # Handle inputs
        car.handle_input(events)
        camera.handle_input(events)

        quality = max(quality, 0)

        # Update objects
        for obj in object_list.values():
            obj.update(heightmap, camera)

        camera.update(heightmap)

        # Set per-frame struct variables
        ls.currentX = camera.position.x
        ls.currentY = camera.position.y
        ls.rotation = camera.rotation
        ls.height = camera.height
        ls.horizon = camera.horizon / settings.res_width_ratio
        ls.scaleHeight = camera.scale_height / settings.res_height_ratio
        ls.distance = settings.view_distance
        ls.quality = quality
        ls.numObjects = len(object_list.keys())
        x = 0
        for obj in object_list.values():
            ls.objects[x][0] = obj.id
            ls.objects[x][1] = int(obj.position.x)
            ls.objects[x][2] = int(obj.position.y)
            ls.objects[x][3] = int(obj.height)
            ls.objects[x][4] = 0
            ls.objects[x][5] = 0

            x += 1

        # Draw objects
        render()

        pygame.display.update()

        # Update clock and delta time
        clock.tick(settings.fps_cap)
        settings.delta_time = clock.get_time() / 1000

        #print(1 / (time.time() - start))


def render():
    surface.fill((135, 206, 235))

    line_calculator.get_lines(ctypes.byref(ls))

    for x in range(ls.numLines):
        line = ls.lines[x]

        pygame.gfxdraw.vline(
            surface,
            line[0],
            line[1],
            line[2],
            [line[3], line[4], line[5]],
        )

    for x in range(ls.numObjects):
        obj = object_list[ls.objects[x][0]]
        pos = [ls.objects[x][4], ls.objects[x][5]]

        if pos[0] == 0 and pos[1] == 0:
            continue

        if pos[0] < 0 or pos[0] >= 1023 and pos[1] < 0 or pos[1] >= 1023:
            continue

        # Scale based on distance from camera
        campy = np.array([ls.currentX, ls.currentY, ls.height])
        objpy = np.array([obj.position.x, obj.position.y, obj.height])
        scale_distance = np.linalg.norm(campy - objpy)
        scale_ratio = (1 / (scale_distance / settings.view_distance)) / 50
        scaled_obj = obj.sprite_sheet.get_image()
        scaled_obj = pygame.transform.scale(scaled_obj, (int(scaled_obj.get_width() * scale_ratio),
                                                         int(scaled_obj.get_height() * scale_ratio)))

        shifted_width = int(pos[0] - (scaled_obj.get_width() / 2))
        shifted_height = int(pos[1] - (scaled_obj.get_height() / 2))

        surface.blit(
            scaled_obj,
            [shifted_width, shifted_height]
        )

    pygame.transform.scale(surface, screen.get_size(), scaled_surface)
    screen.blit(scaled_surface, (0, 0))


if __name__ == '__main__':
    main()


def __main__():
    main()
