################################################################################
'''
Crypto Parking: Automated bitcoin parking lot
File name: payments.py
Description:
Author(s): Kass Chupongstimun, kchupong@ucsd.edu
           John So, jyso@ucsd.edu
'''
################################################################################

import sys
import time, threading

from const import *
import shared as SV

class Payments():

    def __init__(self):
        self.times_checked = 0
        self.t_check_timer = 0

    def check_for_payment(self):
        '''
        payment_received = check_bitcoin_transaction(SV.amount_due)
        if payment_received or self.times_checked > 10:
            self.times_checked = 0
            SV.amount_due = 0
            SV.payment_received = True
        else:
            self.times_checked += 1
            self.t_check_timer = threading.Timer(1, self.check_for_payment)
            self.t_check_timer.start()

        '''

    def check_bitcoin_transactions(amount):
        return False
