import pygame


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


def sign(p1, p2, p3):
    return (p1.x - p3.x) * (p2.y - p3.y) - (p2.x - p3.x) * (p1.y - p3.y)


def point_in_triangle(pt, v1, v2, v3):
    d1 = sign(pt, v1, v2)
    d2 = sign(pt, v2, v3)
    d3 = sign(pt, v3, v1)

    has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
    has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)

    return not (has_neg and has_pos)


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
