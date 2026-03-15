import sys
sys.path.append('../../')
import time
from DFRobot_BMX160 import BMX160
import math
def calculate_IMU_error():
    c = 0
    AccelErrorX = 0
    AccelErrorY = 0
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
        AccelErrorX = AccelErrorX + ((math.atan((AccelY)/math.sqrt(math.pow((AccelX),2) + math.pow((AccelZ),2))) * 180/math.pi))
        AccelErrorY = AccelErrorY + ((math.atan(-1 * (AccelX)/math.sqrt(math.pow((AccelY),2) + math.pow((AccelZ),2)))*180/math.pi))
        c = c+1
    AccelErrorX = AccelErrorX / 200
    AccelErrorY = AccelErrorY / 200
    c = 0
    while c < 200:
        data= bmx.get_all_data()
        GyroX = data[3]
        GyroY = data[4]
        GyroZ = data[5]
        GyroErrorX = GyroErrorX + GyroX
        GyroErrorY = GyroErrorY + GyroY
        GyroErrorZ = GyroErrorZ + GyroZ
        c = c+1
    GyroErrorX = GyroErrorX / 200
    GyroErrorY = GyroErrorY / 200
    GyroErrorZ = GyroErrorZ / 200
    c = 0
    print("GyroX Error: " + str(GyroErrorX))
    print("GyroY Error: " + str(GyroErrorY))
    print("GyroZ Error: " + str(GyroErrorZ))
    print("AccelX Error: " + str(AccelErrorX))
    print("AccelY Error: " + str(AccelErrorY))
    time.sleep(1)
    


bmx = BMX160(1)
currentTime = 0
#begin return True if succeed, otherwise return False
while not bmx.begin():
    time.sleep(2)

def main():
    # kalo mau cek, kommennya ilanging, sisanya di komen
    #calculate_IMU_error()
    AccelAngleX = 0
    AccelAngleY = 0
    gyroAngleX = 0
    gyroAngleY = 0
    currentTime = 0
    yaw = 0
    roll = 0
    pitch = 0
    previousTime = time.time()
    while True:
        currentTime = time.time()
        #print(str(currentTime))
        elapsedTime = currentTime - previousTime
        data= bmx.get_all_data()
        GyroX = data[3]
        GyroY = data[4]
        GyroZ = data[5]

        GyroX = GyroX - 0.004878080000000008 # cek imu error
        GyroY = GyroY - 0.12000839000000017 # cek imu error
        GyroZ = GyroZ + 0.0641772399999999 # cek imu error
        AccelX = data[6]
        AccelY = data[7]
        AccelZ = data[8]
        AccelAngleX = ((math.atan((AccelY)/math.sqrt(math.pow((AccelX),2) + math.pow((AccelZ),2))) * 180/math.pi)) + 5.434288716178433 #cek imu error
        AccelAngleY = ((math.atan(-1 * (AccelX)/math.sqrt(math.pow((AccelY),2) + math.pow((AccelZ),2)))*180/math.pi)) - 2.0191530623398735 # cek imu error
        
        gyroAngleX = gyroAngleX + GyroX * elapsedTime
        gyroAngleY = gyroAngleY + GyroY * elapsedTime
        yaw =  yaw + (GyroZ * elapsedTime *8.18182)

        roll = 0
        pitch = (0.96 * gyroAngleY + 0.04 * AccelAngleY) * 12.85714

        print("Pitch: " + str(pitch))
        print("Yaw: " + str(yaw))
        #print(" ")
        latency = time.time() - currentTime
        print("Latency: " + str(latency))
        time.sleep(1)
        print(" ")
        previousTime = currentTime
        
        

if __name__ == "__main__":
    main()
