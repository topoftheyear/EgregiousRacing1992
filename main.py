import math
import random
import sys
import time

import ctypes
import cv2
import pygame
import pygame.gfxdraw

from common.camera import Camera
from common.settings import Settings
from common.sprite import Sprite
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

worfs = list()
for _ in range(12):
    worfs.append(Sprite('img/worf.png', Point(random.randint(0, settings.internal_res_x),
                                              random.randint(0, settings.internal_res_y))))


def main():
    quality = settings.start_quality

    camera = Camera()

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

        camera.handle_input(events, heightmap)

        quality = max(quality, 0)

        # Set per-frame struct variables
        ls.currentX = camera.position.x
        ls.currentY = camera.position.y
        ls.rotation = camera.rotation
        ls.height = camera.height
        ls.horizon = camera.horizon / settings.res_width_ratio
        ls.scaleHeight = camera.scale_height / settings.res_height_ratio
        ls.distance = settings.view_distance
        ls.quality = quality

        render()

        pygame.display.update()
        clock.tick(settings.fps_cap)

        print(1 / (time.time() - start))


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

    for worf in worfs:
        surface.blit(worf.image, worf.position.tuple())
    pygame.transform.scale(surface, screen.get_size(), scaled_surface)
    screen.blit(scaled_surface, (0, 0))


if __name__ == '__main__':
    main()


def __main__():
    main()
