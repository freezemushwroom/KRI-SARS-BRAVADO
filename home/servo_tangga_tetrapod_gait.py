import time
import math
import numpy as np
from adafruit_servokit import ServoKit


kit1 = ServoKit(channels = 16, address = 0x41, reference_clock_speed = 24723456)
kit2 = ServoKit(channels = 16, address = 0x40, reference_clock_speed = 24985600)

for i in range (9):
    kit1.servo[i].set_pulse_width_range(320, 2320)
    kit2.servo[15-i].set_pulse_width_range(400, 2400)

coxa = 2.644
femur = 6.436
tibia = 8.122
l = 6.436

lebar_depan_belakang = 24.5
lebar_tengah = 33.5

panjang_depan_belakang = 23.3
panjang_depan_tengah = 13

mundur = -20
roll = -18
flag = 0
forward = 4
mepet = 0
flag_stop_tangga = 1
yaw = 0


delay = 0.3


def nilai_h(panjang, derajat, maju, geser):
    h = tibia + (math.tan(math.radians(derajat))*panjang)
    alpha1 = math.acos(((femur*tibia)-(math.sqrt((math.pow(femur,2)*math.pow(tibia,2))+(math.pow(femur,2)*(math.pow(h,2)-math.pow(tibia,2))))))/math.pow(femur,2))
    l = math.sin(alpha1)*femur - geser
    return h, l

def IK_tengah(maju, yaw, panjang, roll, geser):
#    h_belakang = tibia + (math.tan(math.radians(abs(min(roll,15))))*panjang_depan_belakang/2)
#    h_tengah = ((panjang_depan_belakang/2)/panjang_depan_belakang)*h_belakang
    h,l = nilai_h(panjang, abs(roll), maju, geser)
    P = math.sqrt(math.pow(maju,2)+math.pow((l+coxa),2)-(2*maju*(l+coxa)*math.cos(math.radians(90-(yaw))))) #panjang diagonal setelah kaki maju
    sudut_base_coxa_tengah = math.degrees(math.acos((math.pow((l+coxa),2)+math.pow(P,2)-math.pow(maju,2))/(2*(l+coxa)*P)))
    P = P-coxa
    M = math.sqrt(math.pow(h,2)+math.pow(P,2)) #panjang garis miring antara femur tibia

    sudut_coxa_femur_1_tengah = math.degrees(math.acos((math.pow(femur,2)+math.pow(M,2)-math.pow(tibia,2))/(2*femur*M)))
    sudut_coxa_femur_2_tengah = math.degrees(math.acos((math.pow(M,2)+math.pow(h,2)-math.pow(P,2))/(2*h*M)))
    sudut_coxa_femur_total = sudut_coxa_femur_1_tengah + sudut_coxa_femur_2_tengah
    sudut_femur_tibia_tengah = math.degrees(math.acos((math.pow(femur,2)+math.pow(tibia,2)-math.pow(M,2))/(2*tibia*femur)))
    return (sudut_base_coxa_tengah, sudut_coxa_femur_total, sudut_femur_tibia_tengah)

def IK_depan(maju,yaw, panjang, roll, geser):
    h,l = nilai_h(panjang, max(-15, roll), maju, geser)
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
    h,l = nilai_h(panjang, -min(roll, 15), maju, geser)
    PB = math.sqrt(math.pow(maju,2)+math.pow((l+coxa),2)-(2*maju*(l+coxa)*math.cos(math.radians((90-mundur-45-(yaw))))))
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

