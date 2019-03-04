################################################################################
'''
Crypto Parking: Automated bitcoin parking lot
File name: crypto_parking.py
Description:
Author(s): Kass Chupongstimun, kchupong@ucsd.edu
           John So, jyso@ucsd.edu
'''
################################################################################

import sys, time, threading, signal, json
from enum import Enum
from pathlib import Path

import shared as SV
import const
from gui import GUI
from payments import Payments
from sensor_handler import SensorHandler

class CryptoParking(object):
    ''' '''

    def __init__(self):

        # Open and load configuration data
        with Path('./config.json').open('r') as f:
            config = json.load(f)
            try:
                const.ADMIN_EMAIL = config['admin_email']
                const.FREE_PARKING_LIMIT = config['free_parking_limit']
                const.PAYMENT_LIMIT = config['payment_limit']
                const.PARKING_RATE = config['parking_rate']
                const.BITCOIN_ADDR = config['bitcoin_addr']
            except KeyError:
                print("Bad config file")
                sys.exit(0)

        self.gui = GUI()
        self.payments = Payments()
        self.sensors = SensorHandler()

        self.parking_start_time = None
        self.parking_end_time = None
        SV.state = State.EMPTY

    def start(self):
        ''' Starts the main program '''

        # Sigint will trigger a graceful exit
        signal.signal(signal.SIGINT, self.exit_gracefully)

        #-----------------------------------------------------------------------
        # THREAD: Main Polling Loop
        # Run the main program loop on a second thread
        SV.threads['main_loop'] = threading.Thread(target=self.main_loop)
        SV.threads['main_loop'].start()

        # Initializes sensor interrupt on edge detection
        self.sensors.init_interrupts()

        #-----------------------------------------------------------------------
        # MAIN THREAD: tkinter GUI
        # initialize tkinter GUI in the main thread
        # tkinter gets pissed when it is not in the main thread
        try:
            self.gui.run()
        except RuntimeError as e:
            print("Error in GUI")
            print(e)

        # Reached when GUI is terminated (via esc or X button)
        self.exit_gracefully()

        # END PROGRAM

    def exit_gracefully(self, sig=None, frame=None):

        # Break main loop
        SV.KILL = True

        # Cancel all timers, join all threads
        for thread in SV.threads:
            try:
                thread.cancel()
                thread.join()
            except Exception as e:
                pass

        self.sensors.gpio_cleanup()
        sys.exit(0)

    def main_loop(self):
        ''' Main application loop '''

        while True:

            if SV.KILL:
                break

            if SV.sensor_detected:
                self.proximity_interrupt_high()
            else:
                self.proximity_interrupt_low()

            if SV.user_wants_to_pay:
                self.want_to_pay_interrupt()

            if SV.end_payment_window:
                self.end_payment_window_interrupt()

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
        SV.threads['free_parking'] = threading.Timer(
            const.FREE_PARKING_LIMIT,             # timeout
            self.free_parking_to_parked     # callback
        )
        SV.threads['free_parking'].start()

        SV.state = State.FREE_PARKING
        print(SV.state)

    def free_parking_to_empty(self):
        ''' Detects that a car left the spot '''

        # Cancels the timer because a car is no longer detected
        SV.threads['free_parking'].cancel()

        SV.state = State.EMPTY
        print(SV.state)

    def free_parking_to_parked(self):
        ''' Detect that a car has officially parked in the spot '''

        # Record the current time as when the parking starts
        self.parking_start_time = time.time()

        # Lift the blocker
        SV.state = State.BLOCKER_MOVING
        # Wait until there is no obstruction before the blocker lifts
        self.block_execution_for_obstruction(10)
        t_blocker_up = threading.Thread(target=self.sensors.block)
        t_blocker_up.start()
        t_blocker_up.join()

        self.gui.show_parked_page()

        SV.state = State.PARKED
        print(SV.state)

    def parked_to_empty(self):
        ''' Detect case that system detected parking when there's nothing there '''

        # Lower the blocker
        SV.state = State.BLOCKER_MOVING
        # Wait until there is no obstruction before the blocker lowers
        self.block_execution_for_obstruction(10)
        t_blocker_down = threading.Thread(target=self.sensors.lower)
        t_blocker_down.start()
        t_blocker_down.join()

        self.gui.show_main_page()

        SV.state = State.EMPTY
        print(SV.state)

    def parked_to_await_payment(self):
        ''' Detect when user expresses desire to pay for parking '''

        # Record the current time as when parking ends
        self.parking_end_time = time.time()
        print(self.parking_end_time)

        SV.transaction_age_threshold = int(self.parking_end_time)
        total_parked_time = self.parking_end_time - self.parking_start_time
        payment_due = total_parked_time * const.PARKING_RATE
        SV.amount_due = payment_due
        self.gui.set_pay_text(payment_due, total_parked_time)

        self.gui.show_pay_page()

        #-----------------------------------------------------------------------
        # THREAD: Check for payment
        # Calls itself again in a separate thread every 2 seconds
        SV.threads['check_payment'] = threading.Thread(
            target=self.payments.check_for_payment
        )
        SV.threads['check_payment'].start()

        SV.state = State.AWAIT_PAYMENT
        print(SV.state)

    def await_payment_to_parked(self):
        ''' Detect when user fails to pay within time limit '''

        self.gui.show_parked_page()

        # Reset end payment window flag
        SV.end_payment_window = False
        SV.state = State.PARKED
        print(SV.state)

    def await_payment_to_free_parking(self):
        ''' Detect when user has successfully paid the amout due '''

        self.gui.show_paid_page()

        # Wait until there is no obstruction before the blocker lowers
        self.block_execution_for_obstruction(10)
        SV.state = State.BLOCKER_MOVING
        t_blocker_down = threading.Thread(target=self.sensors.lower)
        t_blocker_down.start()
        t_blocker_down.join()

    #***************************************************************************
        # Wait for the thank you page to finish showing
        SV.E_thankyou_page.wait()

        #-----------------------------------------------------------------------
        # THREAD: Free Parking Timer
        # Fork a timer thread to keep track of free parking time
        SV.threads['free_parking'] = threading.Timer(
            const.FREE_PARKING_LIMIT,       # timeout
            self.free_parking_to_parked     # callback
        )
        SV.threads['free_parking'].start()

        # Reset payment received flag
        SV.payment_received = False
        SV.state = State.FREE_PARKING
        print(SV.state)

    #---------------------------------------------------------------------------
    # Software "Interrupt" Handlers
    #---------------------------------------------------------------------------
    def proximity_interrupt_low(self):
        if SV.state == State.FREE_PARKING:
            self.free_parking_to_empty()

        elif SV.state == State.PARKED:
            self.parked_to_empty()

    def proximity_interrupt_high(self):
        if SV.state == State.EMPTY:
            self.empty_to_free_parking()

    def want_to_pay_interrupt(self):
        SV.user_wants_to_pay = False
        if SV.state == State.PARKED:
            self.parked_to_await_payment()

    def end_payment_window_interrupt(self):
        #***********************************************************************
        SV.E_checking_payment.wait()
        if SV.state == State.AWAIT_PAYMENT:
            self.await_payment_to_parked()

    def payment_received_interrupt(self):
        #***********************************************************************
        SV.E_checking_payment.wait()
        if SV.state == State.AWAIT_PAYMENT:
            self.await_payment_to_free_parking()

    def block_execution_for_obstruction(self, timeout):
        email_sent = False
        counter = 0
        while True:
            if self.sensors.no_obstruction():
                return

            if not email_sent and counter > timeout * 40:
                self.gui.alert_sender.send_error_alert()
                email_sent = True
            counter += 1
            time.sleep(.01)


class State(Enum):
    EMPTY = 0
    FREE_PARKING = 1
    PARKED = 2
    AWAIT_PAYMENT = 3
    PAID = 4
    BLOCKER_MOVING = 5
