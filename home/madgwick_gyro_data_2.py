#!/usr/bin/env python3

import sys
sys.path.append('../../')

import time
import numpy as np

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray

from DFRobot_BMX160 import BMX160
from ahrs.filters import Madgwick
from scipy.spatial.transform import Rotation as R


# -------------------------------------------------
# IMU Calibration
# -------------------------------------------------

def calculate_IMU_error():

    c = 0

    AccelErrorX = 0
    AccelErrorY = 0
    AccelErrorZ = 0

    GyroErrorX = 0
    GyroErrorY = 0
    GyroErrorZ = 0

    while c < 200:

        data = bmx.get_all_data()

        GyroErrorX += data[3]
        GyroErrorY += data[4]
        GyroErrorZ += data[5]

        AccelErrorX += data[6]
        AccelErrorY += data[7]
        AccelErrorZ += data[8]

        c += 1

    return (
        GyroErrorX / 200,
        GyroErrorY / 200,
        GyroErrorZ / 200,
        AccelErrorX / 200,
        AccelErrorY / 200,
        AccelErrorZ / 200,
    )


# -------------------------------------------------
# Continuous yaw
# -------------------------------------------------

def unwrap_yaw(prev_yaw, current_yaw):

    delta = current_yaw - prev_yaw

    if delta > 180:
        delta -= 360
    elif delta < -180:
        delta += 360

    return prev_yaw + delta


# -------------------------------------------------
# ROS2 Node
# -------------------------------------------------

class IMUPublisher(Node):

    def __init__(self):

        super().__init__("imu_publisher")

        self.publisher = self.create_publisher(
            Float32MultiArray,
            "/rpy",
            10
        )

        self.timer = self.create_timer(
            0.02,
            self.update
        )


    def update(self):

        global q
        global previous_time
        global prev_yaw

        data = bmx.get_all_data()

        acc = np.array([
            data[6] - IMUAX,
            data[7] - IMUAY,
            9.8066501 + data[8] - IMUAZ
        ])

        gyr = np.radians(np.array([
            data[3] - IMUX,
            data[4] - IMUY,
            data[5] - IMUZ
        ]))

        current_time = time.perf_counter()

        q = madgwick.updateIMU(
            q=q,
            acc=acc,
            gyr=gyr,
            dt=current_time - previous_time
        )

        previous_time = current_time

        if q is None:
            return

        r = R.from_quat([
            q[1],
            q[2],
            q[3],
            q[0]
        ])

        roll, pitch, yaw = r.as_euler(
            'xyz',
            degrees=True
        )

        # Continuous yaw
        yaw = unwrap_yaw(prev_yaw, yaw)
        prev_yaw = yaw

        # Convert to 0~360 degrees
        yaw = yaw % 360

        msg = Float32MultiArray()

        msg.data = [
            float(roll),
            float(pitch),
            float(yaw)
        ]

        self.publisher.publish(msg)

        print(
            f"\r"
            f"Roll:{roll:7.2f}°   "
            f"Pitch:{pitch:7.2f}°   "
            f"Yaw:{yaw:7.2f}°",
            end="",
            flush=True
        )


# -------------------------------------------------
# Initialize Sensor
# -------------------------------------------------

bmx = BMX160(1)

while not bmx.begin():
    time.sleep(2)

print("BMX160 Connected")

q = np.array([1.0, 0.0, 0.0, 0.0])

madgwick = Madgwick()

IMUX, IMUY, IMUZ, IMUAX, IMUAY, IMUAZ = calculate_IMU_error()

prev_yaw = 0.0

previous_time = time.perf_counter()


# -------------------------------------------------
# Main
# -------------------------------------------------

def main(args=None):

    rclpy.init(args=args)

    node = IMUPublisher()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    node.destroy_node()

    rclpy.shutdown()


if __name__ == "__main__":
    main()