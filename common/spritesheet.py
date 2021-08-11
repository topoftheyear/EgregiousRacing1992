import math

import pygame

from common.settings import Settings


class Spritesheet:
    def __init__(self, filename, states, animation_speed):
        self.sheet = pygame.image.load(filename).convert_alpha()
        self.states = states
        self.current_state = list(states.keys())[0]
        self.animation_speed = animation_speed
        self.current_frame = 0
        self.settings = Settings()

    def update(self):
        self.current_frame += self.animation_speed * self.settings.delta_time
        self.current_frame %= len(self.states[self.current_state])
        
    def set_state(self, new_state):
        if new_state not in self.states.keys():
            return 1

        self.current_state = new_state
        self.current_frame = 0

    def get_image(self):
        return self.sheet.subsurface(pygame.Rect(self.states[self.current_state][int(math.floor(self.current_frame))]))
