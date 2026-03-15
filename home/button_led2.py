import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

flag = 0
GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # Button with pull-down resistor
GPIO.setup(23, GPIO.OUT)  # LED

while True:
    if GPIO.input(18) == 1:  # Button is pressed
        time.sleep(0.02)  # Debounce delay (20 ms)
        if GPIO.input(18) == 1:  # Check again after debounce
            if flag == 0:
                GPIO.output(23, GPIO.HIGH)
                print("LED On")
                flag = 1
                while GPIO.input(18) == 1:  # Wait until the button is released
                    time.sleep(0.01)
            else:
                GPIO.output(23, GPIO.LOW)
                print("LED Off")
                flag = 0
                while GPIO.input(18) == 1:  # Wait until the button is released
                    time.sleep(0.01)
