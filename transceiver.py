from network import LoRa
import socket
import binascii
import machine
import pycom
import time
import machine

class Transceiver:

    def __init__(self, app_eui = 0, app_key = 0, dev_addr = 0, nwk_swkey = 0, app_swkey = 0, dataRate = 0, adr = False, useSavedState = True):
        self.app_eui = app_eui
        self.app_key = app_key
        self.dev_addr = dev_addr
        self.nwk_swkey = nwk_swkey
        self.app_swkey = app_swkey
        self.dataRate = dataRate
        self.adr = adr
        self.useSavedState = useSavedState

        # Initialize LoRa in LORAWAN mode
        self.lora = LoRa(mode=LoRa.LORAWAN, region=LoRa.EU868, power_mode=LoRa.TX_ONLY, adr=self.adr)
        # Restore LoRa state from memory (join state, frame counter)
        if self.useSavedState:
            self.lora.nvram_restore()
        else:
            self.lora.nvram_erase()
        # Only (re)join if not joined before
        if not self.lora.has_joined():
            if self.app_eui != 0 and self.app_key != 0:
                # join a network using OTAA (Over the Air Activation). Start with sf12
                self.lora.join(activation=LoRa.OTAA, auth=(self.app_eui, self.app_key), dr=0, timeout=0)
            elif self.dev_addr != 0 and self.nwk_swkey != 0 and self.app_swkey != 0:
                # join a network using ABP (Authentication By Personalization)
                self.lora.join(activation=LoRa.ABP, auth=(self.dev_addr, self.nwk_swkey, self.app_swkey))
            else:
                print("Invalid ABP or OTAA keys")
                return
            # wait until the module has joined the network (ToDo: timeout to prevent indefinite loop)
            while not self.lora.has_joined():
                time.sleep(2.5)
                print('.', end='')
        return

    def transmit(self, payload):
        self.lora.set_battery_level(self.__getLoraBattLevel())
        # create a LoRa socket
        self.s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
        # set the LoRaWAN data rate
        self.s.setsockopt(socket.SOL_LORA, socket.SO_DR, self.dataRate)
        # selecting non-confirmed type of messages
        self.s.setsockopt(socket.SOL_LORA, socket.SO_CONFIRMED, False)
        # make the socket blocking
        # (waits for the data to be sent and for the 2 receive windows to expire)
        self.s.setblocking(True)
        # select port
        self.s.bind(1)
        # Send the LoRa message
        self.s.send(payload)
        # make the socket non-blocking
        # (because if there's no data received it will block forever...)
        self.s.setblocking(False)
        # get any data received (if any...)
        self.receivePayload = self.s.recv(64)
        #print("Store LoRa state in memory")
        self.lora.nvram_save()
        return

    def receive(self):
        return self.receivePayload

    def getMac(self):
        return binascii.hexlify(self.lora.mac()).upper().decode('utf-8')

    def stats(self):
        return self.lora.stats()

    def __getLoraBattLevel(self):
        adc = machine.ADC()
        battReg = adc.channel(pin='P16', attn=1)
        #print('Battery voltage:', battReg() * 3 * 1.334 / 4095)
        loraBattLevel = int(battReg() / 14.9)
        if loraBattLevel > 254:
            loraBattLevel = 0
        battVoltage = battReg() * 3 * 1.334 / 4095
        #print("Battery level: %d (%f V)" % (loraBattLevel, battVoltage))
        return loraBattLevel
