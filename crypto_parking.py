################################################################################
'''
Crypto Parking: Automated bitcoin parking lot
File name: crypto_parking.py
Description:
Author(s): Kass Chupongstimun, kchupong@ucsd.edu
           John So, jyso@ucsd.edu
'''
################################################################################

import sys, time, threading
import RPi.GPIO as GPIO
import signal

import shared as SV
from const import *
from gui import GUI
from blocker import Blocker
from payments import Payments
from sensor_handler import SensorHandler

def exit_gracefully(sig, frame):
    print("Detected SIGINT")
    GPIO.cleanup()
    sys.exit(0)

class CryptoParking(object):
    ''' '''

    def __init__(self):

        self.gui = GUI()
        self.payments = Payments()
        self.sensors = SensorHandler()

        self.free_parking_timer = None
        self.payment_timer = None
        self.parking_start_time = None
        self.parking_end_time = None
        SV.state = State.EMPTY

    def start(self):
        ''' Starts the main program '''

        signal.signal(signal.SIGINT, exit_gracefully)
        #-----------------------------------------------------------------------
        # THREAD: Main Polling Loop
        # Run the main program loop on a second thread
        t_program_loop = threading.Thread(target=self.main_loop)
        t_program_loop.start()

        #self.sensor_handler.init_interrupts()

        #-----------------------------------------------------------------------
        # MAIN THREAD: tkinter GUI
        # initialize tkinter GUI in the main thread
        # tkinter gets pissed when it is not in the main thread
        self.gui.run()

        t_program_loop.join()

    def main_loop(self):
        ''' Main application loop '''

        while True:

            if SV.sensor_detected:
                self.proximity_interrupt_high()
            else:
                self.proximity_interrupt_low()

            if SV.user_wants_to_pay:
                self.want_to_pay_interrupt()

            if SV.payment_received:
                self.payment_received_interrupt()

    #---------------------------------------------------------------------------
    # State Transitions
    #---------------------------------------------------------------------------
    def empty_to_free_parking(self):
        ''' Detects that a car entered the spot '''

        #-----------------------------------------------------------------------
        # THREAD: Free Parking Timer
        # Fork a timer thread to keep track of free parking time
        self.free_parking_timer = threading.Timer(
            FREE_PARKING_LIMIT,             # timeout
            self.free_parking_to_parked     # callback
        )
        self.free_parking_timer.start()

        SV.state = State.FREE_PARKING
        print(SV.state)

    def free_parking_to_empty(self):
        ''' Detects that a car left the spot '''

        # Cancels the timer because a car is no longer detected
        self.free_parking_timer.cancel()

        SV.state = State.EMPTY
        print(SV.state)

    def free_parking_to_parked(self):
        ''' Detect that a car has officially parked in the spot '''

        # Record the current time, it is when the parking starts
        self.parking_start_time = time.time()
        #print(f"started parking at {self.parking_start_time}")

        SV.state = State.BLOCKER_MOVING
        t_blocker_up = threading.Thread(target=self.sensors.block)
        t_blocker_up.start()
        t_blocker_up.join()

        # Go to parked page in GUI
        self.gui.show_parked_page()

        SV.state = State.PARKED
        print(SV.state)

    def parked_to_empty(self):
        ''' Detect case that system detected parking when there's nothing there '''
        self.gui.show_main_page()
        # ABNORMAL BEHAVIOR: call system admin
        SV.state = State.BLOCKER_MOVING
        t_blocker_down = threading.Thread(target=self.sensors.lower)
        t_blocker_down.start()
        t_blocker_down.join()

        SV.state = State.EMPTY
        print(SV.state)

    def parked_to_await_payment(self):
        ''' Detect when user expresses desire to pay for parking '''


        # Record the current time, it is when parking ends
        self.parking_end_time = time.time()
        #print(f"started parking at {self.parking_end_time}")
        total_parked_time = self.parking_end_time - self.parking_start_time
        payment_due = total_parked_time * PARKING_RATE / 3600.0
        SV.amount_due = payment_due
        self.gui.set_amount_due(payment_due)
        #print(f"You parked for {total_parked_time:.3f} seconds")
        #print(f"Payment due: {payment_due:.7f} btc")
        #print(f"Please pay within {PAYMENT_LIMIT} seconds")

        self.payment_timer = threading.Timer(
            PAYMENT_LIMIT,
            self.await_payment_to_parked
        )
        self.payment_timer.start()

        # Go to await payment in GUI
        self.gui.show_pay_page()

        #-----------------------------------------------------------------------
        # THREAD: Check for payment
        # Calls itself again in a separate thread every second
        # Tries for 10 seconds
        # self.payments.check_for_payment()

        # payment_res = self.payments.await_payment()
        SV.state = State.AWAIT_PAYMENT
        print(SV.state)

    def await_payment_to_parked(self):
        ''' Detect when user fails to pay within time limit '''
        self.gui.show_parked_page()
        SV.state = State.PARKED
        print(SV.state)

    def await_payment_to_free_parking(self):
        ''' Detect when user has successfully paid the amout due '''
        self.payment_timer.cancel()
        self.gui.show_paid_page()

        #print(f"Payment received, you have {FREE_PARKING_LIMIT} seconds to leave")

        SV.state = State.BLOCKER_MOVING
        t_blocker_down = threading.Thread(target=self.sensors.lower)
        t_blocker_down.start()
        t_blocker_down.join()

        SV.state = State.FREE_PARKING
        print(SV.state)

    #---------------------------------------------------------------------------
    # Software "Interrupt" Handlers
    #---------------------------------------------------------------------------
    def proximity_interrupt_low(self):
        if SV.state == State.FREE_PARKING:
            self.free_parking_to_empty()

        elif SV.state == State.PARKED:
            # shouldn't happen
            self.parked_to_empty()

    def proximity_interrupt_high(self):
        if SV.state == State.EMPTY:
            self.empty_to_free_parking()

    def want_to_pay_interrupt(self):
        SV.user_wants_to_pay = False
        if SV.state == State.PARKED:
            self.parked_to_await_payment()

    def payment_received_interrupt(self):
        SV.payment_received = False
        if SV.state == State.AWAIT_PAYMENT:
            self.await_payment_to_free_parking()
