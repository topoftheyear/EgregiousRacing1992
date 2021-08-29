import math

from common.settings import Settings
from common.enums import CoinAnimStates
from common.game_object import GameObject
from common.spritesheet import Spritesheet


class Coin(GameObject):
    def __init__(self, position, height=0):
        super().__init__(position, height)

        states = dict()
        states[CoinAnimStates.default] = [
            (0, 0, 64, 64), (64, 0, 64, 64), (128, 0, 64, 64),
            (0, 64, 64, 64), (64, 64, 64, 64), (128, 64, 64, 64),
            (0, 128, 64, 64), (64, 128, 64, 64)
        ]

        self.sprite_sheet = Spritesheet('img/coin.png', states, 8, random_start_frame=True)

        self.z_velocity = 0

        self.settings = Settings()

    def update(self, heightmap, camera):
        # Gravity if not touching the ground
        if self.height > heightmap[math.floor(self.position.x), math.floor(self.position.y)]:
            self.z_velocity += -9.81 * self.settings.delta_time
        # Reset velocity to 0 if velocity is negative
        else:
            if self.z_velocity < 0:
                self.z_velocity = 0

        self.height += self.z_velocity

        self.sprite_sheet.update()

        if self.height < heightmap[self.position.x, self.position.y]:
            self.height = heightmap[self.position.x, self.position.y]
