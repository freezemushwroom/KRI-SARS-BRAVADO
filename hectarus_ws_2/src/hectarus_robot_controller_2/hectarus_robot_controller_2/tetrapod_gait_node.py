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

kit1 = ServoKit(channels = 16, address = 0x41) #, reference_clock_speed = 24723456)
kit2 = ServoKit(channels = 16, address = 0x40) #, reference_clock_speed = 24985600)

for i in range (9):
    kit1.servo[i].set_pulse_width_range(320, 2320)
    kit2.servo[15-i].set_pulse_width_range(400, 2400)


#delay = 0.2

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
        super().__init__("tetrapod_gait_node")
        self.subscriber_angle = self.create_subscription(Int32MultiArray, "/tetrapod_angle_", self.move, 1)

    def move(self, message = Int32MultiArray):
        rows = message.layout.dim[0].size
        cols = message.layout.dim[1].size
        data = np.array(message.data).reshape(rows, cols)
        self.get_logger().info(f"Data: {data}")

        delay = (0.4*(data[3][17]))-0.2
#        delay = 1
        #femur 1 4 angkat
        kit1.servo[7].angle = max(0, min((data[3][4] + 45), 180)) #femur1
        kit2.servo[14].angle = max(0, min((180 - data[3][7] - 45), 180)) #femur4
        kit1.servo[6].angle = max(0, min((180 - data[3][5] + 45), 180)) #tibia1
        kit2.servo[15].angle = max(0, min((data[3][8] - 45), 180)) #tibia4
        wait(delay)

        #coxa 1 4 maju sisanya mundur
        kit1.servo[8].angle = max(0, min((90 + data[0][3]), 180)) #coxa1
        kit2.servo[13].angle = max(0, min((90 + data[3][9] - data[0][6+9]), 180)) #coxa4

        kit2.servo[7].angle = max(0, min((90 - data[1][3+9]), 180)) #coxa6
        kit2.servo[8].angle = max(0, min((180 - data[3][4] - data[1][4+9]), 180)) #femur6
        kit2.servo[9].angle = max(0, min((data[3][5] + data[1][5+9]), 180)) #tibia6

        kit1.servo[5].angle = max(0, min((90 + data[1][0]), 180)) #coxa2
        kit1.servo[4].angle = max(0, min((data[3][1] + data[1][1]), 180)) #femur2
        kit1.servo[3].angle = max(0, min((180 - data[3][2] - data[1][2]), 180)) #tibia2

        kit2.servo[10].angle = max(0, min((90 - data[2][0+9]), 180)) #coxa5
        kit2.servo[11].angle = max(0, min((180 - data[3][1] - data[2][1+9]), 180)) #femur5
        kit2.servo[12].angle = max(0, min((data[3][2] + data[2][2+9]), 180)) #tibia5

        kit1.servo[2].angle = max(0, min((90 - data[3][9] + data[2][6]), 180)) #coxa3
        kit1.servo[1].angle = max(0, min((data[3][7] + data[2][7]), 180)) #femur3
        kit1.servo[0].angle = max(0, min((180 - data[3][8] - data[2][8]), 180)) #tibia3


        #femur 1 4 turun dan tibia turun sekalian adjust ngambil kaki
        kit1.servo[6].angle = max(0, min((180 - data[3][5] - data[0][5]), 180)) #tibia1
        kit2.servo[15].angle = max(0, min((data[3][8] + data[0][8+9]), 180)) #tibia4
        wait(0.1)
        kit1.servo[7].angle = max(0, min((data[3][4] + data[0][4]), 180)) #femur1
        kit2.servo[14].angle = max(0, min((180 - data[3][7] - data[0][7+9]), 180)) #femur4
        wait(delay)

        #femur tibia 3 5 naik
        kit1.servo[1].angle = max(0, min((data[3][7] + 45), 180)) #femur3
        kit2.servo[11].angle = max(0, min((180 - data[3][1] - 45), 180)) #femur5
        kit1.servo[0].angle = max(0, min((180 - data[3][8] + 45), 180)) #tibia3
        kit2.servo[12].angle = max(0, min((data[3][2] - 45), 180)) #tibia5
        wait(delay)

 	#coxa 3 5 maju sisanya mundur
        kit1.servo[8].angle = max(0, min((90 + data[1][3]), 180)) #coxa1
        kit1.servo[7].angle = max(0, min((data[3][4] + data[1][4]), 180)) #femur1
        kit1.servo[6].angle = max(0, min((180 - data[3][5] - data[1][5]), 180)) #tibia1

        kit2.servo[7].angle = max(0, min((90 - data[2][3+9]), 180)) #coxa6
        kit2.servo[8].angle = max(0, min((180 - data[3][4] - data[2][4+9]), 180)) #femur6
        kit2.servo[9].angle = max(0, min((data[3][5] + data[2][5+9]), 180)) #tibia6

        kit1.servo[5].angle = max(0, min((90 + data[2][0]), 180)) #coxa2
        kit1.servo[4].angle = max(0, min((data[3][1] + data[2][1]), 180)) #femur2
        kit1.servo[3].angle = max(0, min((180 - data[3][2] - data[2][2]), 180)) #tibia2

        kit1.servo[2].angle = max(0, min((90 - data[3][9] + data[0][6]), 180)) #coxa3
        kit2.servo[10].angle = max(0, min((90 - data[0][0+9]), 180)) #coxa5

        kit2.servo[13].angle = max(0, min((90 + data[3][9] - data[1][6+9]), 180)) #coxa4
        kit2.servo[14].angle = max(0, min((180 - data[3][7] - data[1][7+9]), 180)) #femur4
        kit2.servo[15].angle = max(0, min((data[3][8] + data[1][8+9]), 180)) #tibia4

	#femur tibia 3 turun
        kit1.servo[0].angle = max(0, min((180 - data[3][8] - data[0][8]), 180)) #tibia3
        kit2.servo[12].angle = max(0, min((data[3][2] + data[0][2+9]), 180)) #tibia5
        wait(0.1)
        kit1.servo[1].angle = max(0, min((data[3][7] + data[0][7]), 180)) #femur3
        kit2.servo[11].angle = max(0, min((180 - data[3][1] - data[0][1+9]), 180)) #femur5
        wait(delay)

        #femur 2 6 angkat
        kit1.servo[4].angle = max(0, min((data[3][1] + 45), 180)) #femur2
        kit2.servo[8].angle = max(0, min((180 - data[3][4] - 45), 180)) #femur6
        kit1.servo[3].angle = max(0, min((180 - data[3][2] + 45), 180)) #tibia2
        kit2.servo[9].angle = max(0, min((data[3][5] - 45), 180)) #tibia6
        wait(delay)

        #coxa 2 6 maju sisanya mundur
        kit1.servo[8].angle = max(0, min((90 + data[2][3]), 180)) #coxa1
        kit1.servo[7].angle = max(0, min((data[3][4] + data[2][4]), 180)) #femur1
        kit1.servo[6].angle = max(0, min((180 - data[3][5] - data[2][5]), 180)) #tibia1

        kit1.servo[5].angle = max(0, min((90 + data[0][0]), 180)) #coxa2
        kit2.servo[7].angle = max(0, min((90 - data[0][3+9]), 180)) #coxa6

        kit2.servo[10].angle = max(0, min((90 - data[1][0+9]), 180)) #coxa5
        kit2.servo[11].angle = max(0, min((180 - data[3][1] - data[1][1+9]), 180)) #femur5
        kit2.servo[12].angle = max(0, min((data[3][2] + data[1][2+9]), 180)) #tibia5

        kit1.servo[2].angle = max(0, min((90 - data[3][9] + data[1][6]), 180)) #coxa3
        kit1.servo[1].angle = max(0, min((data[3][7] + data[1][7]), 180)) #femur3
        kit1.servo[0].angle = max(0, min((180 - data[3][8] - data[1][8]), 180)) #tibia3

        kit2.servo[13].angle = max(0, min((90 + data[3][9] - data[2][6+9]), 180)) #coxa4
        kit2.servo[14].angle = max(0, min((180 - data[3][7] - data[2][7+9]), 180)) #femur4
        kit2.servo[15].angle = max(0, min((data[3][8] + data[2][8+9]), 180)) #tibia4

	#femur tibia 2 turun
        kit1.servo[3].angle = max(0, min((180 - data[3][2] - data[0][2]), 180)) #tibia2
        kit2.servo[9].angle = max(0, min((data[3][5] + data[0][5+9]), 180)) #tibia6
        wait(0.1)
        kit1.servo[4].angle = max(0, min((data[3][1] + data[0][1]), 180)) #femur2
        kit2.servo[8].angle = max(0, min((180 - data[3][4] - data[0][4+9]), 180)) #femur6
        wait(delay)

def main(args=None):
    rclpy.init(args=args)
    node = MyNode()
    rclpy.spin(node)
    rclpy.shutdown()
