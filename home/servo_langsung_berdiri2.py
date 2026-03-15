from time import sleep
from adafruit_servokit import ServoKit
import math

kit1 = ServoKit(channels = 16, address = 0x41) #, reference_clock_speed = 24930632)
kit2 = ServoKit(channels = 16, address = 0x40) #, reference_clock_speed = 25220628)

for i in range (10):
    kit1.servo[i].set_pulse_width_range(320, 2320)
    kit2.servo[15-i].set_pulse_width_range(400, 2400)

coxa = 2.55
femur = 6.508
tibia = 7.964

def lebar(l):
    maju = 0
    alpha1 = math.asin(l/femur)
    h = math.sqrt(math.pow(femur,2)+math.pow(tibia,2)-(2*femur*tibia*math.cos(alpha1))-(math.sin(alpha1)*math.sin(alpha1)*femur*femur))
    P = math.sqrt(math.pow(maju,2)+math.pow((l+coxa),2)) #panjang diagonal setelah kaki maju
    P = P-coxa
    M = math.sqrt(math.pow(h,2)+math.pow(P,2)) #panjang garis miring antara femur tibia
    sudut_coxa_femur_1_tengah = math.degrees(math.acos((math.pow(femur,2)+math.pow(M,2)-math.pow(tibia,2))/(2*femur*M)))
    sudut_coxa_femur_2_tengah = math.degrees(math.acos((math.pow(M,2)+math.pow(h,2)-math.pow(P,2))/(2*h*M)))
    sudut_coxa_femur_total = sudut_coxa_femur_1_tengah + sudut_coxa_femur_2_tengah
    #print("Besar Sudut Coxa Femur Total : " + str(sudut_coxa_femur_total) + " derajat")
    return sudut_coxa_femur_total
flag = 0

while True:
    if flag == 0:
        sudut = lebar(6.508) #3.776
        flag = 1
    elif flag == 1:
        sudut = lebar(6.508) #6
        flag = 2
    elif flag == 2:
        sudut = lebar(6.508) #6.582
        flag = 0
    #sudut = lebar(4.66) # 3.776 - 4.66 - 6.582
    sudutt = sudut + 45
    if sudutt > 180:
        sudutt = 135
    else:
        sudutt = sudut

    suduttt = (180-sudut)-45
    if suduttt < 0:
        suduttt = 135
    else:
        suduttt = sudut

    print("Sudut Femur 1 2 3 : " + str(sudut + 35))
    print("Sudut Femur 4 5 6 : " + str((180-sudut) - 35))
    print("Sudut Tibia 1 2 3 : " + str(sudutt + 45))
    print("Sudut Tibia 4 5 6 : " + str((180-suduttt) - 45))

    kit1.servo[8].angle = 90 #coxa1
    kit2.servo[7].angle = 90 #coxa6
    kit1.servo[5].angle = 90 #coxa2
    kit2.servo[10].angle = 90 #coxa5
    kit1.servo[2].angle = 90 #coxa3
    kit2.servo[13].angle = 90 #coxa4

    kit1.servo[7].angle = sudut + 35 #femur1 125
    kit2.servo[8].angle = (180-sudut) - 35 #femur6 55
    kit1.servo[4].angle = sudut + 35 #femur2 125 
    kit2.servo[11].angle = (180-sudut) - 35 #femur5 55
    kit1.servo[1].angle = sudut + 35 #femur3 125 
    kit2.servo[14].angle = (180-sudut) - 35 #femur4 55

    kit1.servo[6].angle = (sudutt) + 45 #tibia1 135
    kit2.servo[9].angle = (180-suduttt) - 45 #tibia6 45
    kit1.servo[3].angle = (sudutt) + 45 #tibia2 135
    kit2.servo[12].angle = (180-suduttt) - 45 #tibia5 45
    kit1.servo[0].angle = (sudutt) + 45 #tibia3 135
    kit2.servo[15].angle = (180-suduttt) - 45 #tibia4 45
    sleep(3)

