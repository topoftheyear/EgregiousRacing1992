import threading


class Thread(threading.Thread):
    def __init__(self, func, args):
        threading.Thread.__init__(self)
        self.args = args
        self.func = func

        self.started = False

    def run(self):
        self.started = True
        self.func(*self.args)
