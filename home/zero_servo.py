from time import sleep
from adafruit_servokit import ServoKit
import time

kit1 = ServoKit(channels = 16, address = 0x41, reference_clock_speed = 24930632)
kit2 = ServoKit(channels = 16, address = 0x40) #, reference_clock_speed = 24985600)
flag = 0
i = 0

for i in range (9):
    kit1.servo[i].set_pulse_width_range(320, 2320)
    kit2.servo[15-i].set_pulse_width_range(400, 2400)


while True:
    input_var = input("Input Key: ")
#    kit2.servo[10].angle = 90
#    print("Servo ke " + str(60+i) + " derajat")
#    i = i+1
    if flag == 0:
        kit2.servo[9].angle = 0
        print("Servo ke 0 derajat")
        flag = 1
    elif flag == 1:
        kit2.servo[9].angle = 90
        print("Servo ke 90 derajat")
        flag = 2
    elif flag == 2:
        kit2.servo[9].angle = 80
        print("Servo ke 180 derajat")
        flag = 0
