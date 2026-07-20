#!/usr/bin/env python3

import threading

import rclpy
from rclpy.node import Node

from std_msgs.msg import Float32MultiArray
from std_msgs.msg import Bool


# ===========================================================
# Import your gait functions here
# ===========================================================

# from robot_gait import (
#     maju,
#     putar_kiri,
#     putar_kanan,
#     jalan_kiri_miring,
#     jalan_kanan_miring,
#     tetrapod_maju,
# )

# Temporary dummy functions
def maju():
    print("Forward")

def putar_kiri():
    print("Turn Left")

def putar_kanan():
    print("Turn Right")

def jalan_kiri_miring():
    print("Strafe Left")

def jalan_kanan_miring():
    print("Strafe Right")

def tetrapod_maju():
    print("Tetrapod Forward")


class MovementExecutor(Node):

    def __init__(self):

        super().__init__("movement_executor")

        self.busy = False
        self.tetrapod_mode = False

        self.create_subscription(
            Float32MultiArray,
            "/cmd_movement",
            self.cmd_callback,
            10
        )

        self.create_subscription(
            Bool,
            "/move_tetrapod",
            self.tetrapod_callback,
            10
        )

        self.pub_state = self.create_publisher(
            Bool,
            "/movement_state",
            10
        )

        self.get_logger().info("Movement Executor Started")

    def tetrapod_callback(self, msg):
        self.tetrapod_mode = msg.data

    def publish_state(self, moving):

        msg = Bool()
        msg.data = moving
        self.pub_state.publish(msg)

    def cmd_callback(self, msg):

        if self.busy:
            self.get_logger().warn("Robot still moving, ignoring command.")
            return

        if len(msg.data) < 3:
            return

        forward = msg.data[0]
        strafe = msg.data[1]
        rotate = msg.data[2]

        threading.Thread(
            target=self.execute_command,
            args=(forward, strafe, rotate),
            daemon=True
        ).start()

    def execute_command(self, forward, strafe, rotate):

        self.busy = True
        self.publish_state(True)

        try:

            # =============================
            # Forward
            # =============================

            if forward > 0:

                if self.tetrapod_mode:
                    self.get_logger().info("Tetrapod Forward")
                    tetrapod_maju()

                else:
                    self.get_logger().info("Forward")
                    maju()

            # =============================
            # Turn Left
            # =============================

            elif rotate > 0:

                self.get_logger().info("Turn Left")
                putar_kiri()

            # =============================
            # Turn Right
            # =============================

            elif rotate < 0:

                self.get_logger().info("Turn Right")
                putar_kanan()

            # =============================
            # Strafe Left
            # =============================

            elif strafe < 0:

                self.get_logger().info("Strafe Left")
                jalan_kiri_miring()

            # =============================
            # Strafe Right
            # =============================

            elif strafe > 0:

                self.get_logger().info("Strafe Right")
                jalan_kanan_miring()

            else:

                self.get_logger().info("No movement command.")

        finally:

            self.publish_state(False)
            self.busy = False


def main(args=None):

    rclpy.init(args=args)

    node = MovementExecutor()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()