################################################################################
'''
Crypto Parking: Automated bitcoin parking lot
File name: gui.py
Description:
Author(s): Kass Chupongstimun, kchupong@ucsd.edu
             John So, jyso@ucsd.edu
'''
################################################################################

import threading, qrcode, requests
import tkinter as tk
from PIL import ImageTk,Image

import shared as SV
import const

class GUI(object):

    def __init__(self):
        '''
        '''

        self.window = tk.Tk()
        self.window.title("Crypto Parking")
        #self.window.geometry("480x480")
        #self.window.geometry("480x320")
        self.window.attributes("-fullscreen", True)

        self.window.bind("<Escape>", self.quit)
        self.window.bind("x", self.quit)
        self.window.config(bg=const.COLOR_BG)

        #self.window.protocol("WM_DELETE_WINDOW", self.on_exit)
        self.main_frame = MainFrame(self.window)
        self.main_frame.pack(side="top", fill="both", expand=True)

        # Dummy buttons simulate input
        self.frame = tk.Frame(
            self.window,
            bg=const.COLOR_BG
        )
        self.frame.pack(
            side="bottom",
            fill="x",
            expand=False,
            pady=15
        )

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

    def run(self):
        self.show_main_page()
        self.window.mainloop()

    def s1(self):
        SV.sensor_detected = True

    def s0(self):
        SV.sensor_detected = False

    def confirm(self):
        SV.payment_received = True

    def show_main_page(self):
        self.set_usd_rate()
        self.main_frame.welcome_page.lift()
        SV.E_thankyou_page.set()
    #***************************************************************************

    def show_parked_page(self):
        self.main_frame.parked_page.lift()

    def show_pay_page(self):
        self.main_frame.pay_page.lift()

    def show_paid_page(self):
    #***************************************************************************
        SV.E_thankyou_page.clear()
        self.main_frame.paid_page.lift()
        #-----------------------------------------------------------------------
        # THREAD: Show Payment Received Page
        SV.threads['thank_you_page'] = threading.Timer(2, self.show_main_page)
        SV.threads['thank_you_page'].start()

    def set_pay_text(self, amount, time):
        res = requests.get(const.EXCHANGE_RATE_API).json()
        USD_per_BTC = float(res['last'])
        amount_usd = USD_per_BTC * amount
        self.main_frame.pay_page.amount_due_usd.set("($%.6f)" % amount_usd)
        self.main_frame.pay_page.amount_due.set("%.6f BTC" % amount)
        self.main_frame.pay_page.amount_due.set("%.6f BTC" % amount)
        self.main_frame.pay_page.time_parked.set("%.2f seconds" % time)

    def set_usd_rate(self):
        res = requests.get(const.EXCHANGE_RATE_API).json()
        USD_per_BTC = float(res['last'])
        rate_float_hr = const.PARKING_RATE * USD_per_BTC * 3600.0
        text = "($%.6f / hr)" % rate_float_hr
        self.main_frame.welcome_page.parking_rate_usd.set(text)

    def quit(self, instance=None):
        self.window.destroy()
        SV.KILL = True

    def call_admin(self):
        # send email
        self.call_admin_btn.pack_forget()
        self.help_otw_btn.pack()

        SV.threads['help_btn'] = threading.Timer(
            10,
            self.revert_call_admin_btn
        )
        SV.threads['help_btn'].start()

    def revert_call_admin_btn(self):
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
        #parking_rate = "%.5f BTC / hour" % const.PARKING_RATE
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
        self.amount_due = tk.StringVar()
        self.time_parked = tk.StringVar()
        self.amount_due_usd = tk.StringVar()
        self.config(bg=const.COLOR_BG)
        #self.img = ImageTk.PhotoImage(file="./assets/QR.png")
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
