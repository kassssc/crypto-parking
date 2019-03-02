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
        self.times_checked = 0
        self.t_check_timer = 0

    def check_for_payment(self):
        with SV.lock:
            payment_received = self.check_bitcoin_transaction(SV.amount_due)
            if payment_received or self.times_checked > 60:
                self.times_checked = 0
                SV.amount_due = 0
                SV.payment_received = True
            else:
                self.times_checked += 1
                SV.threads['check_payment'] = threading.Timer(
                    2,
                    self.check_for_payment
                )
                SV.threads['check_payment'].start()

    def check_bitcoin_transaction(self, amount):
        res = requests.get(const.BITCOIN_BASE_API + const.BITCOIN_ADDR)
        r_json = res.json()
        latest_transaction = int(r_json['txs'][0]['out'][1]['value'])
        transaction_time = int(r_json['txs'][0]['time'])
        print("trans time %d" % transaction_time)
        print("time threshold %d" % SV.transaction_age_threshold)
        if transaction_time < SV.transaction_age_threshold:
            print("transaction too old")
            return False
        print("amount is %d" % amount)
        print("latest transaction is %d" % latest_transaction)
        print("diff is %d" % abs(latest_transaction - amount))
        return latest_transaction >= (amount - 1000)





