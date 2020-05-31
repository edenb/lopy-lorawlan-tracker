import sys
import os
import binascii
from scanner import Scanner
from ucollections import namedtuple
from time import sleep
from led import Led

def startup():
    iPlatform = sys.platform
    iImplementation = sys.implementation.name
    iImplementationVersion = os.uname().version
    iPythonVersion = sys.version
    iFirmwareVersion = os.uname().release

    print("*************************************************************")
    print("Platform:               ", iPlatform)
    print("Python version:         ", iPythonVersion)
    print("Implementation:         ", iImplementation)
    print("Implementation version: ", iImplementationVersion)
    print("Firmware version:       ", iFirmwareVersion)
    print("*************************************************************")
    return

def test():
    print("*** Testing: LED ***")
    led = Led()
    print("Red 100%")
    led.on(led.RED, 100)
    sleep(0.5)
    print("Red 75%")
    led.on(led.RED, 75)
    sleep(0.5)
    print("Red 50%")
    led.on(led.RED, 50)
    sleep(0.5)
    print("Red 25%")
    led.on(led.RED, 25)
    sleep(0.5)

    print("White 100%")
    led.on(led.WHITE, 100)
    sleep(0.5)
    print("White 75%")
    led.on(led.WHITE, 75)
    sleep(0.5)
    print("White 50%")
    led.on(led.WHITE, 50)
    sleep(0.5)
    print("White 25%")
    led.on(led.WHITE, 25)
    sleep(0.5)

    led.off()

    print("*** Testing: WiFi scanner ***")
    # Initialize the scanner
    scanner = Scanner()

    scanner.get(True, None)
    messageStr = bytearr2string(scanner.createMessage())
    print("Test scanning (no networks)     => len =  {}, message = {}".format(scanner.netsCnt, messageStr))

    nets = []
    nets.append(scanner.net(ssid='ssid', bssid=b'\xA1\xA2\xA3\xA4\xA5\xA6', sec=0, channel=13, rssi=-100))
    scanner.get(True, nets)
    messageStr = bytearr2string(scanner.createMessage())
    print("Test scanning (one network)     => len =  {}, message = {}".format(scanner.netsCnt, messageStr))

    nets = []
    nets.append(scanner.net(ssid='ssid', bssid=b'\xA1\xA2\xA3\xA4\xA5\xA6', sec=0, channel=13, rssi=-100))
    nets.append(scanner.net(ssid='ssid', bssid=b'\xB1\xB2\xB3\xB4\xB5\xB6', sec=0, channel=13, rssi=-100))
    scanner.get(True, nets)
    messageStr = bytearr2string(scanner.createMessage())
    print("Test scanning (two networks)    => len =  {}, message = {}".format(scanner.netsCnt, messageStr))

    nets = []
    nets.append(scanner.net(ssid='ssid', bssid=b'\xA1\xA2\xA3\xA4\xA5\xA6', sec=0, channel=13, rssi=-100))
    nets.append(scanner.net(ssid='ssid', bssid=b'\xB1\xB2\xB3\xB4\xB5\xB6', sec=0, channel=13, rssi=-100))
    nets.append(scanner.net(ssid='ssid', bssid=b'\xC1\xC2\xC3\xC4\xC5\xC6', sec=0, channel=13, rssi=-100))
    scanner.get(True, nets)
    messageStr = bytearr2string(scanner.createMessage())
    print("Test scanning (three networks)  => len =  {}, message = {}".format(scanner.netsCnt, messageStr))

    nets = []
    nets.append(scanner.net(ssid='ssid', bssid=b'\xA1\xA2\xA3\xA4\xA5\xA6', sec=0, channel=13, rssi=-100))
    nets.append(scanner.net(ssid='ssid', bssid=b'\xB1\xB2\xB3\xB4\xB5\xB6', sec=0, channel=13, rssi=-100))
    nets.append(scanner.net(ssid='ssid', bssid=b'\xC1\xC2\xC3\xC4\xC5\xC6', sec=0, channel=13, rssi=-100))
    nets.append(scanner.net(ssid='ssid', bssid=b'\xD1\xD2\xD3\xD4\xD5\xD6', sec=0, channel=13, rssi=-100))
    scanner.get(True, nets)
    messageStr = bytearr2string(scanner.createMessage())
    print("Test scanning (four networks)   => len =  {}, message = {}".format(scanner.netsCnt, messageStr))

    nets = []
    nets.append(scanner.net(ssid='ssid', bssid=b'\xA1\xA2\xA3\xA4\xA5\xA6', sec=0, channel=13, rssi=-100))
    nets.append(scanner.net(ssid='ssid', bssid=b'\xB1\xB2\xB3\xB4\xB5\xB6', sec=0, channel=13, rssi=-100))
    nets.append(scanner.net(ssid='ssid', bssid=b'\xC1\xC2\xC3\xC4\xC5\xC6', sec=0, channel=13, rssi=-100))
    nets.append(scanner.net(ssid='ssid', bssid=b'\xD1\xD2\xD3\xD4\xD5\xD6', sec=0, channel=13, rssi=-100))
    nets.append(scanner.net(ssid='ssid', bssid=b'\xE1\xE2\xE3\xE4\xE5\xE6', sec=0, channel=13, rssi=-100))
    nets.append(scanner.net(ssid='ssid', bssid=b'\xF1\xF2\xF3\xF4\xF5\xF6', sec=0, channel=13, rssi=-100))
    nets.append(scanner.net(ssid='ssid', bssid=b'\xC1\xC2\xC3\xC4\xC5\xC6', sec=0, channel=13, rssi=-100))
    nets.append(scanner.net(ssid='ssid', bssid=b'\x01\x02\x03\x04\x05\x06', sec=0, channel=13, rssi=-100))
    nets.append(scanner.net(ssid='ssid', bssid=b'\x11\x12\x13\x14\x15\x16', sec=0, channel=13, rssi=-100))
    nets.append(scanner.net(ssid='ssid', bssid=b'\x21\x22\x23\x24\x25\x26', sec=0, channel=13, rssi=-100))
    scanner.get(True, nets)
    messageStr = bytearr2string(scanner.createMessage())
    print("Test scanning (ten networks)    => len = {}, message = {}".format(scanner.netsCnt, messageStr))

    print("*** Finish unit testing ***")
    return

def arr2version(arrVersion):
    version = ""
    i = 0
    while i < len(arrVersion):
        version += str(arrVersion[i])
        i += 1
        if i < len(arrVersion):
            version += "."
    return version

def bytearr2string(arr):
    arrStr = binascii.hexlify(arr).upper().decode('utf-8')
    return arrStr
