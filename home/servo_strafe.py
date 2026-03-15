import time
import math
import numpy as np
from adafruit_servokit import ServoKit

kit1 = ServoKit(channels=16, address=0x41)
kit2 = ServoKit(channels=16, address=0x40)

for i in range (9):
    kit1.servo[i].set_pulse_width_range(320, 2320)
    kit2.servo[15-i].set_pulse_width_range(400, 2400)


coxa = 2.644
femur = 6.436
tibia = 8.122
l = 6.436
maju = 3.8
forward = maju
gait = 2
#0 tripod, 1 wave, 2 tetrapod
geser = -4
roll = -6
mundur = 0

delay = 0.4

lebar_depan_belakang = 24.5
lebar_tengah = 33.5

panjang_depan_belakang = 23.3
panjang_depan_tengah = 13


def nilai_h(panjang, derajat, maju, geser, nambah):
    h = tibia + (math.tan(math.radians(derajat))*panjang) + nambah
    alpha1 = math.acos(((femur*tibia)-(math.sqrt((math.pow(femur,2)*math.pow(tibia,2))+(math.pow(femur,2)*(math.pow(h,2)-math.pow(tibia,2))))))/math.pow(femur,2))
    l = math.sin(alpha1)*femur - geser
    return h, l


def IK_tengah(maju, yaw, panjang, roll, geser, nambah):
#    h_belakang = tibia + (math.tan(math.radians(abs(min(roll,15))))*panjang_depan_belakang/2)
#    h_tengah = ((panjang_depan_belakang/2)/panjang_depan_belakang)*h_belakang
    h,l = nilai_h(panjang, abs(roll), maju, geser, nambah)
    P = math.sqrt(math.pow(maju,2)+math.pow((l+coxa),2)-(2*maju*(l+coxa)*math.cos(math.radians(90-(yaw)-30)))) #panjang diagonal setelah kaki maju
    sudut_base_coxa_tengah = math.degrees(math.acos((math.pow((l+coxa),2)+math.pow(P,2)-math.pow(maju,2))/(2*(l+coxa)*P)))
    P = P-coxa
    M = math.sqrt(math.pow(h,2)+math.pow(P,2)) #panjang garis miring antara femur tibia

    sudut_coxa_femur_1_tengah = math.degrees(math.acos((math.pow(femur,2)+math.pow(M,2)-math.pow(tibia,2))/(2*femur*M)))
    sudut_coxa_femur_2_tengah = math.degrees(math.acos((math.pow(M,2)+math.pow(h,2)-math.pow(P,2))/(2*h*M)))
    sudut_coxa_femur_total = sudut_coxa_femur_1_tengah + sudut_coxa_femur_2_tengah
    sudut_femur_tibia_tengah = math.degrees(math.acos((math.pow(femur,2)+math.pow(tibia,2)-math.pow(M,2))/(2*tibia*femur)))
    return (sudut_base_coxa_tengah, sudut_coxa_femur_total, sudut_femur_tibia_tengah)

def IK_depan(maju,yaw, panjang, roll, geser):
    h,l = nilai_h(panjang, max(-15, roll), maju, geser, 0)
    PD = math.sqrt(math.pow(maju,2)+math.pow((l+coxa),2)-(2*maju*(l+coxa)*math.cos(math.radians(135-(yaw)))))
    sudut_base_coxa_depan = math.degrees(math.acos((math.pow((l+coxa),2)+math.pow(PD,2)-math.pow(maju,2))/(2*(l+coxa)*PD)))
    PD = PD-coxa
    MD = math.sqrt(math.pow(h,2)+math.pow(PD,2)) #panjang garis miring antara femur tibia
    sudut_coxa_femur_1_depan = math.degrees(math.acos((math.pow(femur,2)+math.pow(MD,2)-math.pow(tibia,2))/(2*femur*MD)))
    sudut_coxa_femur_2_depan = math.degrees(math.acos((math.pow(MD,2)+math.pow(h,2)-math.pow(PD,2))/(2*h*MD)))
    sudut_coxa_femur_total_depan = sudut_coxa_femur_1_depan + sudut_coxa_femur_2_depan
    sudut_femur_tibia_depan = math.degrees(math.acos((math.pow(femur,2)+math.pow(tibia,2)-math.pow(MD,2))/(2*tibia*femur)))
    return(sudut_base_coxa_depan, sudut_coxa_femur_total_depan, sudut_femur_tibia_depan)

