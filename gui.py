################################################################################
'''
Crypto Parking: Automated bitcoin parking lot
File name: gui.py
Author(s): Kass Chupongstimun, kchupong@ucsd.edu
             John So, jyso@ucsd.edu
'''
################################################################################

import threading, qrcode, requests
import tkinter as tk
from PIL import ImageTk,Image

import shared as SV
import const
from alerts import Alerts

class GUI(object):
    '''
        GUI module of our application
        Responsible for construction of the gui and handling interactions\
        Has the right to set the user wants to pay flag
    '''

    def __init__(self):
        ''' Constructs the GUI '''

        self.window = tk.Tk()
        self.window.title("Crypto Parking")
        self.window.attributes("-fullscreen", True)

        # Bind global keyboard commands
        self.window.bind("<Escape>", self.quit)

        self.window.config(bg=const.COLOR_BG)
        self.main_frame = MainFrame(self.window)
        self.main_frame.pack(side="top", fill="both", expand=True)

        # Call admin for help button
        self.call_admin_btn_img = ImageTk.PhotoImage(file="./assets/call_admin_btn.png")
        self.call_admin_btn = tk.Button(
            self.frame,
            width=175,
            height=35,
            highlightthickness=0,
            highlightbackground=const.COLOR_BG,
            bd=-2,
            bg=const.COLOR_BG,
            command=self.call_admin,
            image=self.call_admin_btn_img
        )
        self.call_admin_btn.pack()

        # Call admin for help button (pressed)
        self.help_otw_btn_img = ImageTk.PhotoImage(file="./assets/help_otw.png")
        self.help_otw_btn = tk.Button(
            self.frame,
            width=175,
            height=35,
            highlightthickness=0,
            highlightbackground=const.COLOR_BG,
            bd=-2,
            bg=const.COLOR_BG,
            image=self.help_otw_btn_img
        )

    # Instantiate alert sender module
        self.alert_sender = Alerts()

    #===========================================================================
    # CODE USED FOR TESTING
        # Dummy buttons simulate input
        '''self.frame = tk.Frame(
            self.window,
            bg=const.COLOR_BG
        )
        self.frame.pack(
            side="bottom",
            fill="x",
            expand=False,
            pady=15
        )
        self.confirm = tk.Button(
            self.frame,
            text="Confirm paid",
            width=16,
            command=self.confirm
        )
        self.s1 = tk.Button(
            self.frame,
            text="Sensor 1",
            width=16,
            command=self.s1
        )
        self.s0 = tk.Button(
            self.frame,
            text="Sensor 0",
            width=16,
            command=self.s0
        )
        #self.confirm.pack()
        #self.s1.pack()
        #self.s0.pack()

    def s1(self):
        SV.sensor_detected = True

    def s0(self):
        SV.sensor_detected = False

    def confirm(self):
        SV.payment_received = True
    '''
    # CODE USED FOR TESTING
    #===========================================================================

    def run(self):
        ''' Runs the GUI '''

        self.show_main_page()
        self.window.mainloop()

    def show_main_page(self):
        ''' Switch to main page '''

        # set the rate info in USD using exchanghe rate API
        self.set_usd_rate()
        self.main_frame.welcome_page.lift()

        # in case when main page is shown after the thank you page expires
        # will unblock execution of state transition from await payment to
        # free parking in main loop
        SV.E_thankyou_page.set()
    #***************************************************************************

    def show_parked_page(self):
        ''' Switch to parked page '''
        self.main_frame.parked_page.lift()

    def show_pay_page(self):
        ''' Switch to pay page '''
        self.main_frame.pay_page.lift()

    def show_paid_page(self):
        ''' Switch to thank you page '''
    #***************************************************************************
        # Block execution of state transition from await payment to
        # free parking in main loop to wait for thank you page to expire
        SV.E_thankyou_page.clear()
        self.main_frame.paid_page.lift()

        #-----------------------------------------------------------------------
        # THREAD: Show main page again after a set time
        SV.threads['thank_you_page'] = threading.Timer(2, self.show_main_page)
        SV.threads['thank_you_page'].start()

    def set_pay_text(self, amount, time):
        '''
            Sets the amount due information in the pay page
            Sets the text of the payment due in USD using exchange rate API
            amount: payment due in BTC
            time: total time parked in seconds
        '''

        # Get exchange rate from BTC to USD from API
        try:
            # Call API
            res = requests.get(const.EXCHANGE_RATE_API).json()
            # Get relevant information from response
            USD_per_BTC = float(res['last'])
            # calculate the amount due in USD
            amount_usd = USD_per_BTC * amount
            amount_usd_text = "($%.2f)" % amount_usd

        # If network / API is not available, show error test on GUI
        except (requests.exceptions.RequestException, ConnectionError) as e:
            print("API ERROR")
            print(e)
            amount_usd_text = "Network error, can't fetch exchange rate"

        self.main_frame.pay_page.amount_due_usd.set(amount_usd_text)
        self.main_frame.pay_page.amount_due.set("%.6f BTC" % amount)
        self.main_frame.pay_page.amount_due.set("%.6f BTC" % amount)
        self.main_frame.pay_page.time_parked.set("%.2f seconds" % time)

    def set_usd_rate(self):
        ''' Sets the parking rate in USD text using exchange rate from API '''

        try:
            # Call API
            res = requests.get(const.EXCHANGE_RATE_API).json()
            # Get relevant info from response
            USD_per_BTC = float(res['last'])
            # Conversion
            rate_float_hr = const.PARKING_RATE * USD_per_BTC * 3600.0
            text = "($%.2f / hr)" % rate_float_hr

        # If network / API is not available, show error test on GUI
        except (requests.exceptions.RequestException, ConnectionError) as e:
            print(e)
            text = "Network error, can't fetch exchange rate"

        self.main_frame.welcome_page.parking_rate_usd.set(text)

    def quit(self, instance=None):
        ''' Destroys GUI to quit application, sets flag to break main loop '''

        self.window.destroy()
        SV.KILL = True

    def call_admin(self):
        '''
            Uses the alerts module to call admin in case user needs assistance
            Also changes the button appearance to give user feedback that
            admin has been notified
            When the appearance is changed, button taps will not send
            notification again
        '''

        self.alert_sender.send_user_alert()
        self.call_admin_btn.pack_forget()
        self.help_otw_btn.pack()

        # After a set time, revert the appearance of the button
        SV.threads['help_btn'] = threading.Timer(
            10,
            self.revert_call_admin_btn
        )
        SV.threads['help_btn'].start()

    def revert_call_admin_btn(self):
        ''' Reverts the call admin button appearnce '''

        self.help_otw_btn.pack_forget()
        self.call_admin_btn.pack()

