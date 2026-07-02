#!/usr/bin/env python3

import rclpy
import RPi.GPIO as GPIO

from rclpy.node import Node
from std_msgs.msg import String
from std_msgs.msg import Int32MultiArray
from std_msgs.msg import Int32
from std_msgs.msg import Float32

import time
import math
import numpy as np

from ahrs.filters import Madgwick
from scipy.spatial.transform import Rotation as R

import sys
sys.path.append('../')

import smbus


class BMX160:
    _BMX160_CHIP_ID_ADDR             = (0x00)
    _BMX160_ERROR_REG_ADDR           = (0x02)
    _BMX160_MAG_DATA_ADDR            = (0x04)
    _BMX160_GYRO_DATA_ADDR           = (0x0C)
    _BMX160_ACCEL_DATA_ADDR          = (0x12)
    _BMX160_STATUS_ADDR              = (0x1B)
    _BMX160_INT_STATUS_ADDR          = (0x1C)
    _BMX160_FIFO_LENGTH_ADDR         = (0x22)
    _BMX160_FIFO_DATA_ADDR           = (0x24)
    _BMX160_ACCEL_CONFIG_ADDR        = (0x40)
    _BMX160_ACCEL_RANGE_ADDR         = (0x41)
    _BMX160_GYRO_CONFIG_ADDR         = (0x42)
    _BMX160_GYRO_RANGE_ADDR          = (0x43)
    _BMX160_MAGN_CONFIG_ADDR         = (0x44)
    _BMX160_FIFO_DOWN_ADDR           = (0x45)
    _BMX160_FIFO_CONFIG_0_ADDR       = (0x46)
    _BMX160_FIFO_CONFIG_1_ADDR       = (0x47)
    _BMX160_MAGN_RANGE_ADDR          = (0x4B)
    _BMX160_MAGN_IF_0_ADDR           = (0x4C)
    _BMX160_MAGN_IF_1_ADDR           = (0x4D)
    _BMX160_MAGN_IF_2_ADDR           = (0x4E)
    _BMX160_MAGN_IF_3_ADDR           = (0x4F)
    _BMX160_INT_ENABLE_0_ADDR        = (0x50)
    _BMX160_INT_ENABLE_1_ADDR        = (0x51)
    _BMX160_INT_ENABLE_2_ADDR        = (0x52)
    _BMX160_INT_OUT_CTRL_ADDR        = (0x53)
    _BMX160_INT_LATCH_ADDR           = (0x54)
    _BMX160_INT_MAP_0_ADDR           = (0x55)
    _BMX160_INT_MAP_1_ADDR           = (0x56)
    _BMX160_INT_MAP_2_ADDR           = (0x57)
    _BMX160_INT_DATA_0_ADDR          = (0x58)
    _BMX160_INT_DATA_1_ADDR          = (0x59)
    _BMX160_INT_LOWHIGH_0_ADDR       = (0x5A)
    _BMX160_INT_LOWHIGH_1_ADDR       = (0x5B)
    _BMX160_INT_LOWHIGH_2_ADDR       = (0x5C)
    _BMX160_INT_LOWHIGH_3_ADDR       = (0x5D)
    _BMX160_INT_LOWHIGH_4_ADDR       = (0x5E)
    _BMX160_INT_MOTION_0_ADDR        = (0x5F)
    _BMX160_INT_MOTION_1_ADDR        = (0x60)
    _BMX160_INT_MOTION_2_ADDR        = (0x61)
    _BMX160_INT_MOTION_3_ADDR        = (0x62)
    _BMX160_INT_TAP_0_ADDR           = (0x63)
    _BMX160_INT_TAP_1_ADDR           = (0x64)
    _BMX160_INT_ORIENT_0_ADDR        = (0x65)
    _BMX160_INT_ORIENT_1_ADDR        = (0x66)
    _BMX160_INT_FLAT_0_ADDR          = (0x67)
    _BMX160_INT_FLAT_1_ADDR          = (0x68)
    _BMX160_FOC_CONF_ADDR            = (0x69)
    _BMX160_CONF_ADDR                = (0x6A)
    _BMX160_IF_CONF_ADDR             = (0x6B)
    _BMX160_SELF_TEST_ADDR           = (0x6D)
    _BMX160_OFFSET_ADDR              = (0x71)
    _BMX160_OFFSET_CONF_ADDR         = (0x77)
    _BMX160_INT_STEP_CNT_0_ADDR      = (0x78)
    _BMX160_INT_STEP_CONFIG_0_ADDR   = (0x7A)
    _BMX160_INT_STEP_CONFIG_1_ADDR   = (0x7B)
    _BMX160_COMMAND_REG_ADDR         = (0x7E)

    BMX160_SOFT_RESET_CMD            = (0xb6)
    BMX160_MAGN_UT_LSB               = (0.3)

    _BMX160_ACCEL_MG_LSB_2G          = (0.000061035)
    _BMX160_ACCEL_MG_LSB_4G          = (0.000122070)
    _BMX160_ACCEL_MG_LSB_8G          = (0.000244141)
    _BMX160_ACCEL_MG_LSB_16G         = (0.000488281)

    _BMX160_GYRO_SENSITIVITY_125DPS  = (0.0038110)
    _BMX160_GYRO_SENSITIVITY_250DPS  = (0.0076220)
    _BMX160_GYRO_SENSITIVITY_500DPS  = (0.0152439)
    _BMX160_GYRO_SENSITIVITY_1000DPS = (0.0304878)
    _BMX160_GYRO_SENSITIVITY_2000DPS = (0.0609756)

    GyroRange_125DPS                 = (0x00)
    GyroRange_250DPS                 = (0x01)
    GyroRange_500DPS                 = (0x02)
    GyroRange_1000DPS                = (0x03)
    GyroRange_2000DPS                = (0x04)

    AccelRange_2G                    = (0x00)
    AccelRange_4G                    = (0x01)
    AccelRange_8G                    = (0x02)
    AccelRange_16G                   = (0x03)

    accelRange = _BMX160_ACCEL_MG_LSB_2G
    gyroRange = _BMX160_GYRO_SENSITIVITY_2000DPS

    def __init__(self, bus):
        self.i2cbus = smbus.SMBus(bus)
        self.i2c_addr = 0x68
        time.sleep(0.16)

    def begin(self):
        if not self.scan():
            return False
        else:
            self.soft_reset()

            self.write_bmx_reg(self._BMX160_COMMAND_REG_ADDR, 0x11)
            time.sleep(0.05)

            self.write_bmx_reg(self._BMX160_COMMAND_REG_ADDR, 0x15)
            time.sleep(0.1)

            self.write_bmx_reg(self._BMX160_COMMAND_REG_ADDR, 0x19)
            time.sleep(0.01)

            self.set_magn_conf()
            return True

    def set_low_power(self):
        self.soft_reset()
        time.sleep(0.1)

        self.set_magn_conf()
        time.sleep(0.1)

        self.write_bmx_reg(self._BMX160_COMMAND_REG_ADDR, 0x12)
        time.sleep(0.1)

        self.write_bmx_reg(self._BMX160_COMMAND_REG_ADDR, 0x17)
        time.sleep(0.1)

        self.write_bmx_reg(self._BMX160_COMMAND_REG_ADDR, 0x1B)
        time.sleep(0.1)

    def wake_up(self):
        self.soft_reset()
        time.sleep(0.1)

        self.set_magn_conf()
        time.sleep(0.1)

        self.write_bmx_reg(self._BMX160_COMMAND_REG_ADDR, 0x11)
        time.sleep(0.1)

        self.write_bmx_reg(self._BMX160_COMMAND_REG_ADDR, 0x15)
        time.sleep(0.1)

        self.write_bmx_reg(self._BMX160_COMMAND_REG_ADDR, 0x19)
        time.sleep(0.1)

    def soft_reset(self):
        data = self.BMX160_SOFT_RESET_CMD
        self.write_bmx_reg(self._BMX160_COMMAND_REG_ADDR, data)
        time.sleep(0.015)
        return True

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

    def set_gyro_range(self, bits):
        if bits == 0:
            self.gyroRange = self._BMX160_GYRO_SENSITIVITY_125DPS
        elif bits == 1:
            self.gyroRange = self._BMX160_GYRO_SENSITIVITY_250DPS
        elif bits == 2:
            self.gyroRange = self._BMX160_GYRO_SENSITIVITY_500DPS
        elif bits == 3:
            self.gyroRange = self._BMX160_GYRO_SENSITIVITY_1000DPS
        elif bits == 4:
            self.gyroRange = self._BMX160_GYRO_SENSITIVITY_2000DPS
        else:
            self.gyroRange = self._BMX160_GYRO_SENSITIVITY_250DPS

    def set_accel_range(self, bits):
        if bits == 0:
            self.accelRange = self._BMX160_ACCEL_MG_LSB_2G
        elif bits == 1:
            self.accelRange = self._BMX160_ACCEL_MG_LSB_4G
        elif bits == 2:
            self.accelRange = self._BMX160_ACCEL_MG_LSB_8G
        elif bits == 3:
            self.accelRange = self._BMX160_ACCEL_MG_LSB_16G
        else:
            self.accelRange = self._BMX160_ACCEL_MG_LSB_2G

    def get_all_data(self):
        data = self.read_bmx_reg(self._BMX160_MAG_DATA_ADDR)

        if data[1] & 0x80:
            magnx = -0x10000 + ((data[1] << 8) | data[0])
        else:
            magnx = (data[1] << 8) | data[0]

        if data[3] & 0x80:
            magny = -0x10000 + ((data[3] << 8) | data[2])
        else:
            magny = (data[3] << 8) | data[2]

        if data[5] & 0x80:
            magnz = -0x10000 + ((data[5] << 8) | data[4])
        else:
            magnz = (data[5] << 8) | data[4]

        if data[9] & 0x80:
            gyrox = -0x10000 + ((data[9] << 8) | data[8])
        else:
            gyrox = (data[9] << 8) | data[8]

        if data[11] & 0x80:
            gyroy = -0x10000 + ((data[11] << 8) | data[10])
        else:
            gyroy = (data[11] << 8) | data[10]

        if data[13] & 0x80:
            gyroz = -0x10000 + ((data[13] << 8) | data[12])
        else:
            gyroz = (data[13] << 8) | data[12]

        if data[15] & 0x80:
            accelx = -0x10000 + ((data[15] << 8) | data[14])
        else:
            accelx = (data[15] << 8) | data[14]

        if data[17] & 0x80:
            accely = -0x10000 + ((data[17] << 8) | data[16])
        else:
            accely = (data[17] << 8) | data[16]

        if data[19] & 0x80:
            accelz = -0x10000 + ((data[19] << 8) | data[18])
        else:
            accelz = (data[19] << 8) | data[18]

        magnx *= self.BMX160_MAGN_UT_LSB
        magny *= self.BMX160_MAGN_UT_LSB
        magnz *= self.BMX160_MAGN_UT_LSB

        gyrox *= self.gyroRange
        gyroy *= self.gyroRange
        gyroz *= self.gyroRange

        # Converted to m/s^2
        accelx *= self.accelRange * 9.8
        accely *= self.accelRange * 9.8
        accelz *= self.accelRange * 9.8

        output = []

        output.append(magnx)
        output.append(magny)
        output.append(magnz)

        output.append(gyrox)
        output.append(gyroy)
        output.append(gyroz)

        output.append(accelx)
        output.append(accely)
        output.append(accelz)

        return output

    def write_bmx_reg(self, register, value):
        self.i2cbus.write_byte_data(self.i2c_addr, register, value)

    def read_bmx_reg(self, register):
        return self.i2cbus.read_i2c_block_data(self.i2c_addr, register)

    def scan(self):
        try:
            self.i2cbus.read_byte(self.i2c_addr)
            return True
        except:
            print("I2C init fail")
            return False


