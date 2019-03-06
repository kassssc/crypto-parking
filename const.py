################################################################################
'''
Crypto Parking: Automated bitcoin parking lot
File name: const.py
Author(s): Kass Chupongstimun, kchupong@ucsd.edu
           John So,
'''
################################################################################

# These will be set by configuration file
ADMIN_EMAIL = ""
FREE_PARKING_LIMIT = 0      # seconds
PAYMENT_LIMIT = 0           # seconds
PARKING_RATE = 0
BITCOIN_ADDR = None

# constants for the application
BITCOIN_BASE_API = 'https://blockchain.info/rawaddr/'
EXCHANGE_RATE_API = 'https://www.bitstamp.net/api/ticker/'
BUFFER_LEN = 50

# GPIO PIN SPECIFICATIONS
MOTOR1A = 15
MOTOR1B = 13
MOTOR1E = 11

PIN_PROXIMITY_SENSOR = 7
PIN_OBSTRUCTION_SENSOR = 36

# COLORS FOR GUI
COLOR_BG = "#202020"
COLOR_FG = "#F2F2F2"
