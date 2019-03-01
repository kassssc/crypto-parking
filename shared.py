################################################################################
'''
Crypto Parking: Automated bitcoin parking lot
File name: shared.py
Description:
Author(s): Kass Chupongstimun, kchupong@ucsd.edu
           John So, jyso@ucsd.edu
'''
################################################################################

from threading import Lock

lock = Lock()

threads = {
	'main_loop': None,
	'poll_sensor': None,
	'free_parking': None,
	'wait_for_payment': None,
	'check_payment': None,
	'thank_you_page': None,
	'help_btn': None
}

sensor_detected = False
user_wants_to_pay = False
payment_received = False
amount_due = 0.0

KILL = False

