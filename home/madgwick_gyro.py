import sys
sys.path.append('../../')
import time
from DFRobot_BMX160 import BMX160
import numpy as np
from ahrs.filters import Madgwick
from scipy.spatial.transform import Rotation as R
import math
def calculate_IMU_error():
    c = 0
    AccelErrorX = 0
    AccelErrorY = 0
    AccelErrorZ = 0
    GyroErrorX = 0
    GyroErrorY = 0
    GyroErrorZ = 0
    while c < 200:
        data= bmx.get_all_data()
        GyroX = data[3]
        GyroY = data[4]
        GyroZ = data[5]
        AccelX = data[6]
        AccelY = data[7]
        AccelZ = data[8]
        AccelErrorX = AccelErrorX + AccelX
        AccelErrorY = AccelErrorY + AccelY
        AccelErrorZ = AccelErrorZ + AccelZ
        GyroErrorX = GyroErrorX + GyroX
        GyroErrorY = GyroErrorY + GyroY
        GyroErrorZ = GyroErrorZ + GyroZ
        c = c+1
    AccelErrorX = AccelErrorX / 200
    AccelErrorY = AccelErrorY / 200
    AccelErrorZ = AccelErrorZ / 200
    GyroErrorX = GyroErrorX / 200
    GyroErrorY = GyroErrorY / 200
    GyroErrorZ = GyroErrorZ / 200
    return(GyroErrorX, GyroErrorY, GyroErrorZ, AccelErrorX, AccelErrorY, AccelErrorZ)


def unwrap_yaw(prev_yaw, current_yaw):
    delta = current_yaw - prev_yaw

    # Correct the discontinuity at the ±180° boundary
    if delta > 180:
        delta -= 360
    elif delta < -180:
        delta += 360

    return prev_yaw + delta

bmx = BMX160(1)

#begin return True if succeed, otherwise return False
while not bmx.begin():
    time.sleep(2)


q = np.array([1.0, 0.0, 0.0, 0.0]) #Initial Quaternion

hard_iron = np.array([-58.37, 0.6, 23.16])
soft_iron = np.array([[0.988, -0.102, 0.549], [-0.102, 0.437, -0.070], [0.549, -0.070, 2.681]])

madgwick = Madgwick(frequency = 129)

IMUX, IMUY, IMUZ, IMUAX, IMUAY, IMUAZ = calculate_IMU_error()

prev_yaw = 0
previous_time = time.time()
while True:
    data = bmx.get_all_data()
#    acc = np.array([-(data[7] - IMUAY), -(data[6] - IMUAX), 9.8066501+ data[8] - IMUAZ])
#    gyr = np.radians(np.array([-(data[4] - IMUY), -(data[3] - IMUX), data[5] - IMUZ]))
    acc = np.array([data[6] - IMUAX, data[7] - IMUAY, 9.8066501 + data[8] - IMUAZ])
    gyr = np.radians(np.array([data[3] - IMUX, data[4] - IMUY, data[5] - IMUZ]))
    mag_raw = np.array([data[0]-hard_iron[0], data[1]-hard_iron[1], data[2]-hard_iron[2]])
    mag_raw = mag_raw @ soft_iron
    mag = [mag_raw[0], mag_raw[1], mag_raw[2]]
    current_time = time.time()
#    q = madgwick.updateMARG(q=q, acc=acc, gyr = gyr, mag = mag)
    q = madgwick.updateIMU(q=q, acc=acc, gyr=gyr, dt = current_time - previous_time)
    previous_time = current_time

    if q is not None:
        r = R.from_quat([q[1], q[2], q[3], q[0]])
        roll, pitch, yaw = r.as_euler('xyz', degrees = True)
        unwarped_yaw = unwrap_yaw (prev_yaw, yaw)
        prev_yaw = unwarped_yaw


        print("Roll: " + str(int(roll)) + " Pitch: " + str(int(pitch)) + " Yaw: " + str(int((unwarped_yaw))))
