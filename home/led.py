import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

flag = 0
GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # Button with pull-down resistor
GPIO.setup(23, GPIO.OUT)  # LED

while True:
    GPIO.output(23, GPIO.HIGH)
    time.sleep(1)
    GPIO.output(23, GPIO.LOW)
    time.sleep(1)
