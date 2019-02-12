################################################################################
'''
Crypto Parking: Automated bitcoin parking lot
File name: main.py
Description:
Author(s): Kass Chupongstimun, kchupong@ucsd.edu
		   John So,
'''
################################################################################

#!/usr/bin/env python3

import sys
# import RPi.GPIO as GPIO

from crypto_parking import CryptoParking

def main():
	print("Crypto Parking Lot")

	app = CryptoParking()

	while True:
		cmd = input("\nEnter an action:")

		if cmd == 'q':
			sys.exit()
		elif cmd == 'p':
			print(app.state)
		elif cmd == 'high':
			app.proximity_interrupt_high()
		elif cmd == 'low':
			app.proximity_interrupt_low()
		elif cmd == 'wanna pay':
			app.want_to_pay_interrupt()
		elif cmd == 'paid':
			app.payment_received_interrupt()

#-------------------------------------------------------------------------------
# PROGRAM ENTRY POINT
#-------------------------------------------------------------------------------
if __name__ == '__main__': main()

