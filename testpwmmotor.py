from time import sleep
import RPi.GPIO as GPIO


motor1a = 15
motor1b = 13
motor1e = 11

GPIO.setmode(GPIO.BOARD)
GPIO.setup(motor1a, GPIO.OUT)
GPIO.setup(motor1b, GPIO.OUT)
GPIO.setup(motor1e, GPIO.OUT)

print("Going up")
GPIO.output(motor1a, GPIO.HIGH)
GPIO.output(motor1b, GPIO.LOW)
GPIO.output(motor1e, GPIO.HIGH)
sleep(2)
GPIO.output(motor1e, GPIO.LOW)
sleep(3)

print("Going down")
GPIO.output(motor1a, GPIO.LOW)
GPIO.output(motor1b, GPIO.HIGH)
GPIO.output(motor1e, GPIO.HIGH)
sleep(2)
GPIO.output(motor1e, GPIO.LOW)

GPIO.cleanup()