def IK_belakang(maju, yaw, panjang, roll, mundur, geser):
    h,l = nilai_h(panjang, -min(roll, 15), maju, geser, 0)
    PB = math.sqrt(math.pow(maju,2)+math.pow((l+coxa),2)-(2*maju*(l+coxa)*math.cos(math.radians(90-30-mundur-45-(yaw)))))
    sudut_base_coxa_belakang = math.degrees(math.acos((math.pow((l+coxa),2)+math.pow(PB,2)-math.pow(maju,2))/(2*(l+coxa)*PB)))
    PB = PB - coxa
    MB = math.sqrt(math.pow(h,2)+math.pow(PB,2)) #panjang garis miring antara femur tibia
    sudut_coxa_femur_1_belakang = math.degrees(math.acos((math.pow(femur,2)+math.pow(MB,2)-math.pow(tibia,2))/(2*femur*MB)))
    sudut_coxa_femur_2_belakang = math.degrees(math.acos((math.pow(MB,2)+math.pow(h,2)-math.pow(PB,2))/(2*h*MB)))
    sudut_coxa_femur_total_belakang = sudut_coxa_femur_1_belakang + sudut_coxa_femur_2_belakang
    sudut_femur_tibia_belakang = math.degrees(math.acos((math.pow(femur,2)+math.pow(tibia,2)-math.pow(MB,2))/(2*tibia*femur)))
    return(sudut_base_coxa_belakang, sudut_coxa_femur_total_belakang, sudut_femur_tibia_belakang)

def wait(waktu):
    flag = True
    myTime = time.time()
    while flag == True:
        currentTime = time.time()
        if currentTime - myTime < waktu:
            flag = True
        elif currentTime - myTime >= waktu:
            flag = False

base_coxa_tengah_berdiri, coxa_femur_tengah_berdiri, femur_tibia_tengah_berdiri = IK_tengah(0, 0, 0, roll, 0, 0)
base_coxa_depan_berdiri, coxa_femur_depan_berdiri, femur_tibia_depan_berdiri = IK_depan(0,0, panjang_depan_belakang/2, roll, 0)
base_coxa_belakang_berdiri, coxa_femur_belakang_berdiri, femur_tibia_belakang_berdiri = IK_belakang(0,0, panjang_depan_belakang/2, roll, mundur, 0)

base_coxa_tengah_kiri, coxa_femur_tengah_kiri, femur_tibia_tengah_kiri = IK_tengah(0, 0, 0, 0, geser,0)
base_coxa_tengah_kiri = base_coxa_tengah_kiri - base_coxa_tengah_berdiri
coxa_femur_tengah_kiri = coxa_femur_tengah_kiri - coxa_femur_tengah_berdiri
femur_tibia_tengah_kiri = femur_tibia_tengah_kiri - femur_tibia_tengah_berdiri

base_coxa_depan_kiri, coxa_femur_depan_kiri, femur_tibia_depan_kiri = IK_depan(0,0, panjang_depan_belakang/2, 0, geser)
base_coxa_depan_kiri = base_coxa_depan_kiri - base_coxa_depan_berdiri
coxa_femur_depan_kiri = coxa_femur_depan_kiri - coxa_femur_depan_berdiri
femur_tibia_depan_kiri = femur_tibia_depan_kiri - femur_tibia_depan_berdiri

