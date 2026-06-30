#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32MultiArray
from adafruit_servokit import ServoKit
import time

kit1 = ServoKit(channels = 16, address = 0x41) #, reference_clock_speed = 24723456)
kit2 = ServoKit(channels = 16, address = 0x40) #, reference_clock_speed = 24985600)

for i in range (9):
    kit1.servo[i].set_pulse_width_range(320, 2320)
    kit2.servo[15-i].set_pulse_width_range(400, 2400)


class MyNode(Node):
    def __init__(self):
        super().__init__("stop_gait_node")
        self.subscriber_angle = self.create_subscription(Int32MultiArray, "/stop_angle_", self.move, 1)

    def move(self, message = Int32MultiArray):
        kit1.servo[8].angle = message.data[3] #coxa1
        kit1.servo[7].angle = message.data[4] #femur1
        kit1.servo[6].angle = 180 - message.data[5] #tibia1

        kit2.servo[7].angle = 180 - message.data[3] #coxa6
        kit2.servo[8].angle = 180 - message.data[4] #femur6
        kit2.servo[9].angle = message.data[5] #tibia6

        kit1.servo[5].angle = message.data[0] #coxa2
        kit1.servo[4].angle = message.data[1] #femur2
        kit1.servo[3].angle = 180 - message.data[2] #tibia2

        kit2.servo[10].angle = 180 - message.data[0] #coxa5
        kit2.servo[11].angle = 180 - message.data[1] #femur5
        kit2.servo[12].angle = message.data[2] #tibia5

        kit1.servo[2].angle = message.data[6] #coxa3
        kit1.servo[1].angle = message.data[7] #femur3
        kit1.servo[0].angle = 180 - message.data[8] #tibia3

        kit2.servo[13].angle = 180 - message.data[6] #coxa4
        kit2.servo[14].angle = 180 - message.data[7] #femur4
        kit2.servo[15].angle = message.data[8] #tibia4

def main(args=None):
    rclpy.init(args=args)
    node = MyNode()
    rclpy.spin(node)
    rclpy.shutdown()
