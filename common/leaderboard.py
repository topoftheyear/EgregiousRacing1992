import json
import os

from utils.helpers import get_list_of_maps
from utils.singleton import Singleton


class Leaderboard(metaclass=Singleton):
    def __init__(self):
        self.file = 'leaderboard.json'

        if not os.path.isfile(self.file):
            open(self.file, 'a').close()

        with open(self.file) as f:
            self.leaderboard = json.load(f)

        # Iterate through every map and establish a leaderboard for it if necessary
        for map_name in get_list_of_maps(False):
            if map_name not in self.leaderboard:
                self.leaderboard[map_name] = [
                    {'name': '---', 'score': 0},
                    {'name': '---', 'score': 0},
                    {'name': '---', 'score': 0},
                    {'name': '---', 'score': 0},
                    {'name': '---', 'score': 0},
                ]

        self.save()

    def save(self):
        with open(self.file, 'w') as f:
            json.dump(self.leaderboard, f)
