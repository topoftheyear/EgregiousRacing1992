import math


class Point:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def move(self, distance, angle):
        self.x += distance * math.sin(angle - math.pi)
        self.y += distance * math.cos(angle - math.pi)

    def __str__(self):
        return f'X:{self.x},Y:{self.y}'
