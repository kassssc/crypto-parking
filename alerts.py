###############################################################################
'''
Crypto Parking: Automated bitcoin parking lot
File name: alerts.py
Description:
Author(s): Kass Chupongstimun, kchupong@ucsd.edu
           John So, jyso@ucsd.edu
'''
###############################################################################

import smtplib
import const


class Alerts:

    def __init__(self):
        self.username = "cryptoparkingalerts@gmail.com"
        self.password = "cse237awi19"

        self.admin_email = const.ADMIN_EMAIL

    def send_email(self, email_text):
        try:
            gmail = smtplib.SMTP("smtp.gmail.com", 587)
            gmail.starttls()
            gmail.login(self.username, self.password)
            gmail.sendmail(self.username, self.admin_email, email_text)
            gmail.close()
        except Exception as ex:
            print("Could not send email " + str(ex))

    def send_user_alert(self):
        subject = "User Requesting Assistance"
        email_text = """\
From: %s
To: %s
Subject: %s

A user at your automated parking space is requesting your presence.
""" % (self.username, self.admin_email, subject)
        self.send_email(email_text)

    def send_error_alert(self):
        email_text = """\
From: %s
To: %s
Subject: Parking Space Error

This automatic message is to alert you that aberrant behavior has been detected in your system.
You may need to check the system to ensure correct execution.
""" % (self.username, self.admin_email)
        self.send_email(email_text)