bmx = BMX160(1)

while not bmx.begin():
    pass


def calculate_IMU_error():
    c = 0

    AccelErrorX = 0.0
    AccelErrorY = 0.0
    AccelErrorZ = 0.0

    GyroErrorX = 0.0
    GyroErrorY = 0.0
    GyroErrorZ = 0.0

    while c < 200:
        data = bmx.get_all_data()

        GyroX = data[3]
        GyroY = data[4]
        GyroZ = data[5]

        AccelX = data[6]
        AccelY = data[7]
        AccelZ = data[8]

        AccelErrorX += AccelX
        AccelErrorY += AccelY
        AccelErrorZ += AccelZ

        GyroErrorX += GyroX
        GyroErrorY += GyroY
        GyroErrorZ += GyroZ

        c += 1

    AccelErrorX /= 200
    AccelErrorY /= 200
    AccelErrorZ /= 200

    GyroErrorX /= 200
    GyroErrorY /= 200
    GyroErrorZ /= 200

    return (
        GyroErrorX,
        GyroErrorY,
        GyroErrorZ,
        AccelErrorX,
        AccelErrorY,
        AccelErrorZ
    )


def unwrap_yaw(prev_yaw, current_yaw):
    delta = current_yaw - prev_yaw

    if delta > 180:
        delta -= 360
    elif delta < -180:
        delta += 360

    return prev_yaw + delta


