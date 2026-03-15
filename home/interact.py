import time
import RPi.GPIO as GPIO
from adafruit_servokit import ServoKit
import board
import busio

kit1 = ServoKit(channels = 16, address = 0x41) #, reference_clock_speed = 24723456)
kit2 = ServoKit(channels = 16, address = 0x40) #, reference_clock_speed = 24985600)

for i in range (10):
    kit1.servo[i].set_pulse_width_range(320, 2320)
    kit2.servo[15-i].set_pulse_width_range(400, 2400)

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.BUTTON = 18
GPIO.LED = 23

GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  #Button
GPIO.setup(23, GPIO.OUT)  # LED
GPIO.output(23, GPIO.LOW)

def berdiri():
    kit1.servo[8].angle = 90 #coxa1
    kit2.servo[7].angle = 90 #coxa6
    kit1.servo[5].angle = 90 #coxa2
    kit2.servo[10].angle = 90 #coxa5
    kit1.servo[2].angle = 90 #coxa3
    kit2.servo[13].angle = 90 #coxa4

    kit1.servo[7].angle = 125 #femur1 125
    kit2.servo[8].angle = 55 #femur6 55
    kit1.servo[4].angle = 125 #125
    kit2.servo[11].angle = 55 #femur5 55
    kit1.servo[1].angle = 125 #femur3 125
    kit2.servo[14].angle = 55 #femur4 55

    kit1.servo[6].angle = 135 #tibia1 135
    kit2.servo[9].angle = 45 #tibia6 45
    kit1.servo[3].angle = 135 #tibia2 135
    kit2.servo[12].angle = 45 #tibia5 45
    kit1.servo[0].angle = 135 #tibia3 135
    kit2.servo[15].angle = 45 #tibia4 45
    wait(0.5)


def wait(waktu):
    flag = True
    myTime = time.time()
    while flag == True:
        currentTime = time.time()
        if currentTime - myTime < waktu:
            flag = True
        elif currentTime - myTime >= waktu:
            flag = False

TRIG = [19, 6, 22, 17, 21, 16, 25]
ECHO = [26, 13, 5, 27, 20, 12, 24]
for i in range (0,7):
    GPIO.setup(TRIG[i],GPIO.OUT)
    GPIO.output(TRIG[i], False)
    GPIO.setup(ECHO[i],GPIO.IN)

def ultrasonic(TRIG, ECHO):
    timeout = 100
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)
    pulse_start = time.time()
    time_timeout = time.time()
    while GPIO.input(ECHO)==0:
        pulse_start = time.time()

    while GPIO.input(ECHO)==1:
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150
    distance = round(distance, 2)
    return distance
flag_kaki = 0
flag = 1
print("Interact OFF")
berdiri()

while True:
    if GPIO.input(18)==1:
        wait(0.02)
        if flag == 0:
            print("Interact ON")
            GPIO.output(23, GPIO.HIGH)
            flag = 1
            while GPIO.input(18) == 1:
                wait(0.01)
        else:
            print("Interact OFF")
            GPIO.output(23, GPIO.LOW)
            flag = 0
            while GPIO.input(18) == 1:
                wait(0.01)
    if flag == 1:
        jarak_depan = ultrasonic(TRIG[0], ECHO[0])
        jarak_kanan = ultrasonic(TRIG[5], ECHO[5])
        jarak_kiri = ultrasonic(TRIG[2], ECHO[2])

        if jarak_depan < 60:
            if flag_kaki == 0:
                print("Hallo! (Right)")
                flag_kaki = 1
                kit2.servo[8].angle = 20 #femur6
                kit2.servo[9].angle = 60
                kit2.servo[7].angle = 60 #coxa6
                wait(0.5)
                kit2.servo[8].angle = 40 #femur6
                kit2.servo[9].angle = 10
                wait(0.2)
                kit2.servo[8].angle = 20 #femur6
                kit2.servo[9].angle = 60
                wait(0.2)
                kit2.servo[8].angle = 40 #femur6
                kit2.servo[9].angle = 10
                wait(0.2)
                kit2.servo[8].angle = 20 #femur6
                kit2.servo[9].angle = 60
                wait(1)
                berdiri()
            elif flag_kaki == 1:
                print("Hallo! (Left)")
                flag_kaki = 0
                kit1.servo[7].angle = 160 #femur 1
                kit1.servo[6].angle = 120 #tibia1
                kit1.servo[8].angle = 120 #coxa1
                wait(0.5)
                kit1.servo[7].angle = 140
                kit1.servo[6].angle = 170
                wait(0.2)
                kit1.servo[7].angle = 160
                kit1.servo[6].angle = 120
                wait(0.2)
                kit1.servo[7].angle = 140
                kit1.servo[6].angle = 170
                wait(0.2)
                kit1.servo[7].angle = 160
                kit1.servo[6].angle = 120
                wait(1)
                berdiri()

        elif jarak_kanan >  8.5 and jarak_kanan < 11:
            print("Left")
            kit1.servo[4].angle = 150
            kit1.servo[3].angle = 160
            wait(0.2)
            kit1.servo[4].angle = 130
            kit1.servo[3].angle = 90
            wait(0.2)
            kit1.servo[4].angle = 150
            kit1.servo[3].angle = 160
            wait(0.2)
            kit1.servo[4].angle = 130
            kit1.servo[3].angle = 90
            wait(0.4)
            berdiri()
        elif jarak_kiri > 8.5 and jarak_kiri < 11:
            print("Right")
            kit2.servo[11].angle = 30
            kit2.servo[12].angle = 25
            wait(0.2)
            kit2.servo[11].angle = 50
            kit2.servo[12].angle = 95
            wait(0.2)
            kit2.servo[11].angle = 30
            kit2.servo[12].angle = 25
            wait(0.2)
            kit2.servo[11].angle = 50
            kit2.servo[12].angle = 95
            wait(0.4)
            berdiri()
