import configparser

from utils.helpers import string_to_pygame_key
from utils.singleton import Singleton


class Settings(metaclass=Singleton):
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('settings.ini')

        # Video
        self.res_x = int(self.config['Video']['ResX'])
        self.res_y = int(self.config['Video']['ResY'])

        # Quality
        self.start_quality = float(self.config['Quality']['StartQuality'])
        self.quality_chunks = float(self.config['Quality']['QualityChunks'])
        self.internal_res_x = int(self.config['Quality']['InternalResX'])
        self.internal_res_y = int(self.config['Quality']['InternalResY'])
        self.view_distance = int(self.config['Quality']['ViewDistance'])

        # Controls
        self.camera_rotation_speed = float(self.config['Controls']['CameraRotationSpeed'])
        self.move_forward = string_to_pygame_key(self.config['Controls']['MoveForward'])
        self.move_backward = string_to_pygame_key(self.config['Controls']['MoveBackward'])
        self.rotate_left = string_to_pygame_key(self.config['Controls']['RotateLeft'])
        self.rotate_right = string_to_pygame_key(self.config['Controls']['RotateRight'])
        self.move_up = string_to_pygame_key(self.config['Controls']['MoveUp'])
        self.move_down = string_to_pygame_key(self.config['Controls']['MoveDown'])

    def save(self):
        with open('settings.ini', 'w') as configfile:
            self.config.write(configfile)
