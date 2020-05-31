from machine import Timer

class Logger:
    INFO = 0
    WARNING = 1
    ERROR = 2

    def __init__(self):
        self.chrono = Timer.Chrono()
        self.chrono.start()

    def out(self, level = INFO, text = ""):
        chronoStr = "{:6.3f}".format(self.chrono.read())
        levelStr = ["Info   ", "Warning", "Error  "]
        print(chronoStr + " " + levelStr[level] + " " + text)
