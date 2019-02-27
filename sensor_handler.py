################################################################################
'''
Crypto Parking: Automated bitcoin parking lot
File name: sensor_handler.py
Description:
Author(s): Kass Chupongstimun, kchupong@ucsd.edu
		   John So, jyso@ucsd.edu
'''
################################################################################
import threading
import numpy as np
import RPi.GPIO as GPIO

import shared as SV
from const import *

class SensorHandler:

	def __init__(self):
		self.counter = 0
		self.stablize_counter = 0
		self.buffer = np.zeros(BUFFER_LEN)
		self.sensor_val = False

		GPIO.setup(PIN_PROXIMITY_SENSOR, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

	def init_interrupts(self):
		GPIO.add_event_detect(
			PIN_PROXIMITY_SENSOR,
			GPIO.BOTH,
			callback=self.wake_detect	# threaded callback
		)

	def wake_detect(self):
		'''
		'''

		GPIO.remove_event_detect(PIN_PROXIMITY_SENSOR)	# disable interrupts
		self.read_sensor()

	def read_sensor(self):

		# Add current reading to buffer array
		self.buffer[self.counter] = 1 if GPIO.input(PIN_PROXIMITY_SENSOR) else 0
		# Increment counter, loop back to first idx in end of buffer
		self.counter = (self.counter + 1) % BUFFER_LEN

		# Every 1 second, take the averge of readings in the buffer
		# Set the shared variable to the result
		# If it reads the same value, add to the stablize counter
		if self.counter == 100:
			sensor_val = np.mean(self.buffer) > 0.5 # might change to a different threshold
			if SV.sensor_detected == sensor_val:
				self.stablize_counter += 1
			SV.sensor_detected = sensor_val

		# If GPIO input stablizes, reset everything and go back to waiting for
		# interrupts on rising/falling edge
		if self.stablize_counter > 3:
			self.buffer = np.zeros(BUFFER_LEN)
			self.counter = 0
			self.stablize_counter = 0
			self.init_interrupts()

		# If GPIO input has not stablized, continue reading values
		# Calls itself again in a thread in 10ms
		else:
			threading.Timer(0.01, self.read_sensor).start()

