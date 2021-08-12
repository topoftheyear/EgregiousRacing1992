from common.enums import CoinAnimStates
from common.game_object import GameObject
from common.spritesheet import Spritesheet


class Coin(GameObject):
    def __init__(self, position, height=0):
        super(Coin, self).__init__(position, height)

        states = dict()
        states[CoinAnimStates.default] = [
            (0, 0, 64, 64), (64, 0, 64, 64), (128, 0, 64, 64),
            (0, 64, 64, 64), (64, 64, 64, 64), (128, 64, 64, 64),
            (0, 128, 64, 64), (64, 128, 64, 64)
        ]

        self.sprite_sheet = Spritesheet('img/coin.png', states, 8)

    def update(self, heightmap, camera):
        self.sprite_sheet.update()

        if self.height < heightmap[self.position.x, self.position.y]:
            self.height = heightmap[self.position.x, self.position.y]
