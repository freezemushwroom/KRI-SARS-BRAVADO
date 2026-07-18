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


class IMUPublisher(Node):

    def __init__(self):

        super().__init__("imu_publisher")

        self.publisher = self.create_publisher(
            Float32MultiArray,
            "/rpy",
            10
        )

        # ----------------------------
        # Initialize IMU
        # ----------------------------

        self.bmx = BMX160(1)

        while not self.bmx.begin():
            self.get_logger().info("Waiting for BMX160...")
            time.sleep(2)

        self.get_logger().info("BMX160 Connected")

        self.q = np.array([1.0, 0.0, 0.0, 0.0])

        self.madgwick = Madgwick()

        (
            self.IMUX,
            self.IMUY,
            self.IMUZ,
            self.IMUAX,
            self.IMUAY,
            self.IMUAZ,
        ) = self.calculate_IMU_error()

        self.prev_yaw = 0.0

        self.previous_time = time.perf_counter()

        # 50 Hz
        self.timer = self.create_timer(0.02, self.update_imu)

    # --------------------------------------------------

    def calculate_IMU_error(self):

        AccelErrorX = 0
        AccelErrorY = 0
        AccelErrorZ = 0

        GyroErrorX = 0
        GyroErrorY = 0
        GyroErrorZ = 0

        for _ in range(200):

            data = self.bmx.get_all_data()

            GyroErrorX += data[3]
            GyroErrorY += data[4]
            GyroErrorZ += data[5]

            AccelErrorX += data[6]
            AccelErrorY += data[7]
            AccelErrorZ += data[8]

        return (
            GyroErrorX / 200,
            GyroErrorY / 200,
            GyroErrorZ / 200,
            AccelErrorX / 200,
            AccelErrorY / 200,
            AccelErrorZ / 200,
        )

    # --------------------------------------------------

    def unwrap_yaw(self, prev_yaw, current_yaw):

        delta = current_yaw - prev_yaw

        if delta > 180:
            delta -= 360
        elif delta < -180:
            delta += 360

        return prev_yaw + delta

    # --------------------------------------------------

    def update_imu(self):

        data = self.bmx.get_all_data()

        acc = np.array([
            data[6] - self.IMUAX,
            data[7] - self.IMUAY,
            9.80665 + data[8] - self.IMUAZ
        ])

        gyr = np.radians(np.array([
            data[3] - self.IMUX,
            data[4] - self.IMUY,
            data[5] - self.IMUZ
        ]))

        current_time = time.perf_counter()

        dt = current_time - self.previous_time

        self.previous_time = current_time

        self.q = self.madgwick.updateIMU(
            q=self.q,
            acc=acc,
            gyr=gyr,
            dt=dt
        )

        if self.q is None:
            return

        r = R.from_quat([
            self.q[1],
            self.q[2],
            self.q[3],
            self.q[0]
        ])

        roll, pitch, yaw = r.as_euler(
            'xyz',
            degrees=True
        )

        yaw = self.unwrap_yaw(self.prev_yaw, yaw)

        self.prev_yaw = yaw

        msg = Float32MultiArray()

        msg.data = [
            float(roll),
            float(pitch),
            float(yaw)
        ]

        self.publisher.publish(msg)

        print(
            f"\rRoll:{roll:7.2f}°   "
            f"Pitch:{pitch:7.2f}°   "
            f"Yaw:{yaw:8.2f}°",
            end="",
            flush=True
        )


# --------------------------------------------------

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