class MainFrame(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)

        self.welcome_page = WelcomePage(self)
        self.parked_page = ParkedPage(self)
        self.pay_page = PayPage(self)
        self.paid_page = PaidPage(self)
        self.welcome_page.place(in_=self, x=0, y=0, relwidth=1, relheight=1)
        self.parked_page.place(in_=self, x=0, y=0, relwidth=1, relheight=1)
        self.pay_page.place(in_=self, x=0, y=0, relwidth=1, relheight=1)
        self.paid_page.place(in_=self, x=0, y=0, relwidth=1, relheight=1)

class Page(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)

class WelcomePage(Page):
    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)

        self.config(bg=const.COLOR_BG, pady=20)
        parking_rate_hr = float(const.PARKING_RATE) * 3600.0
        parking_rate = "%.5f BTC / hr" % parking_rate_hr
        self.parking_rate_usd = tk.StringVar()

        labels = [
            tk.Label(
                self,
                text="Welcome",
                bg=const.COLOR_BG,
                fg=const.COLOR_FG,
                font=("Helvetica 20 bold")
            ),
            tk.Label(
                self,
                text="Bitcoin Parking Lot",
                bg=const.COLOR_BG,
                fg=const.COLOR_FG,
                font=("Helvetica 20 bold")
            ),
            tk.Label(
                self,
                text="Parking Rate:",
                bg=const.COLOR_BG,
                fg=const.COLOR_FG,
                font=("Helvetica 18 bold")
            ),
            tk.Label(
                self,
                text=parking_rate,
                bg=const.COLOR_BG,
                fg=const.COLOR_FG,
                font=("Helvetica 18 bold")
            ),
            tk.Label(
                self,
                textvariable=self.parking_rate_usd,
                bg=const.COLOR_BG,
                fg=const.COLOR_FG,
                font=("Helvetica 18 bold")
            )
        ]

        for label in labels:
            label.pack(fill="none", expand=True)

