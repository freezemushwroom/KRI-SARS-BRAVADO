#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from std_msgs.msg import Int32MultiArray
from std_msgs.msg import Int32
import time

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
        super().__init__("count_time_node")
        self.subscriber_count = self.create_subscription(Int32, "/count_time_", self.count_time, 1)

        self.startTime = 0
        self.currentTime = 0
        self.flag = 0

    def count_time(self, message:Int32):
        if self.flag == 0:
            self.get_logger().info("Start Counting...")
            self.startTime = time.time()
            self.flag = 1
        else:
            self.currentTime = time.time()
            self.get_logger().info("Time Elapsed : " + str(self.currentTime - self.startTime) + " second")
            self.flag = 0

def main(args=None):
    rclpy.init(args=args)
    node = MyNode()
    rclpy.spin(node)
    rclpy.shutdown()
