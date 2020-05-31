from machine import UART
from os import dupterm
from network import Bluetooth
from pycom import heartbeat
from pycom import wifi_on_boot

uart = UART(0, baudrate=115200)
dupterm(uart)

if heartbeat() == True:
    heartbeat(False)

if wifi_on_boot() == True:
    wifi_on_boot(False)

bluetooth = Bluetooth()
bluetooth.deinit()
