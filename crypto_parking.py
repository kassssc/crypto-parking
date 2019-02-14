################################################################################
'''

'''
################################################################################

import sys
import time, threading
from enum import Enum
# import RPi.GPIO as GPIO

from const import *
from blocker import Blocker
from payments import Payments

class CryptoParking(object):
	'''
	'''

	def __init__(self):

		self.blocker = Blocker()
		self.payments = Payments()

		self.state = State.EMPTY
		self.free_parking_timer = None
		self.payment_timer = None
		self.parking_start_time = None
		self.parking_end_time = None

	#---------------------------------------------------------------------------
	# State Transitions
	#---------------------------------------------------------------------------
	def empty_to_free_parking(self):
		''' Detects that a car entered the spot '''

		# Fork a timer thread to keep track of free parking time
		self.free_parking_timer = threading.Timer(
			FREE_PARKING_LIMIT,
			self.free_parking_to_parked
		)
		self.free_parking_timer.start()

		self.state = State.FREE_PARKING
		print(self.state)

	def free_parking_to_empty(self):
		''' Detects that a car left the spot '''

		# Cancels the timer because a car is no longer detected
		self.free_parking_timer.cancel()

		self.state = State.EMPTY
		print(self.state)

	def free_parking_to_parked(self):
		''' Detect that a car has officially parked in the spot '''

		# Record the current time, it is when the parking starts
		self.parking_start_time = time.time()

		self.state = State.BLOCKER_MOVING
		t_blocker_up = threading.Thread(target=self.blocker.block)
		t_blocker_up.start()
		t_blocker_up.join()

		self.state = State.PARKED
		print(self.state)

	def parked_to_empty(self):
		''' Detect case that system detected parking when there's nothing there '''

		self.state = State.EMPTY
		print(self.state)

	def parked_to_await_payment(self):
		''' Detect when user expresses desire to pay for parking '''

		# Record the current time, it is when parking ends
		self.parking_end_time = time.time()
		total_parked_time = self.parking_end_time - self.parking_start_time
		payment_due = total_parked_time * PARKING_RATE
		print(f"You parked for {total_parked_time:.2f} seconds")
		print(f"Payment due: {payment_due:.5f} btc")
		print(f"Please pay within {PAYMENT_LIMIT} seconds")

		self.payment_timer = threading.Timer(
			PAYMENT_LIMIT,
			self.await_payment_to_parked
		)
		self.payment_timer.start()
		# payment_res = self.payments.await_payment()
		self.state = State.AWAIT_PAYMENT
		print(self.state)

	def await_payment_to_parked(self):
		''' Detect when user fails to pay within time limit '''
		self.state = State.PARKED
		print(self.state)

	def await_payment_to_empty(self):
		''' Detect when user has successfully paid the amout due '''
		print(f"Payment received, you have {FREE_PARKING_LIMIT} seconds to leave")
		self.payment_timer.cancel()

		self.state = State.BLOCKER_MOVING
		t_blocker_down = threading.Thread(target=self.blocker.lower)
		t_blocker_down.start()
		t_blocker_down.join()

		self.state = State.EMPTY
		print(self.state)

	#---------------------------------------------------------------------------
	# Interrupt Handlers
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
	BLOCKER_MOVING = 5