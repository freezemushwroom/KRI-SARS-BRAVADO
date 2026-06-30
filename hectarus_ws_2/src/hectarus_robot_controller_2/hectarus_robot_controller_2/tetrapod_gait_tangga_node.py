#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from std_msgs.msg import Int32MultiArray
from std_msgs.msg import Int32
import math
from adafruit_servokit import ServoKit
import time
import numpy as np

kit1 = ServoKit(channels = 16, address = 0x41, reference_clock_speed = 24723456)
kit2 = ServoKit(channels = 16, address = 0x40, reference_clock_speed = 24985600)

for i in range (9):
    kit1.servo[i].set_pulse_width_range(320, 2320)
    kit2.servo[15-i].set_pulse_width_range(400, 2400)

delay = 0.6

def wait(waktu):
    flag = True
    myTime = time.time()
    while flag == True:
        currentTime = time.time()
        if currentTime - myTime < waktu:
            flag = True
        elif currentTime - myTime >= waktu:
            flag = False

class MyNode(Node):
    def __init__(self):
        super().__init__("tetrapod_gait_tangga_node")
        self.subscriber_angle = self.create_subscription(Int32MultiArray, "/tetrapod_tangga_angle_", self.move, 1)

    def move(self, message = Int32MultiArray):

        #femur tibia 1 angkat
        kit1.servo[7].angle = max(0, min((message.data[11+9] + 60), 180)) #femur1
        kit1.servo[6].angle = max(0, min((180 - message.data[12+9] + 60), 180)) #tibia1
        #wait(delay)

        #coxa 1 mundur
        kit1.servo[8].angle = max(0, min((90 - 20), 180))

        #tibia 1 naik
        kit1.servo[6].angle = max(0, min((180 - message.data[12+9] - 30), 180))
        wait(0.5)

        #coxa 1 maju
        kit1.servo[8].angle = max(0, min((90 + message.data[3]), 180)) #coxa1
        wait(delay)

        #femur 1 turun
        kit1.servo[6].angle = max(0, min((180 - message.data[12+9] - message.data[5]), 180)) #tibia1
        wait(0.1)
        kit1.servo[7].angle = max(0, min((message.data[11+9] + message.data[4]), 180)) #femur1
        wait(delay)

        #femur tibia 6 angkat
        kit2.servo[8].angle = max(0, min((180 - message.data[11+9] - 60), 180)) #femur6
        kit2.servo[9].angle =  max(0, min((message.data[12+9] - 60), 180)) #tibia6
        wait(delay)

        #coxa 6 mundur
        kit2.servo[7].angle = max(0, min((90 + 20), 180))

        #tibia 6 naik
        kit2.servo[9].angle = max(0, min(((message.data[12+9] + 30), 180)))
        wait(0.5)

        #coxa 6 maju
        kit2.servo[7].angle = max(0, min((90 - message.data[3+9]), 180)) #coxa6
        wait(delay)

        #femur tibia 1 6 turun
        kit2.servo[9].angle = max(0, min((message.data[12+9] + message.data[5+9]), 180)) #tibia6
        wait(0.1)
        kit2.servo[8].angle = max(0, min((180 - message.data[11+9] - message.data[4+9]), 180)) #femur6
        wait(delay)


        #femur tibia 2 5 angkat
        kit1.servo[4].angle = max(0, min((message.data[9+9] + 30), 180)) #femur2
        kit1.servo[3].angle = max(0, min((180 - message.data[10+9] + 30), 180)) #tibia2
        kit2.servo[11].angle = max(0, min((180 - message.data[9+9] - 30), 180)) #femur5
        kit2.servo[12].angle = max(0, min((message.data[10+9] - 30), 180)) #tibia5
        wait(delay)

        #coxa 2 5 maju
        kit1.servo[5].angle = max(0, min((90 + message.data[0]), 180)) #coxa2
        kit2.servo[10].angle = max(0, min((90 - message.data[0+9]), 180)) #coxa5
        wait(delay)

        #femur tibia 2 5 turun
        kit1.servo[3].angle = max(0, min((180 - message.data[10+9] - message.data[2]), 180)) #tibia2
        kit2.servo[12].angle = max(0, min((message.data[10+9] + message.data[2+9]), 180)) #tibia5
        wait(0.05)
        kit1.servo[4].angle = max(0, min((message.data[9+9] + message.data[1]), 180)) #femur2
        kit2.servo[11].angle = max(0, min((180 - message.data[9+9]- message.data[1+9]), 180)) #femur5
        wait(delay)

        #kaki 1 2 5 6 balik ke posisi awal, kaki 3 4 mundur dengan coxa femur tibianya mundur
        kit1.servo[8].angle = 90 #coxa1
        kit1.servo[7].angle = message.data[11+9] #femur1
        kit1.servo[6].angle = 180 - message.data[12+9] #tibia1

        kit1.servo[5].angle = 90 #coxa2
        kit1.servo[4].angle = message.data[9+9] #femur2
        kit1.servo[3].angle = 180 -message.data[10+9] #tibia2

        kit2.servo[10].angle = 90 #coxa5
        kit2.servo[11].angle = 180 - message.data[9+9] #femur5
        kit2.servo[12].angle = message.data[10+9] #tibia5

        kit2.servo[7].angle = 90 #coxa6
        kit2.servo[8].angle = 180 - message.data[11+9] #femur6
        kit2.servo[9].angle = message.data[12+9] #tibia6

        kit1.servo[2].angle = max(0, min((90 - message.data[15+9] + message.data[6]), 180)) #coxa3
        kit1.servo[1].angle = max(0, min((message.data[13+9] + message.data[7]), 180)) #femur3
        kit1.servo[0].angle = max(0, min((180 - message.data[14+9] - message.data[8]), 180)) #tibia3

        kit2.servo[13].angle = max(0, min((90 + message.data[15+9] - message.data[6+9]), 180)) #coxa4
        kit2.servo[14].angle = max(0, min((180 - message.data[13+9] - message.data[7+9]), 180)) #femur4
        kit2.servo[15].angle = max(0, min((message.data[14+9] + message.data[8+9]), 180)) #tibia4
        wait(delay)

        #femur tibia 3 angkat
        kit1.servo[1].angle = max(0, min((message.data[13+9] + 60), 180)) #femur3
        kit1.servo[0].angle = max(0, min((180 - message.data[14+9] + 100), 180)) #tibia3
        wait(0.5)

        #coxa 3 balik ke posisi awal
        kit1.servo[2].angle = 90 - message.data[15+9] #coxa3

        #femur tibia 3 turun ke posisi awal
        kit1.servo[1].angle = message.data[13+9] #femur3
        kit1.servo[0].angle = 180 - message.data[14+9] #tibia3
        wait(delay)

        #femur tibia 4 angkat
        kit2.servo[14].angle = max(0, min((180 - message.data[13+9] - 60), 180)) #femur4
        kit2.servo[15].angle = max(0, min((message.data[14+9] - 100), 180)) #tibia4
        wait(0.5)

        #coxa 4 balik ke posisi awal
        kit2.servo[13].angle = 90 + message.data[15+9] #coxa4

        #femur tibia 4 turun ke posisi awal
        kit2.servo[14].angle = 180 - message.data[13+9] #femur4
        kit2.servo[15].angle = message.data[14+9] #tibia4
        wait(delay+0.2)

def main(args=None):
    rclpy.init(args=args)
    node = MyNode()
    rclpy.spin(node)
    rclpy.shutdown()
