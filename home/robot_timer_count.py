#!/usr/bin/env python3

import csv
import os
import time

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray


class ElapsedTimer(Node):

    def __init__(self):
        super().__init__("elapsed_timer")

        self.subscription = self.create_subscription(
            Float32MultiArray,
            "/location_state",
            self.state_callback,
            10
        )

        # State names
        self.state_names = {
            1.0: "A",
            2.0: "B_beta",
            3.0: "B",
            4.0: "B_next",
            5.0: "C",
            6.0: "D",
            7.0: "D_next",
            8.0: "E"
        }

        self.current_state = None
        self.state_start_time = None

        self.timer_started = False

        self.run_start_time = None
        self.run_count = 29 
        # kita atur 8 karena sudah 8 kali setelah 30 juli
        # sekarang kita atur 29 karena sudah 29 kali

        self.state_times = {}

        self.csv_file = os.path.expanduser("~/state_times_rl_2.csv")

        # Create CSV header once
        if not os.path.exists(self.csv_file):
            with open(self.csv_file, "w", newline="") as f:
                writer = csv.writer(f)

                writer.writerow([
                    "Run",
                    "Total_Time",
                    "A",
                    "B_beta",
                    "B",
                    "B_next",
                    "C",
                    "D",
                    "D_next",
                    "E"
                ])

        self.get_logger().info("Elapsed Timer Ready")

    #######################################################

    def state_callback(self, msg):

        if len(msg.data) == 0:
            return

        state = msg.data[0]

        # ----------------------------
        # First state starts timer
        # ----------------------------

        if not self.timer_started and state == 1.0:

            self.timer_started = True

            self.run_start_time = time.perf_counter()

            self.state_start_time = self.run_start_time

            self.current_state = state

            self.state_times = {}

            self.get_logger().info(
                f"Run {self.run_count+1} Started"
            )

            return

        if not self.timer_started:
            return

        # ----------------------------
        # State changed
        # ----------------------------

        if state != self.current_state:

            now = time.perf_counter()

            elapsed = now - self.state_start_time

            state_name = self.state_names.get(
                self.current_state,
                str(self.current_state)
            )

            self.state_times[state_name] = elapsed

            self.get_logger().info(
                f"{state_name} : {elapsed:.3f} sec"
            )

            self.current_state = state
            self.state_start_time = now

        # ----------------------------
        # Finished
        # ----------------------------

        if state == 8.0:

            now = time.perf_counter()

            elapsed = now - self.state_start_time

            self.state_times["E"] = elapsed

            total = now - self.run_start_time

            self.run_count += 1

            self.get_logger().info(
                f"Run {self.run_count} Finished"
            )

            self.get_logger().info(
                f"Total Time : {total:.3f} sec"
            )

            self.save_csv(total)

            self.timer_started = False

            self.current_state = None

            self.state_start_time = None

            self.get_logger().info(
                "Waiting for next run..."
            )

    #######################################################

    def save_csv(self, total):

        with open(self.csv_file, "a", newline="") as f:

            writer = csv.writer(f)

            writer.writerow([
                self.run_count,
                round(total, 3),
                round(self.state_times.get("A", 0), 3),
                round(self.state_times.get("B_beta", 0), 3),
                round(self.state_times.get("B", 0), 3),
                round(self.state_times.get("B_next", 0), 3),
                round(self.state_times.get("C", 0), 3),
                round(self.state_times.get("D", 0), 3),
                round(self.state_times.get("D_next", 0), 3),
                round(self.state_times.get("E", 0), 3),
            ])

        self.get_logger().info(
            f"Saved to {self.csv_file}"
        )


###########################################################


def main(args=None):

    rclpy.init(args=args)

    node = ElapsedTimer()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()

    rclpy.shutdown()


if __name__ == "__main__":
    main()