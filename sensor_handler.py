################################################################################
'''
Crypto Parking: Automated bitcoin parking lot
File name: main.py
Description:
Author(s): Kass Chupongstimun, kchupong@ucsd.edu
		   John So, jyso@ucsd.edu
'''
################################################################################
import threading
import numpy as np
# import RPi.GPIO as GPIO
import shared as SV
from const import *

class SensorHandler:

	def __init__(self):
		self.counter = 0
		self.stablize_counter = 0
		self.buffer = np.zeros(100)
		self.sensor_val = False

	def init_interrupts(self):
		GPIO.add_event_detect(
			PIN_PROXIMITY_SENSOR,
			GPIO.BOTH,
			callback=self.wake_detect	# threaded callback
		)

	def wake_detect(self):
		'''
			Poll the proximity sensor and preprocess the data
			Prolly use moving average, gather around 250ms of data
			Return a single 1 or 0 to finalize whether there is something on the sensor
			Go back to sleep if the readings stablize
		'''

		GPIO.remove_event_detect(PIN_PROXIMITY_SENSOR)	# disable interrupts
		self.read_sensor()
			# poll sensor and process raw input
			# SV.SENSOR_SLEEP = 1 if input stablizes
			# every once in a while, set SV.SENSOR_DETECTED to update main thread

	def read_sensor(self):
		# sensor_in = read from gpio
		self.buffer[self.counter] = 100 if sensor_in else 0
		self.counter = (self.counter + 1) % 100

		if self.counter == 0:
			sensor_val = np.mean(self.buffer) > 50
			if SV.sensor_detected == sensor_val:
				self.stablize_counter += 1
			SV.sensor_detected = sensor_val

		if self.stablize_counter > 3:
			self.buffer = np.zeros(100)
			self.counter = 0
			self.stablize_counter = 0
			self.init_interrupts()
		else:
			threading.Timer(0.01, self.read_sensor).start()
