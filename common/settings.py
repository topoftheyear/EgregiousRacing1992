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
        self.start_quality = float(quality['StartQuality'])
        self.quality_chunks = float(quality['QualityChunks'])
        self.internal_res_x = int(quality['InternalResX'])
        self.internal_res_y = int(quality['InternalResY'])
        self.view_distance = int(quality['ViewDistance'])
        self.fps_cap = int(quality['FPSCap'])

        # Controls
        controls = self.config['Controls']
        self.camera_rotation_speed = float(controls['CameraRotationSpeed'])
        self.mouse_sensitivity = float(controls['MouseSensitivity'])
        self.move_forward = string_to_pygame_key(controls['MoveForward'])
        self.move_backward = string_to_pygame_key(controls['MoveBackward'])
        self.move_left = string_to_pygame_key(controls['MoveLeft'])
        self.move_right = string_to_pygame_key(controls['MoveRight'])
        self.move_up = string_to_pygame_key(controls['MoveUp'])
        self.move_down = string_to_pygame_key(controls['MoveDown'])

        # Derived settings
        self.res_width_ratio = self.res_x / self.internal_res_x
        self.res_height_ratio = self.res_y / self.internal_res_y

    def save(self):
        with open('settings.ini', 'w') as configfile:
            self.config.write(configfile)
