import math

import cv2
import numpy as np
import pygame

from common.point import Point


def heightmap_to_ctypes(arr, heightmap):
    for x in range(heightmap.shape[0]):
        for y in range(heightmap.shape[1]):
            arr[x][y] = heightmap[x, y]

    return arr


def colormap_to_ctypes(arr, colormap):
    for x in range(colormap.shape[0]):
        for y in range(colormap.shape[1]):
            for z in range(colormap.shape[2]):
                arr[x][y][z] = colormap[x, y, z]

    return arr


def point_in_triangle(pt, v1, v2, v3):
    d1 = sign(pt, v1, v2)
    d2 = sign(pt, v2, v3)
    d3 = sign(pt, v3, v1)

    has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
    has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)

    return not (has_neg and has_pos)


def sign(p1, p2, p3):
    return (p1.x - p3.x) * (p2.y - p3.y) - (p2.x - p3.x) * (p1.y - p3.y)


def distance(p1, p2):
    return math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)


def reduce(num, amount):
    if num > 0:
        return max(0, num - amount)
    elif num < 0:
        return min(0, num + amount)
    else:
        return num


def points_between(p1, p2, rounded=False):
    dist = distance(p1, p2)
    if dist == 0:
        return None

    dx = (p2.x - p1.x) / dist
    dy = (p2.y - p1.y) / dist

    point_list = list()

    for n in range(math.ceil(dist)):
        point = None
        if rounded:
            point = Point(int(p1.x + n * dx), int(p1.y + n * dy))
        else:
            point = Point(p1.x + n * dx, p1.y + n * dy)

        point.x %= 1024
        point.y %= 1024

        point_list.append(point)

    return point_list


def convert_image_to_palette(image):
    # retrieve palette
    palette = cv2.imread('img/palette.png', -1)
    palette = cv2.cvtColor(palette, cv2.COLOR_BGR2HSV)

    # convert image to hsv (hue, saturation, value)
    hsvimage = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)

    # iterate through each pixel
    for x in range(hsvimage.shape[0]):
        for y in range(hsvimage.shape[1]):
            color = hsvimage[x, y]

            # iterate through each color in palette
            closest_value = 1000000
            closest_color = color
            for z in range(palette.shape[1]):
                p_color = palette[0, z]

                # Determine value
                h = abs(float(p_color[0]) - float(color[0])) * 0.475
                s = abs(float(p_color[1]) - float(color[1])) * 0.2375
                v = abs(float(p_color[2]) - float(color[2])) * 0.2875

                value = h + s + v
                if value < closest_value:
                    closest_value = value
                    closest_color = p_color

            hsvimage[x, y] = closest_color

    # convert image back
    rgbimage = cv2.cvtColor(hsvimage, cv2.COLOR_HSV2RGB)
    return rgbimage


def string_to_pygame_key(string):
    keymap = {
        'a': pygame.K_a,
        'b': pygame.K_b,
        'c': pygame.K_c,
        'd': pygame.K_d,
        'e': pygame.K_e,
        'f': pygame.K_f,
        'g': pygame.K_g,
        'h': pygame.K_h,
        'i': pygame.K_i,
        'j': pygame.K_j,
        'k': pygame.K_k,
        'l': pygame.K_l,
        'm': pygame.K_m,
        'n': pygame.K_n,
        'o': pygame.K_o,
        'p': pygame.K_p,
        'q': pygame.K_q,
        'r': pygame.K_r,
        's': pygame.K_s,
        't': pygame.K_t,
        'u': pygame.K_u,
        'v': pygame.K_v,
        'w': pygame.K_w,
        'x': pygame.K_x,
        'y': pygame.K_y,
        'z': pygame.K_z,
        '0': pygame.K_0,
        '1': pygame.K_1,
        '2': pygame.K_2,
        '3': pygame.K_3,
        '4': pygame.K_4,
        '5': pygame.K_5,
        '6': pygame.K_6,
        '7': pygame.K_7,
        '8': pygame.K_8,
        '9': pygame.K_9,
        'space': pygame.K_SPACE,
        'lshift': pygame.K_LSHIFT,
        'lctrl': pygame.K_LCTRL,
        'tab': pygame.K_TAB,
        'lalt': pygame.K_LALT
    }

    return keymap[string]
