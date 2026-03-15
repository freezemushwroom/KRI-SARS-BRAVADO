import sys
sys.path.append('../../')
import time
from DFRobot_BMX160 import BMX160
import math
import numpy as np
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
        AccelErrorX = AccelErrorX + math.degrees((math.atan((AccelY)/math.sqrt(math.pow((AccelX),2) + math.pow((AccelZ),2)))))
        AccelErrorY = AccelErrorY + math.degrees((math.atan(-1 * (AccelX)/math.sqrt(math.pow((AccelY),2) + math.pow((AccelZ),2)))))
#        AccelErrorX = AccelErrorX + AccelX
#        AccelErrorY = AccelErrorY + AccelY
#        AccelErrorZ = AccelErrorZ + AccelZ
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
    print("GyroX Error: " + str(GyroErrorX))
    print("GyroY Error: " + str(GyroErrorY))
    print("GyroZ Error: " + str(GyroErrorZ))
    print("AccelX Error: " + str(AccelErrorX))
    print("AccelY Error: " + str(AccelErrorY))
    print("AccelZ Error: " + str(AccelErrorZ))
    return(GyroErrorX, GyroErrorY, GyroErrorZ, AccelErrorX, AccelErrorY, AccelErrorZ)
    time.sleep(5)


bmx = BMX160(1)
currentTime = 0.0
#begin return True if succeed, otherwise return False
while not bmx.begin():
    time.sleep(2)

def main():
    IMUX, IMUY, IMUZ, IMUAX, IMUAY, IMUAZ = calculate_IMU_error()
    AccelAngleX = 0
    AccelAngleY = 0
    gyroAngleX = 0
    gyroAngleY = 0
    currentTime = 0.0
    rolll = 0
    yaw = 0
    yaw_gyro = 0
    roll = 0
    pitch = 0

    previousTime = time.perf_counter()
    while True:
        data= bmx.get_all_data()
        GyroX = data[3]
        GyroY = data[4]
        GyroZ = data[5]

        GyroX = GyroX - IMUX # cek imu error
        GyroY = GyroY - IMUY # cek imu error
        GyroZ = GyroZ - (IMUZ) # cek imu error
        AccelX = data[6] #- IMUAX
        AccelY = data[7] #- IMUAY
        AccelZ = data[8] #9.80665- data[8] - IMUAZ
        AccelAngleX = math.degrees((math.atan((AccelY)/math.sqrt(math.pow((AccelX),2) + math.pow((AccelZ),2))))) - IMUAX
        AccelAngleY = math.degrees((math.atan(-1 * (AccelX)/math.sqrt(math.pow((AccelY),2) + math.pow((AccelZ),2))))) - IMUAY

        currentTime = time.perf_counter()
        elapsedTime = (currentTime - previousTime)

        gyroAngleX += (GyroX) * elapsedTime
        gyroAngleY += (GyroY) * elapsedTime
        yaw_gyro += ((GyroZ * elapsedTime))
        previousTime = currentTime

        roll = ((0.98 * gyroAngleX + 0.02 * AccelAngleX))
        pitch = ((0.98 * gyroAngleY + 0.02 * AccelAngleY))

        print("Yaw: " + str(yaw_gyro))
        print("Pitch: " + str(pitch))
        print("Roll: " + str(roll))
        print(" ")

if __name__ == "__main__":
    main()
