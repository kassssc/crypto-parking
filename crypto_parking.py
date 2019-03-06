################################################################################
'''
Crypto Parking: Automated bitcoin parking lot
File name: crypto_parking.py
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
    ''' Main application class '''

    def __init__(self):
        ''' Instantiates the application '''

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

        # Instantiate modules
        self.gui = GUI()
        self.payments = Payments()
        self.sensors = SensorHandler()

        self.parking_start_time = None
        self.parking_end_time = None

        # Initial State
        SV.state = State.EMPTY

    def start(self):
        ''' Starts the main program '''

        # Sigint will trigger a graceful exit
        signal.signal(signal.SIGINT, self.exit_gracefully)

        #-----------------------------------------------------------------------
        # THREAD: Main Polling Loop
        # Run the main program loop on a separate thread
        SV.threads['main_loop'] = threading.Thread(target=self.main_loop)
        SV.threads['main_loop'].start()

        # Initializes sensor interrupt on edge detection
        self.sensors.init_interrupts()

        #-----------------------------------------------------------------------
        # MAIN THREAD: tkinter GUI
        # initialize tkinter GUI in the main thread
        try:
            self.gui.run()
        except RuntimeError as e:
            print("Error in GUI")
            print(e)

        # Reached when GUI is terminated (via esc or X button)
        self.exit_gracefully()

        # END PROGRAM

    def exit_gracefully(self, sig=None, frame=None):
        '''
            Exits the program gracefully
            Wait for all running threads to complete
            Cancels all timer with threaded callbacks
        '''

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
        '''
            Main application loop
            Continuously polls flags and react accordingly
        '''

        while True:

            # Kill flag will break out of the main loop
            if SV.KILL:
                break

            # Parking spot infrared sensor, flag set by sensors module
            # Parking sensor gives a 1
            if SV.sensor_detected:
                self.proximity_high()
            # Parking sensor gives a 0
            else:
                self.proximity_low()

            # User wants to pay flag, set by GUI
            if SV.user_wants_to_pay:
                self.want_to_pay()

            # End payment window flag, set by payments module
            if SV.end_payment_window:
                self.end_payment_window()

            # Payment received flag, set by payments module
            if SV.payment_received:
                self.payment_received()

    #---------------------------------------------------------------------------
    # State Transitions
    #---------------------------------------------------------------------------
    def empty_to_free_parking(self):
        ''' Fires when something is detected in the parking spot '''

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
        ''' Fires when nothing is detected in the parking spot anymore '''

        # Cancels the timer because a car is no longer detected
        SV.threads['free_parking'].cancel()

        SV.state = State.EMPTY
        print(SV.state)

    def free_parking_to_parked(self):
        ''' Fires when a car has parked in the spot for longer than the free parking time '''

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
        '''
            When the system is in parked state, but sensor reads a 0
            Can't happen when a car is in the spot (car physically cannot leave)
            This is for other stuff that blocked the sensor for long enough and
            then leaves, ex. a dog sleeping on it
            Blocker should be lowered
        '''

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
        ''' Fires when the pay button is pressed by the user '''

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
        ''' Fires when payment is not received in given window '''

        self.gui.show_parked_page()

        # Reset end payment window flag
        SV.end_payment_window = False
        SV.state = State.PARKED
        print(SV.state)

    def await_payment_to_free_parking(self):
        ''' Fires when correct payment has been received '''

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
    # Flag handlers
    #---------------------------------------------------------------------------
    def proximity_low(self):
        ''' Handles parking sensor flag '''
        if SV.state == State.FREE_PARKING:
            self.free_parking_to_empty()

        elif SV.state == State.PARKED:
            self.parked_to_empty()

    def proximity_high(self):
        ''' Handles parking sensor flag '''
        if SV.state == State.EMPTY:
            self.empty_to_free_parking()

    def want_to_pay(self):
        ''' Handles user wants to pay flag '''
        SV.user_wants_to_pay = False
        if SV.state == State.PARKED:
            self.parked_to_await_payment()

    def end_payment_window(self):
        ''' Handles end payment window flag '''
        #***********************************************************************
        SV.E_checking_payment.wait()
        if SV.state == State.AWAIT_PAYMENT:
            self.await_payment_to_parked()

    def payment_received(self):
        ''' Handles payment received flag '''
        #***********************************************************************
        SV.E_checking_payment.wait()
        if SV.state == State.AWAIT_PAYMENT:
            self.await_payment_to_free_parking()

    def block_execution_for_obstruction(self, timeout):
        '''
            Enters a loop and does not break until the blocker is no longer
            obstructed. Sends an email to notify system admin after a set
            amount of time passed
            System will get stuck here until blocker could move
        '''

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
    ''' System states '''

    EMPTY = 0
    FREE_PARKING = 1
    PARKED = 2
    AWAIT_PAYMENT = 3
    BLOCKER_MOVING = 4