try:
    while True:
        base_coxa_tengah_berdiri, coxa_femur_tengah_berdiri, femur_tibia_tengah_berdiri = IK_tengah(0,0,0,roll, 0)
        base_coxa_depan_berdiri, coxa_femur_depan_berdiri, femur_tibia_depan_berdiri = IK_depan(0,0, panjang_depan_belakang/2, roll, 0)
        base_coxa_belakang_berdiri, coxa_femur_belakang_berdiri, femur_tibia_belakang_berdiri = IK_belakang(0,0, panjang_depan_belakang/2, roll, mundur, 0)

        base_coxa_tengah_kiri, coxa_femur_tengah_kiri, femur_tibia_tengah_kiri = IK_tengah(forward, (yaw), 0, roll, mepet)
        base_coxa_tengah_kiri = base_coxa_tengah_kiri - base_coxa_tengah_berdiri
        coxa_femur_tengah_kiri = coxa_femur_tengah_kiri - coxa_femur_tengah_berdiri
        femur_tibia_tengah_kiri = femur_tibia_tengah_kiri - femur_tibia_tengah_berdiri

        base_coxa_depan_kiri, coxa_femur_depan_kiri, femur_tibia_depan_kiri = IK_depan(forward, (yaw), panjang_depan_belakang/2, roll, mepet)
        base_coxa_depan_kiri = base_coxa_depan_kiri - base_coxa_depan_berdiri
        coxa_femur_depan_kiri = coxa_femur_depan_kiri - coxa_femur_depan_berdiri
        femur_tibia_depan_kiri = femur_tibia_depan_kiri - femur_tibia_depan_berdiri

        base_coxa_belakang_kiri, coxa_femur_belakang_kiri, femur_tibia_belakang_kiri = IK_belakang(-forward, (yaw), panjang_depan_belakang/2, roll, mundur, mepet)
        base_coxa_belakang_kiri = (180-base_coxa_belakang_kiri) - (180-base_coxa_belakang_berdiri)
        coxa_femur_belakang_kiri = coxa_femur_belakang_kiri - coxa_femur_belakang_berdiri
        femur_tibia_belakang_kiri = femur_tibia_belakang_kiri - femur_tibia_belakang_berdiri

        base_coxa_tengah_kanan, coxa_femur_tengah_kanan, femur_tibia_tengah_kanan = IK_tengah(forward, ((-yaw)), 0, roll, -mepet)
        base_coxa_tengah_kanan = base_coxa_tengah_kanan - base_coxa_tengah_berdiri
        coxa_femur_tengah_kanan = coxa_femur_tengah_kanan - coxa_femur_tengah_berdiri
        femur_tibia_tengah_kanan = femur_tibia_tengah_kanan - femur_tibia_tengah_berdiri

        base_coxa_depan_kanan, coxa_femur_depan_kanan, femur_tibia_depan_kanan = IK_depan(forward, ((-yaw)), panjang_depan_belakang/2, roll, -mepet)
        base_coxa_depan_kanan = base_coxa_depan_kanan - base_coxa_depan_berdiri
        coxa_femur_depan_kanan = coxa_femur_depan_kanan - coxa_femur_depan_berdiri
        femur_tibia_depan_kanan = femur_tibia_depan_kanan - femur_tibia_depan_berdiri

        base_coxa_belakang_kanan, coxa_femur_belakang_kanan, femur_tibia_belakang_kanan = IK_belakang(-forward, ((-yaw)), panjang_depan_belakang/2, roll, mundur, -mepet)
        base_coxa_belakang_kanan = (180-base_coxa_belakang_kanan) - (180-base_coxa_belakang_berdiri)
        coxa_femur_belakang_kanan = coxa_femur_belakang_kanan - coxa_femur_belakang_berdiri
        femur_tibia_belakang_kanan = femur_tibia_belakang_kanan - femur_tibia_belakang_berdiri

        #femur tibia 1 6 angkat
        kit1.servo[7].angle = max(0, min(((coxa_femur_depan_berdiri+35) + 60), 180)) #femur1
        kit1.servo[6].angle = max(0, min((180 - (femur_tibia_depan_berdiri-45) + 60), 180)) #tibia1
        kit2.servo[8].angle = max(0, min((180 - (coxa_femur_depan_berdiri+35) - 60), 180)) #femur6
        kit2.servo[9].angle =  max(0, min(((femur_tibia_depan_berdiri-45) - 60), 180)) #tibia6

        #coxa 1 6 mundur
        kit1.servo[8].angle = max(0, min((90 - 20), 180))
        kit2.servo[7].angle = max(0, min((90 + 20), 180))

        #tibia 1 6 naik
        kit1.servo[6].angle = max(0, min((180 - (femur_tibia_depan_berdiri-45)-30), 180))
        kit2.servo[9].angle = max(0, min(((femur_tibia_depan_berdiri - 45)+30), 180))
        wait(0.3)

        #coxa 1 6 maju
        kit1.servo[8].angle = max(0, min((90 + base_coxa_depan_kiri), 180)) #coxa1
        kit2.servo[7].angle = max(0, min((90 - base_coxa_depan_kanan), 180)) #coxa6
        wait(delay)

        #femur 1 turun
        kit1.servo[6].angle = max(0, min((180 - (femur_tibia_depan_berdiri-45) - femur_tibia_depan_kiri), 180)) #tibia1
        kit2.servo[9].angle = max(0, min(((femur_tibia_depan_berdiri-45) + femur_tibia_depan_kanan), 180)) #tibia6
        wait(0.1)
        kit1.servo[7].angle = max(0, min(((coxa_femur_depan_berdiri+35) + coxa_femur_depan_kiri), 180)) #femur1
        kit2.servo[8].angle = max(0, min((180 - (coxa_femur_depan_berdiri+35) - coxa_femur_depan_kanan), 180)) #femur6
        wait(delay)

        #femur tibia 2 5 angkat
        kit1.servo[4].angle = max(0, min(((coxa_femur_tengah_berdiri+35) + 30), 180)) #femur2
        kit1.servo[3].angle = max(0, min((180 - (femur_tibia_tengah_berdiri-45) + 30), 180)) #tibia2
        kit2.servo[11].angle = max(0, min((180 - (coxa_femur_tengah_berdiri+35) - 30), 180)) #femur5
        kit2.servo[12].angle = max(0, min(((femur_tibia_tengah_berdiri-45) - 30), 180)) #tibia5

        wait(delay)

        #coxa 2 5 maju
        kit1.servo[5].angle = max(0, min((90 + base_coxa_tengah_kiri), 180)) #coxa2
        kit2.servo[10].angle = max(0, min((90 - base_coxa_tengah_kanan), 180)) #coxa5

        wait(delay)

        #femur tibia 2 5 turun
        kit1.servo[3].angle = max(0, min((180 - (femur_tibia_tengah_berdiri-45) - femur_tibia_tengah_kiri), 180)) #tibia2
        kit2.servo[12].angle = max(0, min(((femur_tibia_tengah_berdiri-45) + femur_tibia_tengah_kanan), 180)) #tibia5
        wait(0.05)
        kit1.servo[4].angle = max(0, min(((coxa_femur_tengah_berdiri+35) + coxa_femur_tengah_kiri), 180)) #femur2
        kit2.servo[11].angle = max(0, min((180 - (coxa_femur_tengah_berdiri+35)- coxa_femur_tengah_kanan), 180)) #femur5

        wait(delay)

        #kaki 1 2 5 6 balik ke posisi awal, kaki 3 4 mundur dengan coxa femur tibianya mundur
        kit1.servo[8].angle = 90 #coxa1
        kit1.servo[7].angle = (coxa_femur_depan_berdiri+35) #femur1
        kit1.servo[6].angle = 180 - (femur_tibia_depan_berdiri-45) #tibia1

        kit1.servo[5].angle = 90 #coxa2
        kit1.servo[4].angle = (coxa_femur_tengah_berdiri+35) #femur2
        kit1.servo[3].angle = 180 -(femur_tibia_tengah_berdiri-45) #tibia2

        kit2.servo[10].angle = 90 #coxa5
        kit2.servo[11].angle = 180 - (coxa_femur_tengah_berdiri+35) #femur5
        kit2.servo[12].angle = (femur_tibia_tengah_berdiri-45) #tibia5

        kit2.servo[7].angle = 90 #coxa6
        kit2.servo[8].angle = 180 - (coxa_femur_depan_berdiri+35) #femur6
        kit2.servo[9].angle = (femur_tibia_depan_berdiri-45) #tibia6

        kit1.servo[2].angle = max(0, min((90 - mundur + base_coxa_belakang_kiri), 180)) #coxa3
        kit1.servo[1].angle = max(0, min(((coxa_femur_belakang_berdiri+35) + coxa_femur_belakang_kiri), 180)) #femur3
        kit1.servo[0].angle = max(0, min((180 - (femur_tibia_belakang_berdiri-45) - femur_tibia_belakang_kiri), 180)) #tibia3

        kit2.servo[13].angle = max(0, min((90 + mundur - base_coxa_belakang_kanan), 180)) #coxa4
        kit2.servo[14].angle = max(0, min((180 - (coxa_femur_belakang_berdiri+35) - coxa_femur_belakang_kanan), 180)) #femur4
        kit2.servo[15].angle = max(0, min(((femur_tibia_belakang_berdiri-45) + femur_tibia_belakang_kanan), 180)) #tibia4

        wait(delay)

        #femur tibia 3 4 angkat
        kit1.servo[1].angle = max(0, min(((coxa_femur_belakang_berdiri+35) + 60), 180)) #femur3
        kit1.servo[0].angle = max(0, min((180 - (femur_tibia_belakang_berdiri-45) + 100), 180)) #tibia3
        wait(0.5)

        #coxa 3 balik ke posisi awal
        kit1.servo[2].angle = 90 - mundur #coxa3

        #femur 3 turun ke posisi awal
        kit1.servo[1].angle = (coxa_femur_belakang_berdiri+35) #femur3
        kit1.servo[0].angle = 180 - (femur_tibia_belakang_berdiri-45) #tibia3
        wait(delay)

        #femur tibia 4 angkat
        kit2.servo[14].angle = max(0, min((180 - (coxa_femur_belakang_berdiri+35) - 60), 180)) #femur4
        kit2.servo[15].angle = max(0, min(((femur_tibia_belakang_berdiri-45) - 100), 180)) #tibia4
        wait(0.5)

        #coxa 4 balik ke posisi awal
        kit2.servo[13].angle = 90 + mundur #coxa4

        #femur 4 turun ke posisi awal
        kit2.servo[14].angle = 180 - (coxa_femur_belakang_berdiri+35) #femur4
        kit2.servo[15].angle = (femur_tibia_belakang_berdiri-45) #tibia4

        wait(delay)





