import math
import random
import sys
import time

import pygame
import pygame.gfxdraw

from common.enums import Screens
from common.game_manager import GameManager
from common.screens.game_screen import GameScreen
from common.screens.game_end_screen import GameEndScreen
from common.screens.leaderboard_screen import LeaderboardScreen
from common.screens.main_menu_screen import MainMenuScreen
from common.screens.map_select_screen import MapSelectScreen
from common.screens.settings_screen import SettingsScreen
from common.settings import Settings
from utils.helpers import *
from utils.thread import Thread


def main():
    pygame.init()
    gm = GameManager()
    settings = Settings()

    flags = pygame.DOUBLEBUF
    screen = pygame.display.set_mode((settings.res_x, settings.res_y), flags)
    pygame.display.set_caption('Egregious Racing 1992')

    surface = pygame.Surface((settings.internal_res_x, settings.internal_res_y))
    scaled_surface = pygame.Surface(screen.get_size())

    clock = pygame.time.Clock()

    mms = MainMenuScreen()
    mms_thread = Thread(mms.load, ())
    ss = SettingsScreen()
    ss_thread = Thread(ss.load, ())
    lbs = LeaderboardScreen()
    lbs_thread = Thread(lbs.load, ())
    mss = MapSelectScreen()
    mss_thread = Thread(mss.load, ())
    gs = GameScreen()
    gs_thread = Thread(gs.load, ())
    ges = GameEndScreen()
    ges_thread = Thread(ges.load, ())
    states = {
        Screens.main_menu: {
            'screen': mms,
            'thread': mms_thread,
        },
        Screens.settings: {
            'screen': ss,
            'thread': ss_thread,
        },
        Screens.leaderboard: {
            'screen': lbs,
            'thread': lbs_thread,
        },
        Screens.map_select: {
            'screen': mss,
            'thread': mss_thread,
        },
        Screens.game: {
            'screen': gs,
            'thread': gs_thread,
        },
        Screens.game_end: {
            'screen': ges,
            'thread': ges_thread,
        }
    }

    gm.screens = states

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

        cscreen = gm.screens[gm.current_screen]['screen']
        thread = gm.screens[gm.current_screen]['thread']

        if cscreen.loaded:
            gm.unload_previous_screen()

            pygame.mouse.set_visible(cscreen.mouse_visible)
            pygame.event.set_grab(cscreen.mouse_grab)
            cscreen.update(events)
            cscreen.render(surface)
        elif not thread.started:
            thread.start()
        else:
            progress = cscreen.current_loading / cscreen.max_loading
            pygame.gfxdraw.box(
                surface,
                [surface.get_width() / 2 - 25, surface.get_height() / 2 - 5, 50, 10],
                (255, 255, 255)
            )
            pygame.gfxdraw.box(
                surface,
                [surface.get_width() / 2 - 24, surface.get_height() / 2 - 4, max(1, 48 * progress), 8],
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
