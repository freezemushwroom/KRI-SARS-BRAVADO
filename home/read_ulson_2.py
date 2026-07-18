#!/usr/bin/env python3

import time

import RPi.GPIO as GPIO

import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32MultiArray


# ===============================
# GPIO Configuration
# ===============================

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

TRIG = [19, 6, 22, 17, 21, 16, 23]
ECHO = [26, 13, 5, 25, 20, 12, 24]

SENSOR_NAMES = [
    "Left Front",
    "Left",
    "Left Rear",
    "Rear",
    "Right Front",
    "Right",
    "Front"
]

NUM_SENSORS = len(TRIG)

for i in range(NUM_SENSORS):
    GPIO.setup(TRIG[i], GPIO.OUT)
    GPIO.output(TRIG[i], False)

    GPIO.setup(ECHO[i], GPIO.IN)

time.sleep(2)


# ===============================
# Ultrasonic Function
# ===============================

def ultrasonic(trig, echo):

    timeout_ms = 100

    GPIO.output(trig, True)
    time.sleep(0.00001)
    GPIO.output(trig, False)

    pulse_start = time.time()
    pulse_end = time.time()

    timeout = time.time()

    while GPIO.input(echo) == 0:
        pulse_start = time.time()

        if (time.time() - timeout) * 1000 > timeout_ms:
            return -1

    while GPIO.input(echo) == 1:
        pulse_end = time.time()

        if (time.time() - timeout) * 1000 > timeout_ms:
            return -1

    pulse_duration = pulse_end - pulse_start

    distance = pulse_duration * 17150

    return round(distance, 2)


# ===============================
# ROS2 Node
# ===============================

class UltrasonicReader(Node):

    def __init__(self):
        super().__init__("ultrasonic_reader")

        self.publisher = self.create_publisher(
            Int32MultiArray,
            "/ultrasonic",
            10
        )

        # Read every 0.2 seconds
        self.timer = self.create_timer(0.2, self.read_sensors)

    def read_sensors(self):

        distances = []

        for i in range(NUM_SENSORS):

            distance = ultrasonic(TRIG[i], ECHO[i])
            distances.append(int(distance))

            # Small delay to reduce ultrasonic cross-talk
            time.sleep(0.02)

        msg = Int32MultiArray()
        msg.data = distances
        self.publisher.publish(msg)

        # Print horizontally
        print(
            f"LF:{distances[0]:3}  "
            f"L:{distances[1]:3}  "
            f"LR:{distances[2]:3}  "
            f"R:{distances[3]:3}  "
            f"RF:{distances[4]:3}  "
            f"RR:{distances[5]:3}  "
            f"F:{distances[6]:3}"
        )


# ===============================
# Main
# ===============================

def main(args=None):

    rclpy.init(args=args)

    node = UltrasonicReader()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    finally:
        GPIO.cleanup()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()