base_coxa_belakang_kiri, coxa_femur_belakang_kiri, femur_tibia_belakang_kiri = IK_belakang(0,0, panjang_depan_belakang/2, 0, 0, geser)
base_coxa_belakang_kiri = base_coxa_belakang_kiri - base_coxa_belakang_berdiri
coxa_femur_belakang_kiri = coxa_femur_belakang_kiri - coxa_femur_belakang_berdiri
femur_tibia_belakang_kiri = femur_tibia_belakang_kiri - femur_tibia_belakang_berdiri

base_coxa_tengah_kanan, coxa_femur_tengah_kanan, femur_tibia_tengah_kanan = IK_tengah(0,0,0, 0, -geser, 0)
base_coxa_tengah_kanan = base_coxa_tengah_kanan - base_coxa_tengah_berdiri
coxa_femur_tengah_kanan = coxa_femur_tengah_kanan - coxa_femur_tengah_berdiri
femur_tibia_tengah_kanan = femur_tibia_tengah_kanan - femur_tibia_tengah_berdiri

base_coxa_depan_kanan, coxa_femur_depan_kanan, femur_tibia_depan_kanan = IK_depan(0,0, panjang_depan_belakang/2, 0, -geser)
base_coxa_depan_kanan = base_coxa_depan_kanan - base_coxa_depan_berdiri
coxa_femur_depan_kanan = coxa_femur_depan_kanan - coxa_femur_depan_berdiri
femur_tibia_depan_kanan = femur_tibia_depan_kanan - femur_tibia_depan_berdiri

base_coxa_belakang_kanan, coxa_femur_belakang_kanan, femur_tibia_belakang_kanan = IK_belakang(0,0, panjang_depan_belakang/2, 0, 0, -geser)
base_coxa_belakang_kanan = base_coxa_belakang_kanan - base_coxa_belakang_berdiri
coxa_femur_belakang_kanan = coxa_femur_belakang_kanan - coxa_femur_belakang_berdiri
femur_tibia_belakang_kanan = femur_tibia_belakang_kanan - femur_tibia_belakang_berdiri

data = [int(base_coxa_tengah_kiri), int(coxa_femur_tengah_kiri), int(femur_tibia_tengah_kiri), int(base_coxa_depan_kiri), int(coxa_femur_depan_kiri),int(femur_tibia_depan_kiri), int(base_coxa_belakang_kiri), int(coxa_femur_belakang_kiri), int(femur_tibia_belakang_kiri), int(base_coxa_tengah_kanan), int(coxa_femur_tengah_kanan), int(femur_tibia_tengah_kanan), int(base_coxa_depan_kanan), int(coxa_femur_depan_kanan), int(femur_tibia_depan_kanan), int(base_coxa_belakang_kanan), int(coxa_femur_belakang_kanan), int(femur_tibia_belakang_kanan), int(coxa_femur_tengah_berdiri+35), int(femur_tibia_tengah_berdiri-45), int(coxa_femur_depan_berdiri+35), int(femur_tibia_depan_berdiri-45), int(coxa_femur_belakang_berdiri+35), int(femur_tibia_belakang_berdiri-45), 0]


#coxa 1 3 4 6 geser 

kit1.servo[8].angle = 90 - 30 #coxa1
kit1.servo[2].angle = 90 + 30 #coxa3
kit2.servo[13].angle = 90 - 30 #coxa4
kit2.servo[7].angle = 90 + 30 #coxa6
wait(delay)

try:
    while True:
        #femur angkat
        kit1.servo[7].angle = max(0, min((data[11+9] + 30), 180)) #femur1
        kit1.servo[6].angle = max(0, min((180 - data[12+9] + 30), 180)) #tibia1
        kit1.servo[1].angle = max(0, min((data[13+9] + 30), 180)) #femur3
        kit1.servo[0].angle = max(0, min((180 - data[14+9] + 30), 180)) #tibia3
        kit2.servo[11].angle = max(0, min((180 - data[9+9] - 30), 180)) #femur5
