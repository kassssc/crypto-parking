################################################################################
'''
Crypto Parking: Automated bitcoin parking lot
File name: payments.py
Description:
Author(s): Kass Chupongstimun, kchupong@ucsd.edu
           John So, jyso@ucsd.edu
'''
################################################################################

import sys, time, threading, math
import requests

import const
import shared as SV

class Payments():

    def __init__(self):
        self.api = const.BITCOIN_BASE_API + const.BITCOIN_ADDR
        self.times_checked = 0

    def check_for_payment(self):

    #***************************************************************************
        SV.E_checking_payment.clear()
        print(SV.amount_due)
        amount_satoshi = SV.amount_due * 100000000
        print(amount_satoshi)
        payment_received = self.check_bitcoin_transaction(amount_satoshi)
        print(self.times_checked)
        if payment_received or self.times_checked > 15:
            SV.amount_due = 0
            self.times_checked = 0
            if payment_received:
                SV.payment_received = True
            else:
                SV.end_payment_window = True
        else:
            self.times_checked += 1
            SV.threads['check_payment'] = threading.Timer(
                2,
                self.check_for_payment
            )
            SV.threads['check_payment'].start()
        SV.E_checking_payment.set()
    #***************************************************************************

    def check_bitcoin_transaction(self, amount):

        if SV.payment_received:
            return True

        try:
            res = requests.get(self.api).json()
        except Exception:
            print("API ERROR")
            return False

        transaction_time = int(res['txs'][0]['time'])

        print("transaction time %d" % transaction_time)
        print("time threshold %d" % SV.transaction_age_threshold)

        if transaction_time >= SV.transaction_age_threshold:
            transactions = res['txs'][0]['out']
            for t in transactions:
                print(t['addr'])
                if t['addr'] == const.BITCOIN_ADDR:
                    print("addr matched!!")
                    transaction_amount = int(t['value'])

                    print("Payment due: %d" % amount)
                    print("transaction amount: %d" % transaction_amount)
                    print("diff: %d" % abs(transaction_amount - amount))

                    if transaction_amount >= (amount - 1000):
                        print("Payment received")
                        return True

        print("Payment not received")
        return False





