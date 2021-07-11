import math
import sys
import time

import ctypes
import cv2
import pygame
import pygame.gfxdraw

from common.point import Point
from common.settings import Settings
from utils.helpers import *

pygame.init()
settings = Settings()

resolution_width_ratio = settings.res_x / settings.internal_res_x
resolution_height_ratio = settings.res_y / settings.internal_res_y

flags = pygame.DOUBLEBUF
screen = pygame.display.set_mode((settings.res_x, settings.res_y), flags)
pygame.display.set_caption("VoxelSpace")

surface = pygame.Surface((settings.internal_res_x, settings.internal_res_y))
scaled_surface = pygame.Surface(screen.get_size())

clock = pygame.time.Clock()

heightmap = cv2.imread('img/1H.png', 0)
colormap = cv2.imread('img/1C.png', -1)
colormap = cv2.cvtColor(colormap, cv2.COLOR_BGR2RGB)


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


def main():
    quality = settings.start_quality

    current_position = Point(0, 0)
    speed = 4
    moving_forward = False
    moving_backward = False

    current_rotation = 0
    rotating_right = False
    rotating_left = False

    current_height = 50
    moving_up = False
    moving_down = False

    horizon = 120
    scale_height = 240

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
                if event.key == settings.rotate_right:
                    rotating_right = True
                if event.key == settings.rotate_left:
                    rotating_left = True
                if event.key == settings.move_forward:
                    moving_forward = True
                if event.key == settings.move_backward:
                    moving_backward = True

                if event.key == settings.move_up:
                    moving_up = True
                if event.key == settings.move_down:
                    moving_down = True

                if event.key == pygame.K_EQUALS:
                    quality -= settings.quality_chunks
                if event.key == pygame.K_MINUS:
                    quality += settings.quality_chunks

                if event.key == pygame.K_ESCAPE:
                    pygame.display.quit()
                    sys.exit()

            if event.type == pygame.KEYUP:
                if event.key == settings.rotate_right:
                    rotating_right = False
                if event.key == settings.rotate_left:
                    rotating_left = False
                if event.key == settings.move_forward:
                    moving_forward = False
                if event.key == settings.move_backward:
                    moving_backward = False

                if event.key == settings.move_up:
                    moving_up = False
                if event.key == settings.move_down:
                    moving_down = False

        quality = max(quality, 0)

        if rotating_right:
            current_rotation -= settings.camera_rotation_speed
        if rotating_left:
            current_rotation += settings.camera_rotation_speed
        current_rotation %= 2 * math.pi

        if moving_forward:
            current_position.move(speed, current_rotation)
        if moving_backward:
            current_position.move(-speed, current_rotation)

        if moving_up:
            current_height += speed
        if moving_down:
            current_height -= speed

        current_position.x = min(current_position.x % 1024, 1023)
        current_position.y = min(current_position.y % 1024, 1023)

        current_height = max(current_height, heightmap[math.floor(current_position.x), math.floor(current_position.y)] + 1)
        current_height = min(current_height, 1000)

        # Set per-frame struct variables
        ls.currentX = current_position.x
        ls.currentY = current_position.y
        ls.rotation = current_rotation
        ls.height = current_height
        ls.horizon = horizon / resolution_width_ratio
        ls.scaleHeight = scale_height / resolution_height_ratio
        ls.distance = settings.view_distance
        ls.quality = quality

        render()

        pygame.display.update()
        clock.tick(30)

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

    pygame.transform.scale(surface, screen.get_size(), scaled_surface)
    screen.blit(scaled_surface, (0, 0))


if __name__ == '__main__':
    main()


def __main__():
    main()
