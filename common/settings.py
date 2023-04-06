import configparser

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
        self.fps_cap = 30

        # Controls
        controls = self.config['Controls']
        self.mouse_sensitivity = float(controls['MouseSensitivity'])
        self.accelerate = int(controls['Accelerate'])
        self.decelerate = int(controls['Decelerate'])
        self.rotate_left = int(controls['RotateLeft'])
        self.rotate_right = int(controls['RotateRight'])
        self.handbrake = int(controls['Handbrake'])
        self.reset_camera = int(controls['ResetCamera'])

        # Derived settings
        self.res_width_ratio = None
        self.res_height_ratio = None

        # Other useful settings
        self.delta_time = 0

        self.recalculate()

    def recalculate(self):
        # Derived settings
        self.res_width_ratio = self.res_x / self.internal_res_x
        self.res_height_ratio = self.res_y / self.internal_res_y

    def default(self):
        # Video
        self.res_x = 1280
        self.res_y = 720

        # Quality
        self.quality = 0.0
        self.internal_res_x = 320
        self.internal_res_y = 180
        self.view_distance = 800
        self.fps_cap = 30

        # Controls
        self.mouse_sensitivity = 0.15
        self.accelerate = 119
        self.decelerate = 115
        self.rotate_left = 97
        self.rotate_right = 100
        self.handbrake = 32
        self.reset_camera = 99

        self.recalculate()

    def save(self):
        # Video
        video = self.config['Video']
        video['ResX'] = str(self.res_x)
        video['ResY'] = str(self.res_y)

        # Quality
        quality = self.config['Quality']
        quality['Quality'] = str(self.quality)
        quality['InternalResX'] = str(self.internal_res_x)
        quality['InternalResY'] = str(self.internal_res_y)

        # Controls
        controls = self.config['Controls']
        controls['MouseSensitivity'] = str(self.mouse_sensitivity)
        controls['Accelerate'] = str(self.accelerate)
        controls['Decelerate'] = str(self.decelerate)
        controls['RotateLeft'] = str(self.rotate_left)
        controls['RotateRight'] = str(self.rotate_right)
        controls['Handbrake'] = str(self.handbrake)
        controls['ResetCamera'] = str(self.reset_camera)

        self.recalculate()

        with open('settings.ini', 'w') as configfile:
            self.config.write(configfile)
