#!/usr/bin/env python3

import math
import rclpy
from rclpy.node import Node

from sensor_msgs.msg import Imu
from std_msgs.msg import Float32


class ImuDistanceNode(Node):
    def __init__(self):
        super().__init__('imu_distance_node')

        self.imu_topic = '/hectarus_imu_data'

        self.sub = self.create_subscription(
            Imu,
            self.imu_topic,
            self.imu_callback,
            10
        )

        self.distance_pub = self.create_publisher(
            Float32,
            '/imu_distance',
            10
        )

        self.last_time = None

        self.velocity_x = 0.0
        self.velocity_y = 0.0

        self.position_x = 0.0
        self.position_y = 0.0

        self.filtered_ax = 0.0
        self.filtered_ay = 0.0

        self.alpha = 0.8

        self.accel_deadzone = 0.08

        self.get_logger().info('IMU distance node started')

    def apply_deadzone(self, value):
        if abs(value) < self.accel_deadzone:
            return 0.0
        return value

    def imu_callback(self, msg):
        current_time = self.get_clock().now()

        if self.last_time is None:
            self.last_time = current_time
            return

        dt = (current_time - self.last_time).nanoseconds / 1e9
        self.last_time = current_time

        if dt <= 0.0:
            return

        raw_ax = msg.linear_acceleration.x
        raw_ay = msg.linear_acceleration.y

        self.filtered_ax = (
            self.alpha * self.filtered_ax
            + (1.0 - self.alpha) * raw_ax
        )

        self.filtered_ay = (
            self.alpha * self.filtered_ay
            + (1.0 - self.alpha) * raw_ay
        )

        ax = self.apply_deadzone(self.filtered_ax)
        ay = self.apply_deadzone(self.filtered_ay)

        self.velocity_x += ax * dt
        self.velocity_y += ay * dt

        self.position_x += self.velocity_x * dt
        self.position_y += self.velocity_y * dt

        distance = math.sqrt(
            self.position_x ** 2 +
            self.position_y ** 2
        )

        msg_out = Float32()
        msg_out.data = float(distance)
        self.distance_pub.publish(msg_out)

        self.get_logger().info(
            f'Distance: {distance:.3f} m | '
            f'vx: {self.velocity_x:.3f}, vy: {self.velocity_y:.3f}'
        )


def main(args=None):
    rclpy.init(args=args)
    node = ImuDistanceNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()