class ParkedPage(Page):
    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)

        self.config(bg=const.COLOR_BG, pady=20)
        self.btn_img = ImageTk.PhotoImage(file="./assets/pay_btn.png")
        items = [
            tk.Label(
                self,
                text="Parking Spot is Occupied",
                bg=const.COLOR_BG,
                fg=const.COLOR_FG,
                font=("Helvetica 18 bold")
            ),
            tk.Button(
                self,
                width=250,
                height=50,
                highlightthickness=0,
                highlightbackground=const.COLOR_BG,
                bd=-2,
                bg=const.COLOR_BG,
                font=("Helvetica 18 bold"),
                command=self.on_pay_click,
                image=self.btn_img
            )
        ]

        for item in items:
            item.pack(fill="none", expand=True)

    def on_pay_click(self):
        SV.user_wants_to_pay = True

class PayPage(Page):
    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)

        # Init dynamic variables
        self.amount_due = tk.StringVar()
        self.time_parked = tk.StringVar()
        self.amount_due_usd = tk.StringVar()
        self.config(bg=const.COLOR_BG)

        # Construct QR code image from bitcoin address string
        qr = qrcode.QRCode(
            version=2,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=5,
            border=4,
        )
        qr.add_data(const.BITCOIN_ADDR)
        qr.make(fit=True)

        self.img = ImageTk.PhotoImage(
            qr.make_image(
                fill_color="black",
                back_color="white"
            )
        )

        img_frame = tk.Frame(
            self,
            bg=const.COLOR_BG,
            width=240,
            height=320
        )
        text_frame = tk.Frame(
            self,
            bg=const.COLOR_BG,
            width=240,
            height=320
        )

        items = [
            tk.Label(
                img_frame,
                image=self.img,
                bg=const.COLOR_BG,
            ),
            tk.Label(
                text_frame,
                text= "Total Time Parked:",
                bg=const.COLOR_BG,
                fg=const.COLOR_FG,
                font=("Helvetica 15 bold")
            ),
            tk.Label(
                text_frame,
                textvariable=self.time_parked,
                bg=const.COLOR_BG,
                fg=const.COLOR_FG,
                font=("Helvetica 22 bold")
            ),
            tk.Label(
                text_frame,
                text="Amount Due:",
                bg=const.COLOR_BG,
                fg=const.COLOR_FG,
                font=("Helvetica 15 bold")
            ),
            tk.Label(
                text_frame,
                textvariable=self.amount_due,
                bg=const.COLOR_BG,
                fg=const.COLOR_FG,
                font=("Helvetica 22 bold")
            ),
            tk.Label(
                text_frame,
                text="Pay with Bitcoin",
                bg=const.COLOR_BG,
                fg=const.COLOR_FG,
                font=("Helvetica 15 bold")
            ),
            tk.Label(
                text_frame,
                textvariable=self.amount_due_usd,
                bg=const.COLOR_BG,
                fg=const.COLOR_FG,
                font=("Helvetica 22 bold")
            ),
        ]

        img_frame.pack(
            side=tk.LEFT,
            fill="both",
            expand=True,
            pady=10
        )
        text_frame.pack(
            side=tk.RIGHT,
            fill="x",
            expand=True
        )

        for item in items:
            item.pack(fill="none", expand=True)

class PaidPage(Page):
    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)

        self.config(bg=const.COLOR_BG, pady=35)

        labels = [
            tk.Label(
                self,
                text="Payment Received",
                bg=const.COLOR_BG,
                fg=const.COLOR_FG,
                font=("Helvetica 20 bold")
            ),
            tk.Label(
                self,
                text="Thank You!",
                bg=const.COLOR_BG,
                fg=const.COLOR_FG,
                font=("Helvetica 20 bold")
            ),
            tk.Label(
                self,
                text="You have 5 minutes to leave...",
                bg=const.COLOR_BG,
                fg=const.COLOR_FG,
                font=("Helvetica 14 bold")
            )
        ]

        for label in labels:
            label.pack(fill="none", expand=True)
