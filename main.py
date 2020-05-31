import binascii
import pycom
import struct
import machine
import config
from logger import Logger
from led import Led
from startup import startup
from startup import test
from scanner import Scanner
from transceiver import Transceiver

#
# Global variables
#

# Create OTAA authentication parameters
app_eui = binascii.unhexlify(config.APP_EUI)
app_key = binascii.unhexlify(config.APP_KEY)

# Create ABP authentication parameters
dev_addr = struct.unpack(">l", binascii.unhexlify(config.DEV_ADDR))[0]
nwk_swkey = binascii.unhexlify(config.NWK_SWKEY)
app_swkey = binascii.unhexlify(config.APP_SWKEY)

#
# Program start
#

# Create logger for debug purposes
logger = Logger()

# Initialize RGB LED (off)
led = Led()

# machine.PWRON_RESET, machine.HARD_RESET, machine.WDT_RESET, machine.DEEPSLEEP_RESET, machine.SOFT_RESET, machine.BROWN_OUT_RESET
resetCause = machine.reset_cause()
# Startup procedure only cold boot
if (resetCause == machine.PWRON_RESET) or (resetCause == machine.WDT_RESET):
    logger.out(logger.INFO, "Initial startup.")
    startup()
    if config.UNITTESTING:
        logger.out(logger.INFO, "Unittest started.")
        test()

# Flash LED to mark start
led.flash(led.GREEN, 100, 100)

# Initialize access point scanner
scanner = Scanner()
# Scan for access points
logger.out(logger.INFO, "AP scan started.")
nets = scanner.get()
logger.out(logger.INFO, "AP scan finished. " + str(len(nets)) + " network(s) found.")

# Check for stationary or moving
prevNets = scanner.readStore()
diff = scanner.netDiff(nets, prevNets)
logger.out(logger.INFO, "Difference between scans: " + str(diff))

# Save scan result in non-volatile RAM
scanner.writeStore()

logger.out(logger.INFO, "LoRa join started.")
led.on(led.RED, 10)
# ABP join
#lora = Transceiver(dev_addr = dev_addr, nwk_swkey = nwk_swkey, app_swkey = app_swkey, dataRate = 0, adr = True, useSavedState = useSavedState)
# OTAA join
lora = Transceiver(app_eui = app_eui, app_key = app_key, dataRate = 0, adr = True, useSavedState = True)
led.off()
logger.out(logger.INFO, "LoRa join finished. Dev EUI: " +  lora.getMac())

# Create an empty LoRa message
sMessage = bytearray()
# Add type to the LoRa message
sMessage.append(0x00)
# Add list with bssid and rssi to the LoRa message
sMessage = sMessage + scanner.createMessage()

logger.out(logger.INFO, "LoRa transmit start. Message: " + str(binascii.hexlify(sMessage).upper().decode('utf-8')))
led.on(led.BLUE, 10)
lora.transmit(sMessage)
led.off()
logger.out(logger.INFO, "LoRa transmit finished.")

data = lora.receive()
if len(data) > 0:
    logger.out(logger.INFO, "LoRa message received. Message: " + str(binascii.hexlify(data).upper().decode('utf-8')))

logger.out(logger.INFO, "LoRa stats: " + str(lora.stats()))

logger.out(logger.INFO, "Deep sleep started.")
machine.deepsleep(60000)
