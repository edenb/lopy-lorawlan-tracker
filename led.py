import pycom
import machine
import utime
import _thread

class Led:
    OFF = 0x000000
    RED = 0xFF0000
    GREEN = 0x00FF00
    BLUE = 0x0000FF
    WHITE = 0xFFFFFF

    def __init__(self):
        # Disable heartbeat LED
        if pycom.heartbeat() == True:
            pycom.heartbeat(False)
        self.off()
        # Initialize expansion board LED (off)
        machine.Pin('P9', mode=machine.Pin.OUT).value(1)

    def on(self, color = WHITE, brightness = 100):
        if brightness > 100:
            brightness = 100
        elif brightness < 0:
            brightness = 0
        dimmedRed = int(((color & 0xFF0000)>>16) * brightness / 100)
        dimmedGreen = int(((color & 0x00FF00)>>8) * brightness / 100)
        dimmedBlue = int((color & 0x0000FF) * brightness / 100)
        dimmedColor = (dimmedRed<<16) | (dimmedGreen<<8) | dimmedBlue
        pycom.rgbled(dimmedColor)

    def off(self):
        pycom.rgbled(self.OFF)

    def flash(self, color = WHITE, brightness = 100, duration = 100):
        _thread.start_new_thread(self.__flashLED, (color, brightness, duration))

    def __flashLED(self, color, brightness, duration):
        self.on(color, brightness)
        utime.sleep_ms(duration)
        self.off()
