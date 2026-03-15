import RPi.GPIO as GPIO
import time
import board
import busio
import adafruit_vl53l0x

#i2c = busio.I2C(board.SCL, board.SDA)
#vl53 = adafruit_vl53l0x.VL53L0X(i2c, 41)


GPIO.setmode(GPIO.BCM)

def ultrasonic(TRIG, ECHO):
    timeout = 100
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)
    pulse_start = time.time()
    while GPIO.input(ECHO)==0:
        if ((time.time() - pulse_start)*1000) > timeout:
            distance = 30
            return distance
        pulse_start = time.time()

    while GPIO.input(ECHO)==1:
        pulse_end = time.time()   
    
    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150
    distance = round(distance, 2)
    return distance

TRIG = [19, 6, 22, 17, 21, 16, 25]
ECHO = [26, 13, 5, 27, 20, 12, 24]
us = [0,0,0,0,0,0,0]
for i in range (0,7):
    GPIO.setup(TRIG[i], GPIO.OUT)
    GPIO.output(TRIG[i], False)
    GPIO.setup(ECHO[i], GPIO.IN)


try:
    while True:
        for i in range (0,7):
#            if i != 1 and i != 3 and i != 4 and i != 6: #and i != 2 and i != 5:
            us[i] = ultrasonic(TRIG[i], ECHO[i])
            print("Distance Ultrasonik " + str(i+1) + ": " + str(us[i]) + " cm")
            time.sleep(0.01)
#        print("Distance Time of Flight: {0} cm".format(vl53.range/10))
        time.sleep(1)
        print ("")
except KeyboardInterrupt:
    GPIO.cleanup()
