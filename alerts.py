###############################################################################
'''
Crypto Parking: Automated bitcoin parking lot
File name: alerts.py
Author(s): Kass Chupongstimun, kchupong@ucsd.edu
           John So, jyso@ucsd.edu
'''
###############################################################################

import smtplib
import const

class Alerts:
    ''' Alerts module, responsible for sending admin notification emails '''

    def __init__(self):
        # account from which emails are sent
        self.username = "cryptoparkingalerts@gmail.com"
        self.password = "cse237awi19"

        self.admin_email = const.ADMIN_EMAIL

    def send_email(self, email_text):
        '''
            Sends email to admin
            email_text: content of the email to be sent
        '''

        try:
            gmail = smtplib.SMTP("smtp.gmail.com", 587)
            gmail.starttls()
            gmail.login(self.username, self.password)
            gmail.sendmail(self.username, self.admin_email, email_text)
            gmail.close()
        except smtplib.SMTPException as ex:
            print("Could not send email " + str(ex))

    def send_user_alert(self):
        ''' Sends the email to notify admin that a user requested assistance '''

        # Set subject and email template
        subject = "User Requesting Assistance"
        email_text = """\
From: %s
To: %s
Subject: %s

A user at your automated parking space is requesting your presence.
""" % (self.username, self.admin_email, subject)
        self.send_email(email_text)

    def send_error_alert(self):
        ''' Sends the email to notify admin that the blocker has been obstructed for too long '''

        # Set subject and email template
        email_text = """\
From: %s
To: %s
Subject: Parking Space Error

This automatic message is to alert you that aberrant behavior has been detected in your system.
You may need to check the system to ensure correct execution.
""" % (self.username, self.admin_email)
        self.send_email(email_text)
