################################################################################
'''

'''
################################################################################
import sys
import time, threading
from enum import Enum
import RPi.GPIO as GPIO

from const import *

class Blocker():

    def __init__(self):
        self.position = Position.DOWN

    def block(self):
        print("Blocker coming up...")
        self.position = Position.MOVING

        GPIO.output(MOTOR1A, GPIO.HIGH)
        GPIO.output(MOTOR1B, GPIO.LOW)
        GPIO.output(MOTOR1E, GPIO.HIGH)
        time.sleep(2)

        GPIO.output(MOTOR1E, GPIO.LOW)
        self.position = Position.UP
        print("Spot is now blocked")

    def lower(self):
        print("Blocker lowering...")
        self.position = Position.MOVING
        GPIO.output(MOTOR1A, GPIO.LOW)
        GPIO.output(MOTOR1B, GPIO.HIGH)
        GPIO.output(MOTOR1E, GPIO.HIGH)
        time.sleep(2)

        GPIO.output(MOTOR1E, GPIO.LOW)
        self.position = Position.DOWN
        print("Blocker is now lowered")

class Position(Enum):
    DOWN = 0
    MOVING = 1
    UP = 2
