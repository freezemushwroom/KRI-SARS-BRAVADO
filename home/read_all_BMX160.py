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

    BMX160_MAGN_UT_LSB = 0.3

    _BMX160_ACCEL_MG_LSB_2G = 0.000061035
    _BMX160_GYRO_SENSITIVITY_2000DPS = 0.0609756

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

        mag_x_raw = self.get_signed_16bit(data[1], data[0])
        mag_y_raw = self.get_signed_16bit(data[3], data[2])
        mag_z_raw = self.get_signed_16bit(data[5], data[4])

        gyro_x_raw = self.get_signed_16bit(data[9], data[8])
        gyro_y_raw = self.get_signed_16bit(data[11], data[10])
        gyro_z_raw = self.get_signed_16bit(data[13], data[12])

        accel_x_raw = self.get_signed_16bit(data[15], data[14])
        accel_y_raw = self.get_signed_16bit(data[17], data[16])
        accel_z_raw = self.get_signed_16bit(data[19], data[18])

        mag_x = mag_x_raw * self.BMX160_MAGN_UT_LSB
        mag_y = mag_y_raw * self.BMX160_MAGN_UT_LSB
        mag_z = mag_z_raw * self.BMX160_MAGN_UT_LSB

        gyro_x = gyro_x_raw * self.gyroRange
        gyro_y = gyro_y_raw * self.gyroRange
        gyro_z = gyro_z_raw * self.gyroRange

        accel_x = accel_x_raw * self.accelRange * 9.8
        accel_y = accel_y_raw * self.accelRange * 9.8
        accel_z = accel_z_raw * self.accelRange * 9.8

        return [
            mag_x,
            mag_y,
            mag_z,
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


class BMX160PrintNode(Node):
    def __init__(self):
        super().__init__("bmx160_print_node")

        self.imu = BMX160(bus=1)

        while not self.imu.begin():
            self.get_logger().error("BMX160 not detected. Retrying...")
            time.sleep(1.0)

        self.get_logger().info("BMX160 detected and initialized.")

        # Print data every 0.5 seconds
        self.timer = self.create_timer(0.5, self.print_imu_data)

    def print_imu_data(self):
        data = self.imu.get_all_data()

        mag_x = data[0]
        mag_y = data[1]
        mag_z = data[2]

        gyro_x = data[3]
        gyro_y = data[4]
        gyro_z = data[5]

        accel_x = data[6]
        accel_y = data[7]
        accel_z = data[8]

        self.get_logger().info(
            "\n"
            "===== BMX160 IMU DATA =====\n"
            f"Magnetometer X : {mag_x:.3f} uT\n"
            f"Magnetometer Y : {mag_y:.3f} uT\n"
            f"Magnetometer Z : {mag_z:.3f} uT\n"
            "\n"
            f"Gyroscope X    : {gyro_x:.3f} deg/s\n"
            f"Gyroscope Y    : {gyro_y:.3f} deg/s\n"
            f"Gyroscope Z    : {gyro_z:.3f} deg/s\n"
            "\n"
            f"Accelerometer X: {accel_x:.3f} m/s^2\n"
            f"Accelerometer Y: {accel_y:.3f} m/s^2\n"
            f"Accelerometer Z: {accel_z:.3f} m/s^2\n"
            "==========================="
        )


def main(args=None):
    rclpy.init(args=args)

    node = BMX160PrintNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()