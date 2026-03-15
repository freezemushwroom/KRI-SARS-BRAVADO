from time import sleep
from adafruit_servokit import ServoKit


kit1 = ServoKit(channels = 16, address = 0x41)
kit2 = ServoKit(channels = 16, address = 0x40)


#femur naik
kit1.servo[7].angle = 180 #femur1
sleep(2)
kit1.servo[7].angle = 140
sleep(1)
kit2.servo[8].angle = 0 #femur6
sleep(2)
kit2.servo[8].angle = 40
sleep(1)
kit1.servo[1].angle = 180 #femur3
sleep(2)
kit1.servo[1].angle = 140
sleep(1)
kit2.servo[14].angle = 0 #femur4
sleep(2)
kit2.servo[14].angle = 40






