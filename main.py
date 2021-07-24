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
from common.settings import Settings
from common.point import Point
from utils.helpers import *

pygame.init()
settings = Settings()

flags = pygame.DOUBLEBUF
screen = pygame.display.set_mode((settings.res_x, settings.res_y), flags)
pygame.display.set_caption("VoxelSpace")

surface = pygame.Surface((settings.internal_res_x, settings.internal_res_y))
scaled_surface = pygame.Surface(screen.get_size())

clock = pygame.time.Clock()

heightmap = cv2.imread('img/1H.png', 0)
colormap = cv2.imread('img/1C.png', -1)
colormap = cv2.cvtColor(colormap, cv2.COLOR_BGR2RGB)

pygame.mouse.set_visible(False)
pygame.event.set_grab(True)


# establish c function
class LineStruct(ctypes.Structure):
    _fields_ = [
        ('lines', (ctypes.c_int * 6) * 1000000),
        ('numLines', ctypes.c_int),
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

#worf = Sprite('img/worf.png', Point(500, 500))
worf = pygame.image.load('img/worf.png').convert_alpha()
worf = pygame.transform.scale(worf, (int(worf.get_width() / settings.res_width_ratio),
                                     int(worf.get_height() / settings.res_height_ratio)))

car = Car(Point(10, 10), worf, height=1000)
camera = Camera(car)


def main():
    quality = settings.start_quality

    # Set one-time struct variables
    ls.heightMap = heightmap_to_ctypes(ls.heightMap, heightmap)
    ls.colorMap = colormap_to_ctypes(ls.colorMap, colormap)
    ls.screenWidth = surface.get_width()
    ls.screenHeight = surface.get_height()

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
        car.update(heightmap, camera)
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

    # Determine height on screen
    cam_car_distance = distance(camera.position, car.position)
    temp_horizon = camera.horizon / settings.res_width_ratio
    temp_scaling = camera.scale_height / settings.res_height_ratio
    height_on_screen = (camera.height - car.height) / cam_car_distance * temp_scaling + temp_horizon

    # Scale based on distance from camera
    campy = np.array([camera.position.x, camera.position.y, camera.height])
    carpy = np.array([car.position.x, car.position.y, car.height])
    scale_distance = np.linalg.norm(campy - carpy)
    scale_ratio = (1 / (scale_distance / settings.view_distance)) / 100
    scaled_car = car.image
    scaled_car = pygame.transform.scale(scaled_car, (int(scaled_car.get_width() * scale_ratio),
                                                     int(scaled_car.get_height() * scale_ratio)))

    surface.blit(scaled_car, (int((settings.internal_res_x / 2) - (scaled_car.get_width() / 2)),
                              int(height_on_screen - (scaled_car.get_height() / 2))))

    pygame.transform.scale(surface, screen.get_size(), scaled_surface)
    screen.blit(scaled_surface, (0, 0))


if __name__ == '__main__':
    main()


def __main__():
    main()
