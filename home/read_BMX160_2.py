#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

import time
import smbus


class BMX160:
    _BMX160_MAG_DATA_ADDR = 0x04
    _BMX160_MAGN_IF_0_ADDR = 0x4C
    _BMX160_MAGN_IF_1_ADDR = 0x4D
    _BMX160_MAGN_IF_2_ADDR = 0x4E
    _BMX160_MAGN_IF_3_ADDR = 0x4F
    _BMX160_MAGN_CONFIG_ADDR = 0x44
    _BMX160_COMMAND_REG_ADDR = 0x7E

    BMX160_SOFT_RESET_CMD = 0xB6

    _BMX160_ACCEL_MG_LSB_2G = 0.000061035
    _BMX160_GYRO_SENSITIVITY_2000DPS = 0.0609756
    BMX160_MAGN_UT_LSB = 0.3

    def __init__(self, bus=1):
        self.i2cbus = smbus.SMBus(bus)
        self.i2c_addr = 0x68

        self.accelRange = self._BMX160_ACCEL_MG_LSB_2G
        self.gyroRange = self._BMX160_GYRO_SENSITIVITY_2000DPS

        time.sleep(0.16)

    def begin(self):
        if not self.scan():
            return False

        self.soft_reset()

        # Enable accelerometer
        self.write_bmx_reg(self._BMX160_COMMAND_REG_ADDR, 0x11)
        time.sleep(0.05)

        # Enable gyroscope
        self.write_bmx_reg(self._BMX160_COMMAND_REG_ADDR, 0x15)
        time.sleep(0.1)

        # Enable magnetometer
        self.write_bmx_reg(self._BMX160_COMMAND_REG_ADDR, 0x19)
        time.sleep(0.01)

        self.set_magn_conf()

        return True

    def soft_reset(self):
        self.write_bmx_reg(
            self._BMX160_COMMAND_REG_ADDR,
            self.BMX160_SOFT_RESET_CMD
        )
        time.sleep(0.015)

    def set_magn_conf(self):
        self.write_bmx_reg(self._BMX160_MAGN_IF_0_ADDR, 0x80)
        time.sleep(0.05)

        self.write_bmx_reg(self._BMX160_MAGN_IF_3_ADDR, 0x01)
        self.write_bmx_reg(self._BMX160_MAGN_IF_2_ADDR, 0x4B)

        self.write_bmx_reg(self._BMX160_MAGN_IF_3_ADDR, 0x04)
        self.write_bmx_reg(self._BMX160_MAGN_IF_2_ADDR, 0x51)

        self.write_bmx_reg(self._BMX160_MAGN_IF_3_ADDR, 0x0E)
        self.write_bmx_reg(self._BMX160_MAGN_IF_2_ADDR, 0x52)

        self.write_bmx_reg(self._BMX160_MAGN_IF_3_ADDR, 0x02)
        self.write_bmx_reg(self._BMX160_MAGN_IF_2_ADDR, 0x4C)

        self.write_bmx_reg(self._BMX160_MAGN_IF_1_ADDR, 0x42)
        self.write_bmx_reg(self._BMX160_MAGN_CONFIG_ADDR, 0x08)
        self.write_bmx_reg(self._BMX160_MAGN_IF_0_ADDR, 0x03)

        time.sleep(0.05)

    def get_signed_16bit(self, msb, lsb):
        value = (msb << 8) | lsb

        if value & 0x8000:
            value -= 0x10000

        return value

    def get_all_data(self):
        data = self.read_bmx_reg(self._BMX160_MAG_DATA_ADDR)

        gyro_x_raw = self.get_signed_16bit(data[9], data[8])
        gyro_y_raw = self.get_signed_16bit(data[11], data[10])
        gyro_z_raw = self.get_signed_16bit(data[13], data[12])

        accel_x_raw = self.get_signed_16bit(data[15], data[14])
        accel_y_raw = self.get_signed_16bit(data[17], data[16])
        accel_z_raw = self.get_signed_16bit(data[19], data[18])

        gyro_x = gyro_x_raw * self.gyroRange
        gyro_y = gyro_y_raw * self.gyroRange
        gyro_z = gyro_z_raw * self.gyroRange

        accel_x = accel_x_raw * self.accelRange * 9.8
        accel_y = accel_y_raw * self.accelRange * 9.8
        accel_z = accel_z_raw * self.accelRange * 9.8

        return [
            0.0,
            0.0,
            0.0,
            gyro_x,
            gyro_y,
            gyro_z,
            accel_x,
            accel_y,
            accel_z
        ]

    def write_bmx_reg(self, register, value):
        self.i2cbus.write_byte_data(self.i2c_addr, register, value)

    def read_bmx_reg(self, register):
        return self.i2cbus.read_i2c_block_data(
            self.i2c_addr,
            register
        )

    def scan(self):
        try:
            self.i2cbus.read_byte(self.i2c_addr)
            return True
        except Exception:
            return False