except KeyboardInterrupt:
    kit1.servo[8].angle = 90 #coxa1
    kit1.servo[7].angle = (coxa_femur_depan_berdiri+35) #femur1
    kit1.servo[6].angle = 180 - (femur_tibia_depan_berdiri-45) #tibia1

    kit2.servo[7].angle = 180 - 90 #coxa6
    kit2.servo[8].angle = 180 - (coxa_femur_depan_berdiri+35) #femur6
    kit2.servo[9].angle = (femur_tibia_depan_berdiri-45) #tibia6

    kit1.servo[5].angle = 90 #coxa2
    kit1.servo[4].angle = (coxa_femur_tengah_berdiri+35) #femur2
    kit1.servo[3].angle = 180 - (femur_tibia_tengah_berdiri-45) #tibia2

    kit2.servo[10].angle = 180 - 90 #coxa5
    kit2.servo[11].angle = 180 - (coxa_femur_tengah_berdiri+35) #femur5
    kit2.servo[12].angle = (femur_tibia_tengah_berdiri-45) #tibia5

    kit1.servo[2].angle = 90 - mundur #coxa3
    kit1.servo[1].angle = (coxa_femur_belakang_berdiri+35) #femur3
    kit1.servo[0].angle = 180 - (femur_tibia_belakang_berdiri-45) #tibia3

    kit2.servo[13].angle = 180 - 90 + mundur #coxa4
    kit2.servo[14].angle = 180 - (coxa_femur_belakang_berdiri+35) #femur4
    kit2.servo[15].angle = (femur_tibia_belakang_berdiri-45) #tibia4

