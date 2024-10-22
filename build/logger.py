import logging

class MyLogger(logging.Logger):

    def __init__(self, name, level = 0):
        super().__init__(name, level)
        self.warning = ""

    def warning(self, msg, *args, **kargs):
        return super().warning(msg, *args, **kargs)