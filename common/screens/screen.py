class Screen:
    def __init__(self):
        self.current_loading = 0
        self.max_loading = 1
        self.loaded = False
        self.mouse_visible = True
        self.mouse_grab = False

    def load(self):
        pass

    def update(self, events):
        pass

    def render(self, surface):
        pass
