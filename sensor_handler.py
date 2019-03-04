################################################################################
'''
Crypto Parking: Automated bitcoin parking lot
File name: sensor_handler.py
Description:
Author(s): Kass Chupongstimun, kchupong@ucsd.edu
           John So, jyso@ucsd.edu
'''
################################################################################
import threading
import numpy as np
import RPi.GPIO as GPIO
import time

import shared as SV
import const


class SensorHandler:

    def __init__(self):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(const.MOTOR1A, GPIO.OUT)
        GPIO.setup(const.MOTOR1B, GPIO.OUT)
        GPIO.setup(const.MOTOR1E, GPIO.OUT)

        self.counter = 0
        self.stablize_counter = 0
        self.buffer = np.zeros(const.BUFFER_LEN)
        self.sensor_val = False

        GPIO.setup(const.PIN_PROXIMITY_SENSOR, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(const.PIN_OBSTRUCTION_SENSOR, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def gpio_cleanup(self):
        GPIO.cleanup()

    def init_interrupts(self):
        GPIO.add_event_detect(
            const.PIN_PROXIMITY_SENSOR,
            GPIO.BOTH,
            callback=self.wake_detect   # threaded callback
        )

    def wake_detect(self, instance):
        '''
        '''

        print("Detected rising/falling edge, waking up")
        print(GPIO.input(const.PIN_PROXIMITY_SENSOR))
        GPIO.remove_event_detect(const.PIN_PROXIMITY_SENSOR)  # disable interrupts
        self.read_sensor()

    def read_sensor(self):

        # Add current reading to buffer array
        self.buffer[self.counter] = 0 if GPIO.input(const.PIN_PROXIMITY_SENSOR) else 1
        # Increment counter, loop back to first idx in end of buffer
        self.counter = (self.counter + 1) % const.BUFFER_LEN

        # Every 1 second, take the averge of readings in the buffer
        # Set the shared variable to the result
        # If it reads the same value, add to the stablize counter
        if self.counter == 49:
            sensor_val = np.mean(self.buffer) > 0.5  # might change to a different threshold
            if SV.sensor_detected == sensor_val:
                self.stablize_counter += 1
            SV.sensor_detected = sensor_val
            print("sensor reads %d" % sensor_val)

        # If GPIO input stablizes, reset everything and go back to waiting for
        # interrupts on rising/falling edge
        if self.stablize_counter > 20:
            self.buffer = np.zeros(const.BUFFER_LEN)
            self.counter = 0
            self.stablize_counter = 0
            self.init_interrupts()
            print("Sensor value stablized, sleeping...")

        # If GPIO input has not stablized, continue reading values
        # Calls itself again in a thread in 10ms
        else:
            #-------------------------------------------------------------------
            # THREAD: Poll Sensor
            self.t_poll_sensor = threading.Timer(0.005, self.read_sensor)
            self.t_poll_sensor.start()

    # Returns True if there is no obstruction and false otherwise
    def no_obstruction(self):
        return GPIO.input(const.PIN_OBSTRUCTION_SENSOR)

    def block(self):
        print("Blocker coming up...")
        GPIO.output(const.MOTOR1A, GPIO.HIGH)
        GPIO.output(const.MOTOR1B, GPIO.LOW)
        GPIO.output(const.MOTOR1E, GPIO.HIGH)
        time.sleep(1)

        GPIO.output(const.MOTOR1E, GPIO.LOW)
        print("Spot is now blocked")

    def lower(self):
        print("Blocker lowering...")
        GPIO.output(const.MOTOR1A, GPIO.LOW)
        GPIO.output(const.MOTOR1B, GPIO.HIGH)
        GPIO.output(const.MOTOR1E, GPIO.HIGH)
        time.sleep(1)

        GPIO.output(const.MOTOR1E, GPIO.LOW)
        print("Blocker is now lowered")