#        kit2.servo[12].angle = max(0, min((data[10+9] - 30), 180)) #tibia5
        wait(delay)

        #femur 1 3 5 turun dan tibia turun sekalian adjust ngambil kaki
        kit1.servo[6].angle = max(0, min((180 - data[12+9] - data[5]), 180)) #tibia1
        kit1.servo[0].angle = max(0, min((180 - data[14+9] - data[8]), 180)) #tibia3
        kit2.servo[12].angle = 0 #max(0, min((data[10+9] + data[2+9] - 10), 180)) #tibia5
        wait(0.3)
        kit1.servo[7].angle = max(0, min((data[11+9] + data[4]), 180)) #femur1
        kit1.servo[1].angle = max(0, min((data[13+9] + data[7]), 180)) #femur3
        kit2.servo[11].angle = max(0, min((180 - data[9+9]- data[1+9]), 180)) #femur5

        wait(delay)

        # femur tibia 1 3 5 balik ke posisi awal
        kit1.servo[7].angle = data[11+9] #femur1
        kit1.servo[6].angle = 180 - data[12+9] #tibia1

        kit1.servo[1].angle = data[13+9] #femur3
        kit1.servo[0].angle = 180 - data[14+9] #tibia3

        kit2.servo[11].angle = 180 - data[9+9] #femur5
        kit2.servo[12].angle = data[10+9] #tibia5

        wait(0.02)

        kit1.servo[4].angle = max(0, min((data[9+9] + 30), 180)) #femur2
        kit1.servo[3].angle = max(0, min((180 - data[10+9] + 30), 180)) #tibia2
        kit2.servo[14].angle = max(0, min((180 - data[13+9] - 30), 180)) #femur4
#        kit2.servo[15].angle = max(0, min((data[14+9] - 30), 180)) #tibia4
        kit2.servo[8].angle = max(0, min((180 - data[11+9] - 30), 180)) #femur6
#        kit2.servo[9].angle =  max(0, min((data[12+9] - 30), 180)) #tibia6
        wait(delay)

        #femur 2 4 6 turun dan tibia turun sekalian adjust ngambil kaki
        kit1.servo[3].angle = max(0, min((180 - data[10+9] - data[2]), 180)) #tibia2
        kit2.servo[15].angle = max(0, min((data[14+9] + data[8+9] - 10), 180)) #tibia4
        kit2.servo[9].angle = max(0, min((data[12+9] + data[5+9] - 10), 180)) #tibia6
        wait(0.3)
        kit1.servo[4].angle = max(0, min((data[9+9] + data[1]), 180)) #femur2
        kit2.servo[14].angle = max(0, min((180 - data[13+9] - data[7+9]), 180)) #femur4
        kit2.servo[8].angle = max(0, min((180 - data[11+9] - data[4+9]), 180)) #femur6
        wait(delay)

        #femur tibia 2 4 6 balik ke poisi awal
        kit1.servo[4].angle = data[9+9] #femur2
        kit1.servo[3].angle = 180 -data[10+9] #tibia2

        kit2.servo[14].angle = 180 - data[13+9] #femur4
        kit2.servo[15].angle = data[14+9] #tibia4

        kit2.servo[8].angle = 180 - data[11+9] #femur6
        kit2.servo[9].angle = data[12+9] #tibia6

except KeyboardInterrupt:
    kit1.servo[7].angle = data[11+9] #femur1
    kit1.servo[6].angle = 180 - data[12+9] #tibia1

    kit1.servo[1].angle = data[13+9] #femur3
    kit1.servo[0].angle = 180 - data[14+9] #tibia3

    kit2.servo[11].angle = 180 - data[9+9] #femur5
    kit2.servo[12].angle = data[10+9] #tibia5

    kit1.servo[4].angle = data[9+9] #femur2
    kit1.servo[3].angle = 180 -data[10+9] #tibia2

    kit2.servo[14].angle = 180 - data[13+9] #femur4
    kit2.servo[15].angle = data[14+9] #tibia4

    kit2.servo[8].angle = 180 - data[11+9] #femur6
    kit2.servo[9].angle = data[12+9] #tibia6
