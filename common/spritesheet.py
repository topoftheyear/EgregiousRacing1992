import math
import random

import pygame

from common.settings import Settings


class Spritesheet:
    def __init__(self, filename, states, animation_speed, random_start_frame=False):
        self.sheet = pygame.image.load(filename).convert_alpha()
        self.states = states
        self.current_state = list(states.keys())[0]
        self.animation_speed = animation_speed
        self.current_frame = 0
        if random_start_frame:
            self.current_frame = random.randint(0, len(self.states[self.current_state]))
        self.settings = Settings()

    def update(self):
        self.current_frame += self.animation_speed * self.settings.delta_time
        self.current_frame %= len(self.states[self.current_state])

    def get_image(self):
        self.current_frame %= len(self.states[self.current_state])
        return self.sheet.subsurface(pygame.Rect(self.states[self.current_state][int(math.floor(self.current_frame))]))
