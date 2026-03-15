'''!
  @file read_all_data.py
  @brief Through the example, you can get the sensor data by using getSensorData:
  @n     get all data of magnetometer, gyroscope, accelerometer.
  @n     With the rotation of the sensor, data changes are visible.
  @copyright	Copyright (c) 2010 DFRobot Co.Ltd (http://www.dfrobot.com)
  @license     The MIT License (MIT)
  @author [luoyufeng] (yufeng.luo@dfrobot.com)
  @maintainer [Fary](feng.yang@dfrobot.com)
  @version  V1.0
  @date  2021-10-20
  @url https://github.com/DFRobot/DFRobot_BMX160
'''
import sys
sys.path.append('../../')
import time
from DFRobot_BMX160 import BMX160

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
        #AccelErrorX = AccelErrorX + ((math.atan((AccelY)/math.sqrt(math.pow((AccelX),2) + math.pow((AccelZ),2))) * 180/math.pi))
        #AccelErrorY = AccelErrorY + ((math.atan(-1 * (AccelX)/math.sqrt(math.pow((AccelY),2) + math.pow((AccelZ),2)))*180/math.pi))
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


bmx = BMX160(1)

#begin return True if succeed, otherwise return False
while not bmx.begin():
    time.sleep(2)

def main():
    IMUX = 0
    IMUY = 0
    IMUZ = 0
    IMUAX = 0
    IMUAY = 0
    IMUAZ = 0
#    IMUX, IMUY, IMUZ, IMUAX, IMUAY, IMUAZ = calculate_IMU_error()
    while True:
        data= bmx.get_all_data()
#        time.sleep(1)
#        print("magn: x: {0:.2f} uT, y: {1:.2f} uT, z: {2:.2f} uT".format((data[0] - 98.7)*0.66888,(data[1]-(-74.1))*0.7727,(data[2]-18)*8.2459))
        print("gyro  x: {0:.2f} g, y: {1:.2f} g, z: {2:.2f} g".format(data[3]-IMUX,data[4]-IMUY,data[5]-IMUZ))
        print("accel x: {0:.2f} m/s^2, y: {1:.2f} m/s^2, z: {2:.2f} m/s^2".format(data[6]-IMUAX,data[7]-IMUAY, 9.8066501 + data[8]-IMUAZ))
        print(" ")
#        print("gyro  x: {0:.2f} g, y: {1:.2f} g, z: {2:.2f} g".format(data[3],data[4],data[5]))

#y nya kedepan +
# xnya ke kanan +
# znya dah bener
if __name__ == "__main__":
    main()
