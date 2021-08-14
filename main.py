import math
import random
import sys
import time

import pygame
import pygame.gfxdraw

from common.game_screen import GameScreen
from common.settings import Settings
from utils.helpers import *
from utils.thread import Thread

pygame.init()
settings = Settings()

flags = pygame.DOUBLEBUF
screen = pygame.display.set_mode((settings.res_x, settings.res_y), flags)
pygame.display.set_caption('Egregious Racing 1992')

surface = pygame.Surface((settings.internal_res_x, settings.internal_res_y))
scaled_surface = pygame.Surface(screen.get_size())

clock = pygame.time.Clock()


def main():
    current_screen = GameScreen(surface, 'C1')
    loading_thread = Thread(current_screen.load, ())

    print("Starting loop")
    while 1:
        start = time.time()

        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                pygame.display.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.display.quit()
                    sys.exit()

        if current_screen.loaded:
            current_screen.update(events)
        elif not loading_thread.started:
            loading_thread.start()
        else:
            progress = current_screen.current_loading / current_screen.max_loading
            pygame.gfxdraw.box(
                surface,
                [surface.get_width() / 2 - 25, surface.get_height() / 2 - 5, 50, 10],
                (255, 255, 255)
            )
            pygame.gfxdraw.box(
                surface,
                [surface.get_width() / 2 - 24, surface.get_height() / 2 - 4, 48 * progress, 8],
                (255 * (1 - progress), 255 * progress, 0)
            )

        pygame.transform.scale(surface, screen.get_size(), scaled_surface)
        screen.blit(scaled_surface, (0, 0))

        pygame.display.update()

        # Update clock and delta time
        clock.tick(settings.fps_cap)
        settings.delta_time = clock.get_time() / 1000

        #print(1 / (time.time() - start))


if __name__ == '__main__':
    main()


def __main__():
    main()
