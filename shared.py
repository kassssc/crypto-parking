################################################################################
'''
Crypto Parking: Automated bitcoin parking lot
File name: shared.py
Author(s): Kass Chupongstimun, kchupong@ucsd.edu
           John So, jyso@ucsd.edu
'''
################################################################################

import threading

# Synchronization variables "events"
E_checking_payment = threading.Event()
E_thankyou_page = threading.Event()


# Keep threads organized
threads = {
	'main_loop': None,
	'poll_sensor': None,
	'free_parking': None,
	'check_payment': None,
	'thank_you_page': None,
	'help_btn': None
}

# Flags
sensor_detected = False
user_wants_to_pay = False
payment_received = False
end_payment_window = False
KILL = False

# Regular shared variables
amount_due = 0.0
transaction_age_threshold = None

