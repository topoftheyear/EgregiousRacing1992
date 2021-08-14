import configparser

from utils.helpers import string_to_pygame_key
from utils.singleton import Singleton


class Settings(metaclass=Singleton):
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('settings.ini')

        # Video
        video = self.config['Video']
        self.res_x = int(video['ResX'])
        self.res_y = int(video['ResY'])

        # Quality
        quality = self.config['Quality']
        self.quality = float(quality['Quality'])
        self.internal_res_x = int(quality['InternalResX'])
        self.internal_res_y = int(quality['InternalResY'])
        self.view_distance = 800
        self.fps_cap = int(quality['FPSCap'])

        # Controls
        controls = self.config['Controls']
        self.mouse_sensitivity = float(controls['MouseSensitivity'])
        self.accelerate = string_to_pygame_key(controls['Accelerate'])
        self.decelerate = string_to_pygame_key(controls['Decelerate'])
        self.rotate_left = string_to_pygame_key(controls['RotateLeft'])
        self.rotate_right = string_to_pygame_key(controls['RotateRight'])
        self.handbrake = string_to_pygame_key(controls['Handbrake'])
        self.reset_camera = string_to_pygame_key(controls['ResetCamera'])

        # Derived settings
        self.res_width_ratio = self.res_x / self.internal_res_x
        self.res_height_ratio = self.res_y / self.internal_res_y

        # Other useful settings
        self.delta_time = 0

    def save(self):
        with open('settings.ini', 'w') as configfile:
            self.config.write(configfile)