class BMX160AccelCheckNode(Node):
    def __init__(self):
        super().__init__("bmx160_accel_check_node")

        self.imu = BMX160(bus=1)

        while not self.imu.begin():
            self.get_logger().error("BMX160 not detected. Retrying...")
            time.sleep(1.0)

        self.get_logger().info("BMX160 detected and initialized.")

        # -------------------------------------------------
        # Settings
        # -------------------------------------------------
        self.change_threshold = 0.08

        # How often to read IMU.
        # 0.02 = 50 Hz
        self.timer_period = 0.02

        # -------------------------------------------------
        # Baseline / idle acceleration
        # -------------------------------------------------
        self.idle_acc_x = 0.0
        self.idle_acc_y = 0.0
        self.idle_acc_z = 0.0

        self.baseline_ready = False
        self.baseline_samples = []
        self.baseline_sample_target = 100

        # -------------------------------------------------
        # Detection state
        # -------------------------------------------------
        self.is_counting_x = False
        self.start_time_x = None
        self.start_delta_x = 0.0
        self.start_direction_x = 0

        self.timer = self.create_timer(
            self.timer_period,
            self.read_accelerometer
        )

        self.get_logger().info(
            "Calibrating idle acceleration. Keep the IMU still..."
        )

    def read_accelerometer(self):
        data = self.imu.get_all_data()

        acc_x = data[6]
        acc_y = data[7]
        acc_z = data[8]

        # -------------------------------------------------
        # First: calculate idle acceleration baseline
        # -------------------------------------------------
        if not self.baseline_ready:
            self.baseline_samples.append((acc_x, acc_y, acc_z))

            if len(self.baseline_samples) >= self.baseline_sample_target:
                sum_x = 0.0
                sum_y = 0.0
                sum_z = 0.0

                for sample in self.baseline_samples:
                    sum_x += sample[0]
                    sum_y += sample[1]
                    sum_z += sample[2]

                self.idle_acc_x = sum_x / self.baseline_sample_target
                self.idle_acc_y = sum_y / self.baseline_sample_target
                self.idle_acc_z = sum_z / self.baseline_sample_target

                self.baseline_ready = True

                self.get_logger().info(
                    "Idle acceleration baseline ready:\n"
                    f"Idle Acc X: {self.idle_acc_x:.4f} m/s^2\n"
                    f"Idle Acc Y: {self.idle_acc_y:.4f} m/s^2\n"
                    f"Idle Acc Z: {self.idle_acc_z:.4f} m/s^2"
                )

            return

        # -------------------------------------------------
        # Calculate change from idle acceleration
        # -------------------------------------------------
        delta_x = acc_x - self.idle_acc_x
        delta_y = acc_y - self.idle_acc_y
        delta_z = acc_z - self.idle_acc_z

        self.get_logger().info(
            f"Accel X: {acc_x:.4f} m/s^2 | "
            f"Accel Y: {acc_y:.4f} m/s^2 | "
            f"Accel Z: {acc_z:.4f} m/s^2 | "
            f"Delta X: {delta_x:.4f}"
        )

        # -------------------------------------------------
        # X-axis movement detection
        # -------------------------------------------------
        self.check_x_movement(delta_x)

    def check_x_movement(self, delta_x):
        current_time = time.perf_counter()

        # -------------------------------------------------
        # Start counting when acceleration change exceeds threshold
        # -------------------------------------------------
        if not self.is_counting_x:
            if abs(delta_x) >= self.change_threshold:
                self.is_counting_x = True
                self.start_time_x = current_time
                self.start_delta_x = delta_x

                if delta_x > 0:
                    self.start_direction_x = 1
                else:
                    self.start_direction_x = -1

                self.get_logger().info(
                    "X acceleration change detected. Timer started.\n"
                    f"Start Delta X: {self.start_delta_x:.4f} m/s^2\n"
                    f"Direction: {self.start_direction_x}\n"
                    f"Start Time: {self.start_time_x:.4f}"
                )

            return

        # -------------------------------------------------
        # Stop counting when acceleration changes to opposite direction
        # Example:
        # idle = 0.15
        # positive change = 1.15
        # opposite change = -1.15
        # -------------------------------------------------
        opposite_direction_detected = (
            self.start_direction_x == 1
            and delta_x <= -self.change_threshold
        ) or (
            self.start_direction_x == -1
            and delta_x >= self.change_threshold
        )

        if opposite_direction_detected:
            end_time_x = current_time
            elapsed_time_x = end_time_x - self.start_time_x

            # Simple estimate based on your requested formula:
            # velocity = acceleration_change * time
            # displacement = velocity * time
            vel_x = self.start_delta_x * elapsed_time_x
            disp_x = vel_x * elapsed_time_x

            self.get_logger().info(
                "Opposite X acceleration detected. Timer stopped.\n"
                f"End Delta X: {delta_x:.4f} m/s^2\n"
                f"Elapsed Time: {elapsed_time_x:.4f} s\n"
                f"Estimated Vel X: {vel_x:.4f} m/s\n"
                f"Estimated Disp X: {disp_x:.4f} m"
            )

            # Reset state for next detection
            self.is_counting_x = False
            self.start_time_x = None
            self.start_delta_x = 0.0
            self.start_direction_x = 0


def main(args=None):
    rclpy.init(args=args)

    node = BMX160AccelCheckNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()