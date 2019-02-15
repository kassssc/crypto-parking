################################################################################
'''
Crypto Parking: Automated bitcoin parking lot
File name: main.py
Description:
Author(s): Kass Chupongstimun, kchupong@ucsd.edu
		   John So, jyso@ucsd.edu
'''
################################################################################
import shared as SV

class SensorHandler:

	def __init__(self):

		# set up interrupt handler on rising edge
		pass

	def wake_detect(self):
		'''
			Poll the proximity sensor and preprocess the data
			Prolly use moving average, gather around 250ms of data
			Return a single 1 or 0 to finalize whether there is something on the sensor
			Go back to sleep if the readings stablize
		'''

		# disable interrupts

		while not SV.SENSOR_SLEEP:
			# poll sensor and process raw input
			# SV.SENSOR_SLEEP = 1 if input stablizes
			# every once in a while, set SV.SENSOR_DETECTED to update main thread
			pass

		# set up interrupts again