class MyNode(Node):
    def __init__(self):
        super().__init__("gyro_node")

        self.publish_maju = self.create_publisher(
            Int32MultiArray,
            "/gait_",
            1
        )

        self.distance_pub = self.create_publisher(
            Float32,
            "/imu_distance",
            10
        )

        self.subscriber_trigger = self.create_subscription(
            Int32MultiArray,
            "/state_",
            self.getting_data,
            1
        )

        self.subscriber_calibrate = self.create_subscription(
            Int32,
            "/calibrate_",
            self.calibrate_callback,
            1
        )

        self.subscriber_turn_on_roll = self.create_subscription(
            Int32,
            "/turn_on_roll_",
            self.turn_on_roll_callback,
            1
        )

        self.subscriber_turn_on_pitch = self.create_subscription(
            Int32,
            "/turn_on_pitch_",
            self.turn_on_pitch_callback,
            1
        )

        self.subscriber_correction = self.create_subscription(
            Int32,
            "/correction_",
            self.correction_heading,
            1
        )

        # I changed this from 0.0001 to 0.01.
        # 0.0001 means 10,000 Hz, which is too fast for I2C IMU reading.
        # 0.01 means 100 Hz.
        self.timer_ = self.create_timer(0.01, self.ngitung_gyro)

        self.measurement = 0

        self.yaw = 0.0
        self.roll = 0.0
        self.pitch = 0.0

        self.send_yaw = 0.0
        self.send_roll = 0.0
        self.send_pitch = 0.0

        self.calibrate_value = 0
        self.correction = 0

        self.turn_on_roll_value = 0
        self.turn_on_pitch_value = 0

        self.current_time = time.perf_counter()
        self.previous_time = time.perf_counter()

        self.gyroAngleX = 0.0
        self.gyroAngleY = 0.0

        self.q = np.array([1.0, 0.0, 0.0, 0.0])
        self.madgwick = Madgwick()

        self.raw_yaw = 0.0
        self.prev_yaw = 0.0

        self.IMUX = 0.0
        self.IMUY = 0.0
        self.IMUZ = 0.0

        self.IMUAX = 0.0
        self.IMUAY = 0.0
        self.IMUAZ = 0.0

        self.get_logger().info("Calibrating IMU. Keep robot still...")

        (
            self.IMUX,
            self.IMUY,
            self.IMUZ,
            self.IMUAX,
            self.IMUAY,
            self.IMUAZ
        ) = calculate_IMU_error()

        self.get_logger().info("IMU calibration finished.")

        # Distance estimation variables
        self.velocity_x = 0.0
        self.velocity_y = 0.0

        self.position_x = 0.0
        self.position_y = 0.0

        self.distance = 0.0

        self.filtered_accel_x = 0.0
        self.filtered_accel_y = 0.0

        # Low-pass filter value.
        # Higher value = smoother but slower response.
        self.accel_alpha = 0.85

        # Ignore small acceleration noise.
        # Tune this between 0.05 and 0.25 depending on your sensor noise.
        self.accel_deadzone = 0.08

        # Optional velocity damping to reduce drift.
        # Closer to 1.0 = less damping.
        self.velocity_damping = 0.98

        self.get_logger().info("gyro_node with IMU distance estimation started.")

    def apply_deadzone(self, value):
        if abs(value) < self.accel_deadzone:
            return 0.0
        return value

    def turn_on_roll_callback(self, message: Int32):
        self.turn_on_roll_value = 1

    def turn_on_pitch_callback(self, message: Int32):
        self.turn_on_pitch_value = 1

    def calibrate_callback(self, message: Int32):
        self.calibrate_value += message.data

    def correction_heading(self, message: Int32):
        self.correction = message.data

    def getting_data(self, message: Int32MultiArray):
        info = Int32MultiArray()

        self.send_yaw = (
            self.yaw
            + (90 * self.calibrate_value)
            + self.correction
        )

        info.data = [
            int(self.send_yaw),
            int(self.send_roll),
            int(message.data[0]),
            int(message.data[1]),
            int(self.send_pitch)
        ]

        self.publish_maju.publish(info)

    def ngitung_gyro(self):
        data = bmx.get_all_data()

        # -------------------------------------------------
        # Raw sensor mapping from BMX160 get_all_data()
        # -------------------------------------------------
        # data[0] = magnetometer x
        # data[1] = magnetometer y
        # data[2] = magnetometer z
        # data[3] = gyro x
        # data[4] = gyro y
        # data[5] = gyro z
        # data[6] = accel x
        # data[7] = accel y
        # data[8] = accel z
        # -------------------------------------------------

        GyroX = data[3] - self.IMUX
        GyroY = data[4] - self.IMUY
        GyroZ = data[5] - self.IMUZ

        raw_accel_x = data[6]
        raw_accel_y = data[7]
        raw_accel_z = data[8]

        # Calibrated body-frame acceleration.
        # These values are used for distance estimation.
        body_accel_x = raw_accel_x - self.IMUAX
        body_accel_y = raw_accel_y - self.IMUAY
        body_accel_z = raw_accel_z - self.IMUAZ

        # Madgwick needs gravity direction.
        # Your old code used:
        # AccelZ = 9.80665 + data[8] - self.IMUAZ
        # Here we only add gravity for orientation calculation.
        acc_for_orientation = np.array([
            body_accel_x,
            body_accel_y,
            body_accel_z + 9.80665
        ])

        gyr = np.radians(np.array([
            GyroX,
            GyroY,
            GyroZ
        ]))

        self.current_time = time.perf_counter()
        dt = self.current_time - self.previous_time

        if dt <= 0.0:
            return

        self.q = self.madgwick.updateIMU(
            q=self.q,
            acc=acc_for_orientation,
            gyr=gyr,
            dt=dt
        )

        self.previous_time = self.current_time

        # -------------------------------------------------
        # Orientation calculation
        # -------------------------------------------------
        rotation = None

        if self.q is not None:
            rotation = R.from_quat([
                self.q[1],
                self.q[2],
                self.q[3],
                self.q[0]
            ])

            self.roll, self.pitch, self.raw_yaw = rotation.as_euler(
                'xyz',
                degrees=True
            )

            self.yaw = unwrap_yaw(self.prev_yaw, self.raw_yaw)
            self.prev_yaw = self.yaw

        if self.turn_on_roll_value == 1:
            self.send_roll = self.roll

        if self.turn_on_pitch_value == 1:
            self.send_pitch = self.pitch

        # -------------------------------------------------
        # Distance estimation
        # -------------------------------------------------
        # Use calibrated acceleration without added gravity.
        body_accel = np.array([
            body_accel_x,
            body_accel_y,
            body_accel_z
        ])

        if rotation is not None:
            # Convert robot/body-frame acceleration to world-frame acceleration.
            world_accel = rotation.apply(body_accel)

            world_accel_x = world_accel[0]
            world_accel_y = world_accel[1]
        else:
            # Fallback if orientation is not ready.
            world_accel_x = body_accel_x
            world_accel_y = body_accel_y

        # Low-pass filter
        self.filtered_accel_x = (
            self.accel_alpha * self.filtered_accel_x
            + (1.0 - self.accel_alpha) * world_accel_x
        )

        self.filtered_accel_y = (
            self.accel_alpha * self.filtered_accel_y
            + (1.0 - self.accel_alpha) * world_accel_y
        )

        accel_x = self.apply_deadzone(self.filtered_accel_x)
        accel_y = self.apply_deadzone(self.filtered_accel_y)

        # Integrate acceleration to velocity
        self.velocity_x += accel_x * dt
        self.velocity_y += accel_y * dt

        # Damping helps reduce infinite velocity drift
        self.velocity_x *= self.velocity_damping
        self.velocity_y *= self.velocity_damping

        # Integrate velocity to position
        self.position_x += self.velocity_x * dt
        self.position_y += self.velocity_y * dt

        # Total displacement from start position
        self.distance = math.sqrt(
            self.position_x ** 2
            + self.position_y ** 2
        )

        distance_msg = Float32()
        distance_msg.data = float(self.distance)
        self.distance_pub.publish(distance_msg)


def main(args=None):
    rclpy.init(args=args)

    node = MyNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()