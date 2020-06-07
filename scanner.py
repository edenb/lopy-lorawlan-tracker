from network import WLAN
import pycom
import struct
from ucollections import namedtuple

class Scanner:

    def __init__(self):
        # Initialize wlan
        self.wlan = WLAN(mode=WLAN.STA)
        # Internal (WLAN.INT_ANT) or external (WLAN.EXT_ANT) antenna
        self.wlan.antenna(WLAN.INT_ANT)
        self.nets = []
        self.netsCnt = 0
        # Define the named tuple that contains the WiFi access point information
        self.net = namedtuple('net', ('ssid', 'bssid', 'sec', 'channel', 'rssi'))

    def get(self, testNetworksValid = False, testNetworks = []):
        if testNetworksValid:
            self.nets = testNetworks
        else:
            # Scan available networks
            self.nets = self.wlan.scan(type = WLAN.SCAN_PASSIVE, scantime = 120)
            # Switch WiFi off
            self.wlan.deinit()

        # Nets is defined None if no networks are found
        if self.nets is None:
            self.nets = []
            self.netsCnt = 0
        else:
            self.netsCnt = len(self.nets)

        # If more than one network, order the list by RSSI (strongest first)
        if self.netsCnt > 1:
            sorted(self.nets, key = self.__byRssi_key)

        return self.nets

    def writeStore(self):
        pycom.nvs_set('netsCnt', self.netsCnt)

        i = 0
        while (i < 10):
            if (i < self.netsCnt):
            #print("Store net 1:", binascii.hexlify(nets[i].bssid).upper().decode('utf-8'))
                lsb = struct.unpack(">I", self.nets[i].bssid[-4:])[0]
                msb = struct.unpack(">H", self.nets[i].bssid[0:2])[0]
            else:
                lsb = 0
                msb = 0
            if (i == 0):
                pycom.nvs_set('net1lsb', lsb)
                pycom.nvs_set('net1msb', msb)
            elif (i == 1):
                pycom.nvs_set('net2lsb', lsb)
                pycom.nvs_set('net2msb', msb)
            elif (i == 2):
                pycom.nvs_set('net3lsb', lsb)
                pycom.nvs_set('net3msb', msb)
            elif (i == 3):
                pycom.nvs_set('net4lsb', lsb)
                pycom.nvs_set('net4msb', msb)
            elif (i == 4):
                pycom.nvs_set('net5lsb', lsb)
                pycom.nvs_set('net5msb', msb)
            elif (i == 5):
                pycom.nvs_set('net6lsb', lsb)
                pycom.nvs_set('net6msb', msb)
            elif (i == 6):
                pycom.nvs_set('net7lsb', lsb)
                pycom.nvs_set('net7msb', msb)
            elif (i == 7):
                pycom.nvs_set('net8lsb', lsb)
                pycom.nvs_set('net8msb', msb)
            elif (i == 8):
                pycom.nvs_set('net9lsb', lsb)
                pycom.nvs_set('net9msb', msb)
            elif (i == 9):
                pycom.nvs_set('net10lsb', lsb)
                pycom.nvs_set('net10msb', msb)
            i = i + 1
        return

    def readStore(self):
        self.storedNetsCnt = pycom.nvs_get('netsCnt')
        self.storedNets = []

        i = 0
        while (i < 10):
            if (i == 0):
                lsb = pycom.nvs_get('net1lsb')
                msb = pycom.nvs_get('net1msb')
            elif (i == 1):
                lsb = pycom.nvs_get('net2lsb')
                msb = pycom.nvs_get('net2msb')
            elif (i == 2):
                lsb = pycom.nvs_get('net3lsb')
                msb = pycom.nvs_get('net3msb')
            elif (i == 3):
                lsb = pycom.nvs_get('net4lsb')
                msb = pycom.nvs_get('net4msb')
            elif (i == 4):
                lsb = pycom.nvs_get('net5lsb')
                msb = pycom.nvs_get('net5msb')
            elif (i == 5):
                lsb = pycom.nvs_get('net6lsb')
                msb = pycom.nvs_get('net6msb')
            elif (i == 6):
                lsb = pycom.nvs_get('net7lsb')
                msb = pycom.nvs_get('net7msb')
            elif (i == 7):
                lsb = pycom.nvs_get('net8lsb')
                msb = pycom.nvs_get('net8msb')
            elif (i == 8):
                lsb = pycom.nvs_get('net9lsb')
                msb = pycom.nvs_get('net9msb')
            elif (i == 9):
                lsb = pycom.nvs_get('net10lsb')
                msb = pycom.nvs_get('net10msb')

            readnet = struct.pack(">HI", msb, lsb)
            self.storedNets.append(self.net(ssid='', bssid=readnet, sec=0, channel=1, rssi=-100))
            i = i + 1
        return self.storedNets

    def createMessage(self):
        message = bytearray()
        i = 0
        while (i < self.netsCnt) and (i < 3):
            # Add BSSID to the LoRa message
            message = message + self.nets[i].bssid
            # Add RSSI (without minus) to the LoRa message
            message.append(self.nets[i].rssi * -1)
            i = i + 1
        return message

    def netDiff(self, nets1 = [], nets2 = []):
        matchCnt = 0
        # Define the named tuple that contains the result of the matching
        diffRes = namedtuple('diffRes', ('net1', 'net2', 'match', 'noMatch'))
        for net1 in nets1:
            for net2 in nets2:
                if net1.bssid == net2.bssid:
                    matchCnt = matchCnt + 1
        noMatchCnt = len(nets1) + len(nets2) - (2*matchCnt)
        return diffRes(net1=len(nets1), net2=len(nets2), match=matchCnt, noMatch=noMatchCnt)

    def __byRssi_key(self, net):
        return net.rssi
