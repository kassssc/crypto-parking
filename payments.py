################################################################################
'''
Crypto Parking: Automated bitcoin parking lot
File name: payments.py
Author(s): Kass Chupongstimun, kchupong@ucsd.edu
           John So, jyso@ucsd.edu
'''
################################################################################

import sys, time, threading, math
import requests

import const
import shared as SV

class Payments():
    '''
        Payments module
        Handles all payment related aspects of the system
        Has the right to set the End Payment Window and Payment Received Flags
    '''

    def __init__(self):
        self.api = const.BITCOIN_BASE_API + const.BITCOIN_ADDR
        self.times_checked = 0

    def check_for_payment(self):
        '''
            Called as a separate thread when the system wants to check for payment
            Either calls itself as a separate thread again in 2 seconds if
            payment window has not ended or set the appropriate flags when
            payment has been received or payment window has ended
        '''

    #***************************************************************************
    # Prevent the state transition related to payment from being able to fire
    # while we check for payment
        SV.E_checking_payment.clear()

        # Convert amount from BTC to Satoshi
        amount_satoshi = SV.amount_due * 100000000
        # Check for payment with API
        payment_received = self.check_bitcoin_transaction(amount_satoshi)

        if payment_received or self.times_checked >= 30:
            # Reset variables
            SV.amount_due = 0
            self.times_checked = 0
            # Payment has been received
            if payment_received:
                SV.payment_received = True
            # Checked 30 times, no payment received
            else:
                SV.end_payment_window = True

        # No payment received and payment window hasn't ended
        else:
            self.times_checked += 1
            # Spawn thread to check again after 2 seconds
            SV.threads['check_payment'] = threading.Timer(
                2,
                self.check_for_payment
            )
            SV.threads['check_payment'].start()

        SV.E_checking_payment.set()
    # Allow the state transitions related to payment to be fired
    #***************************************************************************

    def check_bitcoin_transaction(self, amount):
        '''
            Gets data from the blockchain API to check for payment
            Checks for both transaction age and amount
            amount:
                BTC due in payment
            returns:
                true if payment received, false otherwise
        '''

        # Call API, get response
        try:
            res = requests.get(self.api).json()
        except requests.exceptions.RequestException:
            print("API ERROR")
            return False

        # Get transaction timestamp
        transaction_time = int(res['txs'][0]['time'])

        # Only count if the transaction is after the parking session has ended
        if transaction_time >= SV.transaction_age_threshold:

            # Get list of transaction from the response
            # The list will contain 2 transactions
            # - transaction of the miner fee associated with sending bitcoins
            # - transaction to the parking lot owner's bitcoim address
            transactions = res['txs'][0]['out']

            # For loop throught the list to get the transaction to the
            # owner's bitcon address
            for t in transactions:
                if t['addr'] == const.BITCOIN_ADDR:

                    # Tranaction amount
                    transaction_amount = int(t['value'])

                    # Payment received if amount is greated than amount due
                    if transaction_amount >= (amount - 1000):
                        print("Payment received")
                        return True

        print("Payment not received")
        return False





