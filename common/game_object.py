from common.point import Point


class GameObject:
    id_counter = 0

    def __init__(self, position=Point(), height=50):
        self.id = GameObject.id_counter
        GameObject.id_counter += 1

        self.position = position
        self.height = height
        self.sprite_sheet = None

    def update(self, heightmap, camera):
        pass
