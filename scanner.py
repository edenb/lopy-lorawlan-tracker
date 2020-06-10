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

        # If more than one network, order the list by RSSI (strongest first)
        if len(self.nets) > 1:
            sorted(self.nets, key = self.__byRssi_key)

        # Flash file storage not used because it is slow
        #self.storeNets(self.convertNetList(self.nets))
        #print(self.readNets())
        return self.nets

    # Convert from list of named tuples to list of dictionaries
    # ssid', 'bssid', 'sec', 'channel', 'rssi'
    def convertNetList(self, tupleNetList):
        dictNetList = []
        for tupleNet in tupleNetList:
            dictNet = {
                "ssid":tupleNet.ssid,
                "bssid":tupleNet.bssid,
                "sec":tupleNet.sec,
                "channel":tupleNet.channel,
                "rssi":tupleNet.rssi
            }
            dictNetList.append(dictNet)
        return dictNetList

    def writeLongList(self, name, longVars, maxLen):
        i = 0
        while i < len(longVars) and i < maxLen:
            pycom.nvs_set(name+str(i)+'l', struct.unpack(">I", longVars[i][-4:])[0])
            pycom.nvs_set(name+str(i)+'m', struct.unpack(">H", longVars[i][0:2])[0])
            i = i + 1
        try:
            pycom.nvs_erase(name+str(i)+'l')
            pycom.nvs_erase(name+str(i)+'m')
        except:
            return
        else:
            return

    def readLongList(self, name):
        longVars = []
        i = 0
        while True:
            try:
                lsb = pycom.nvs_get(name+str(i)+'l')
                msb = pycom.nvs_get(name+str(i)+'m')
            except:
                break
            else:
                longVars.append(struct.pack(">HI", msb, lsb))
                i = i + 1
        return longVars

    def writeStore(self):
        macList = []
        i = 0
        while i < len(self.nets):
            macList.append(self.nets[i].bssid)
            i = i + 1
        self.writeLongList('net', macList, 10)
        return

    def readStore(self):
        macList = self.readLongList('net')

        self.storedNets = []
        for mac in macList:
            self.storedNets.append(self.net(ssid='', bssid=mac, sec=0, channel=1, rssi=-100))
        return self.storedNets

    def storeNets(self, nets):
        f = open('data.txt', 'w+')
        for net in nets:
            f.write(repr(net) + '\n')
        f.close()

    def readNets(self):
        dictNetList = []
        f = open('data.txt')
        nets = f.readlines()
        for net in nets:
            dictNetList.append(eval(net))
        f.close()
        return dictNetList

    def createMessage(self):
        message = bytearray()
        i = 0
        while i < len(self.nets) and i < 3:
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
