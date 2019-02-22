################################################################################
'''
Crypto Parking: Automated bitcoin parking lot
File name: const.py
Description:
Author(s): Kass Chupongstimun, kchupong@ucsd.edu
           John So,
'''
################################################################################

FREE_PARKING_LIMIT = 5		# seconds
PAYMENT_LIMIT = 15				# seconds
PARKING_RATE = 0.1
#PARKING_RATE = 0.00077		# btc / hour

PIN_PROXIMITY_SENSOR = 0

COLOR_BG = "#202020"
COLOR_FG = "#F2F2F2"

from enum import Enum
class State(Enum):
	EMPTY = 0
	FREE_PARKING = 1
	PARKED = 2
	AWAIT_PAYMENT = 3
	PAID = 4
	BLOCKER_MOVING = 5