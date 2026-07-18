#!/usr/bin/env python3

import time

import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32MultiArray

import RPi.GPIO as GPIO


# ---------------- GPIO Setup ----------------

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

TRIG = [19, 6, 22, 14, 21, 16, 23]
ECHO = [26, 13, 5, 25, 20, 12, 24]
# 1, 2, 3, 4, 5, 6, 7
# kiri depan, kiri, kiri belakang, belakang, kanan depan, kanan, depan

NUM_SENSORS = len(TRIG)

for i in range(NUM_SENSORS):
    GPIO.setup(TRIG[i], GPIO.OUT)
    GPIO.output(TRIG[i], False)

    GPIO.setup(ECHO[i], GPIO.IN)

time.sleep(2)


# ---------------- Ultrasonic Function ----------------

def ultrasonic(trig, echo):

    timeout = 100  # milliseconds

    GPIO.output(trig, True)
    time.sleep(0.00001)
    GPIO.output(trig, False)

    pulse_start = time.time()
    pulse_end = time.time()

    timeout_start = time.time()

    while GPIO.input(echo) == 0:
        pulse_start = time.time()

        if (time.time() - timeout_start) * 1000 > timeout:
            return 300

    while GPIO.input(echo) == 1:
        pulse_end = time.time()

        if (time.time() - timeout_start) * 1000 > timeout:
            return 300

    pulse_duration = pulse_end - pulse_start

    distance = pulse_duration * 17150

    return int(round(distance))


# ---------------- ROS2 Node ----------------

class UltrasonicReader(Node):

    def __init__(self):

        super().__init__("ultrasonic_reader")

        self.publisher = self.create_publisher(
            Int32MultiArray,
            "/ultrasonic",
            10
        )

        # Read every 100 ms
        self.timer = self.create_timer(0.1, self.read_ultrasonic)

    def read_ultrasonic(self):

        distances = []

        for i in range(NUM_SENSORS):

            distance = ultrasonic(TRIG[i], ECHO[i])
            distances.append(distance)

            # Small delay prevents ultrasonic interference
            time.sleep(0.01)

        msg = Int32MultiArray()
        msg.data = distances

        self.publisher.publish(msg)

        self.get_logger().info(
            f"Distances (cm): {distances}"
        )


# ---------------- Main ----------------

def main(args=None):

    rclpy.init(args=args)

    node = UltrasonicReader()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    GPIO.cleanup()

    node.destroy_node()

    rclpy.shutdown()


if __name__ == "__main__":
    main()