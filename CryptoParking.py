################################################################################
'''

'''
################################################################################

import sys
import time, threading, signal
from enum import Enum
# import RPi.GPIO as GPIO

from const import *

class CryptoParking():
	'''
	'''

	def __init__(self):

		# self.payments = Payments()
		# self.blocker = Blocker()

		self.state = State.EMPTY
		self.free_parking_timer = None
		self.payment_timer = None
		self.parking_start_time = None
		self.parking_end_time = None

	#---------------------------------------------------------------------------
	# State Transitions
	#---------------------------------------------------------------------------
	def empty_to_free_parking(self):
		self.free_parking_timer = threading.Timer(
			FREE_PARKING_LIMIT,
			self.free_parking_to_parked
		)
		self.free_parking_timer.start()

		self.state = State.FREE_PARKING
		print(self.state)

	def free_parking_to_empty(self):
		self.free_parking_timer.cancel()

		self.state = State.EMPTY
		print(self.state)

	def free_parking_to_parked(self):
		self.parking_start_time = time.time()
		self.state = State.PARKED
		print(self.state)

	def parked_to_empty(self):

		self.state = State.EMPTY
		print(self.state)

	def parked_to_await_payment(self):
		self.parking_end_time = time.time()
		total_parked_time = self.parking_end_time - self.parking_start_time

		print("You parked for %d seconds" % total_parked_time)
		print("Payment due: $%d" % total_parked_time * PARKING_RATE)
		print("Please pay within %d seconds" % PAYMENT_LIMIT)

		self.payment_timer = threading.Timer(
			PAYMENT_LIMIT,
			self.await_payment_to_parked
		)
		self.payment_timer.start()
		self.state = State.AWAIT_PAYMENT
		print(self.state)

	def await_payment_to_parked(self):
		self.state = State.PARKED
		print(self.state)

	def await_payment_to_empty(self):

		print("Payment received, you have %d seconds to leave" % FREE_PARKING_LIMIT)

		self.payment_timer.cancel()
		self.state = State.EMPTY
		print(self.state)

	#---------------------------------------------------------------------------
	# Sensor Interrupt Handlers
	#---------------------------------------------------------------------------
	def proximity_interrupt_low(self):

		if self.state == State.FREE_PARKING:
			self.free_parking_to_empty()

		if self.state == State.PARKED:
			# shouldn't happen
			self.parked_to_empty()

	def proximity_interrupt_high(self):

		if self.state == State.EMPTY:
			self.empty_to_free_parking()

	def want_to_pay_interrupt(self):
		if self.state == State.PARKED:
			self.parked_to_await_payment()

	def payment_received_interrupt(self):

		if self.state == State.AWAIT_PAYMENT:
			self.await_payment_to_empty()

class State(Enum):
	EMPTY = 0
	FREE_PARKING = 1
	PARKED = 2
	AWAIT_PAYMENT = 3
	PAID = 4