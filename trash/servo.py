from time import sleep
from adafruit_servokit import ServoKit


kit1 = ServoKit(channels = 16, address = 0x41)
kit2 = ServoKit(channels = 16, address = 0x40)

kit2.servo[14].angle = 0


