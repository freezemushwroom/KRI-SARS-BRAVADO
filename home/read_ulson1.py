import time
import RPi.GPIO as GPIO
import pygame
import rclpy

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

#depan = 0, kanan = 1, kiri = 2, belakang = 3 
TRIG = [19, 6, 22, 17, 21, 16, 25]
ECHO = [26, 13, 5, 27, 20, 12, 24]
for i in range (0,7):
    GPIO.setup(TRIG[i],GPIO.OUT)
    GPIO.output(TRIG[i], False)
    GPIO.setup(ECHO[i],GPIO.IN)

jarak = [0, 0, 0, 0]

def ultrasonic(TRIG, ECHO):
    timeout = 100
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)
    pulse_start = time.time()
    time_timeout = time.time()
    while GPIO.input(ECHO)==0:
        if ((time.time() - time_timeout) *1000) > timeout:
            distance = 30
            return distance
        pulse_start = time.time()

    while GPIO.input(ECHO)==1:
        if ((time.time() - time_timeout) *1000) > timeout:
            distance = 30
            return distance
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150
    distance = round(distance, 2)
    return distance

try:
    while True:
        #print(f"depan = {ultrasonic(TRIG[0], ECHO[0])} cm, kanan = {ultrasonic(TRIG[1], ECHO[1])} cm, kiri = {ultrasonic(TRIG[2], ECHO[2])} cm, belakang = {ultrasonic(TRIG[3], ECHO[3])} cm")
        get_logger().info(f"depan = {ultrasonic(TRIG[0], ECHO[0])} cm, kanan = {ultrasonic(TRIG[1], ECHO[1])} cm, kiri = {ultrasonic(TRIG[2], ECHO[2])} cm, belakang = {ultrasonic(TRIG[3], ECHO[3])} cm")
        #

except KeyboardInterrupt:
    print("\nStopped")

