################################################################################
'''

'''
################################################################################

import sys
import time, threading
from enum import Enum
# import RPi.GPIO as GPIO

from const import *

class Blocker():

	def __init__(self):
		self.position = Position.DOWN

	def block(self):
		print("Blocker coming up...")
		self.position = Position.MOVING
		time.sleep(5)
		self.position = Position.UP
		print("Spot is now blocked")

	def lower(self):
		print("Blocker lowering...")
		self.position = Position.MOVING
		time.sleep(5)
		self.position = Position.DOWN
		print("Blocker is now lowered")

class Position(Enum):
	DOWN = 0
	MOVING = 1
	UP = 2