from time import sleep
from adafruit_servokit import ServoKit

import math

coxa = 2.55
femur = 6.508
tibia = 7.964
l = 6.508

def IK_berdiri():
    maju = 0
    alpha1 = math.asin(l/femur)
    h = math.sqrt(math.pow(femur,2)+math.pow(tibia,2)-(2*femur*tibia*math.cos(alpha1))-(math.sin(alpha1)*math.sin(alpha1)*femur*femur))
    sudut_base_coxa_tengah = math.degrees(math.atan(maju/(l+coxa)))
    P = math.sqrt(math.pow(maju,2)+math.pow((l+coxa),2)) #panjang diagonal setelah kaki maju
    P = P-coxa
    M = math.sqrt(math.pow(h,2)+math.pow(P,2)) #panjang garis miring antara femur tibia
    sudut_coxa_femur_1_tengah = math.degrees(math.acos((math.pow(femur,2)+math.pow(M,2)-math.pow(tibia,2))/(2*femur*M)))
    sudut_coxa_femur_2_tengah = math.degrees(math.acos((math.pow(M,2)+math.pow(h,2)-math.pow(P,2))/(2*h*M)))
    sudut_coxa_femur_total = sudut_coxa_femur_1_tengah + sudut_coxa_femur_2_tengah
    sudut_femur_tibia_tengah = math.degrees(math.acos((math.pow(femur,2)+math.pow(tibia,2)-math.pow(M,2))/(2*tibia*femur)))

    PD = math.sqrt(math.pow(maju,2)+math.pow((l+coxa),2)-(2*maju*(l+coxa)*math.cos(math.radians(135))))
    sudut_base_coxa_depan = math.degrees(math.acos((math.pow((l+coxa),2)+math.pow(PD,2)-math.pow(maju,2))/(2*(l+coxa)*PD)))
    PD = PD-coxa
    MD = math.sqrt(math.pow(h,2)+math.pow(PD,2)) #panjang garis miring antara femur tibia
    sudut_coxa_femur_1_depan = math.degrees(math.acos((math.pow(femur,2)+math.pow(MD,2)-math.pow(tibia,2))/(2*femur*MD)))
    sudut_coxa_femur_2_depan = math.degrees(math.acos((math.pow(MD,2)+math.pow(h,2)-math.pow(PD,2))/(2*h*MD)))
    sudut_coxa_femur_total_depan = sudut_coxa_femur_1_depan + sudut_coxa_femur_2_depan
    sudut_femur_tibia_depan = math.degrees(math.acos((math.pow(femur,2)+math.pow(tibia,2)-math.pow(MD,2))/(2*tibia*femur)))


    PB = math.sqrt(math.pow(maju,2)+math.pow((l+coxa),2)-(2*maju*(l+coxa)*math.cos(math.radians(45))))
    sudut_base_coxa_belakang = math.degrees(math.acos((math.pow((l+coxa),2)+math.pow(PB,2)-math.pow(maju,2))/(2*(l+coxa)*PB)))
    PB = PB - coxa
    MB = math.sqrt(math.pow(h,2)+math.pow(PB,2)) #panjang garis miring antara femur tibia
    sudut_coxa_femur_1_belakang = math.degrees(math.acos((math.pow(femur,2)+math.pow(MB,2)-math.pow(tibia,2))/(2*femur*M)))
    sudut_coxa_femur_2_belakang = math.degrees(math.acos((math.pow(MB,2)+math.pow(h,2)-math.pow(PB,2))/(2*h*MB)))
    sudut_coxa_femur_total_belakang = sudut_coxa_femur_1_belakang + sudut_coxa_femur_2_belakang
    sudut_femur_tibia_belakang = math.degrees(math.acos((math.pow(femur,2)+math.pow(tibia,2)-math.pow(MB,2))/(2*tibia*femur)))
    return (sudut_base_coxa_tengah, sudut_coxa_femur_total, sudut_femur_tibia_tengah, sudut_base_coxa_depan, sudut_coxa_femur_total_depan, sudut_femur_tibia_depan, sudut_base_coxa_belakang, sudut_coxa_femur_total_belakang, sudut_femur_tibia_belakang)
    

def IK_maju(maju):
    alpha1 = math.asin(l/femur)
    h = math.sqrt(math.pow(femur,2)+math.pow(tibia,2)-(2*femur*tibia*math.cos(alpha1))-(math.sin(alpha1)*math.sin(alpha1)*femur*femur))
    sudut_base_coxa_tengah = math.degrees(math.atan(maju/(l+coxa)))
    P = math.sqrt(math.pow(maju,2)+math.pow((l+coxa),2)) #panjang diagonal setelah kaki maju
    P = P-coxa
    M = math.sqrt(math.pow(h,2)+math.pow(P,2)) #panjang garis miring antara femur tibia
    sudut_coxa_femur_1_tengah = math.degrees(math.acos((math.pow(femur,2)+math.pow(M,2)-math.pow(tibia,2))/(2*femur*M)))
    sudut_coxa_femur_2_tengah = math.degrees(math.acos((math.pow(M,2)+math.pow(h,2)-math.pow(P,2))/(2*h*M)))
    sudut_coxa_femur_total = sudut_coxa_femur_1_tengah + sudut_coxa_femur_2_tengah
    sudut_femur_tibia_tengah = math.degrees(math.acos((math.pow(femur,2)+math.pow(tibia,2)-math.pow(M,2))/(2*tibia*femur)))

    PD = math.sqrt(math.pow(maju,2)+math.pow((l+coxa),2)-(2*maju*(l+coxa)*math.cos(math.radians(135))))
    sudut_base_coxa_depan = math.degrees(math.acos((math.pow((l+coxa),2)+math.pow(PD,2)-math.pow(maju,2))/(2*(l+coxa)*PD)))
    PD = PD-coxa
    MD = math.sqrt(math.pow(h,2)+math.pow(PD,2)) #panjang garis miring antara femur tibia
    sudut_coxa_femur_1_depan = math.degrees(math.acos((math.pow(femur,2)+math.pow(MD,2)-math.pow(tibia,2))/(2*femur*MD)))
    sudut_coxa_femur_2_depan = math.degrees(math.acos((math.pow(MD,2)+math.pow(h,2)-math.pow(PD,2))/(2*h*MD)))
    sudut_coxa_femur_total_depan = sudut_coxa_femur_1_depan + sudut_coxa_femur_2_depan
    sudut_femur_tibia_depan = math.degrees(math.acos((math.pow(femur,2)+math.pow(tibia,2)-math.pow(MD,2))/(2*tibia*femur)))

    PB = math.sqrt(math.pow(maju,2)+math.pow((l+coxa),2)-(2*maju*(l+coxa)*math.cos(math.radians(45))))
    sudut_base_coxa_belakang = math.degrees(math.acos((math.pow((l+coxa),2)+math.pow(PB,2)-math.pow(maju,2))/(2*(l+coxa)*PB)))
    PB = PB - coxa
    MB = math.sqrt(math.pow(h,2)+math.pow(PB,2)) #panjang garis miring antara femur tibia
    sudut_coxa_femur_1_belakang = math.degrees(math.acos((math.pow(femur,2)+math.pow(MB,2)-math.pow(tibia,2))/(2*femur*M)))
    sudut_coxa_femur_2_belakang = math.degrees(math.acos((math.pow(MB,2)+math.pow(h,2)-math.pow(PB,2))/(2*h*MB)))
    sudut_coxa_femur_total_belakang = sudut_coxa_femur_1_belakang + sudut_coxa_femur_2_belakang
    sudut_femur_tibia_belakang = math.degrees(math.acos((math.pow(femur,2)+math.pow(tibia,2)-math.pow(MB,2))/(2*tibia*femur)))
    base_coxa_tengah, coxa_femur_tengah, femur_tibia_tengah, base_coxa_depan, coxa_femur_depan, femur_tibia_depan, base_coxa_belakang, coxa_femur_belakang, femur_tibia_belakang = IK_berdiri()

    return (sudut_base_coxa_tengah-base_coxa_tengah, sudut_coxa_femur_total-coxa_femur_tengah, sudut_femur_tibia_tengah - femur_tibia_tengah, sudut_base_coxa_depan - base_coxa_depan, sudut_coxa_femur_total_depan - coxa_femur_depan, sudut_femur_tibia_depan - femur_tibia_depan, sudut_base_coxa_belakang - base_coxa_belakang, sudut_coxa_femur_total_belakang - coxa_femur_belakang, sudut_femur_tibia_belakang - femur_tibia_belakang)


waktu_sleep = 0.2

kit1 = ServoKit(channels = 16, address = 0x41)
kit2 = ServoKit(channels = 16, address = 0x40)


base_coxa_tengah, coxa_femur_tengah, femur_tibia_tengah, base_coxa_depan, coxa_femur_depan, femur_tibia_depan, base_coxa_belakang, coxa_femur_belakang, femur_tibia_belakang = IK_maju(4)


#femur 1 3 5 ngangkat
for i in range(0, 46, 5):
    kit1.servo[7].angle = 125 + i #femur1
    kit1.servo[6].angle = 135 + (i) #tibia1
    kit1.servo[1].angle = 125 + i #femur3
    kit1.servo[0].angle = 135 + (i) #tibia3
    kit2.servo[11].angle = 55 -(i) #femur5
    kit2.servo[12].angle = 45 - (i) #tibia5
print("Femur 1 3 5 Ngangkat")
sleep(waktu_sleep)

try:
    while True:
        #coxa 1 3 5 maju
        kit1.servo[8].angle = 90 + base_coxa_depan #coxa1
        kit1.servo[2].angle = 90 + base_coxa_belakang #coxa3
        kit2.servo[10].angle = 90 - base_coxa_tengah #coxa5
        print("Coxa 1 3 5 Maju")
        sleep(waktu_sleep)
        

        #femur 1 3 5 turun dan tibia turun sekalian adjust ngambil kaki
        kit1.servo[6].angle = 135 - femur_tibia_depan #tibia1
        kit1.servo[0].angle = 135 - femur_tibia_belakang #tibia3
        kit2.servo[12].angle = (45 + femur_tibia_tengah) #tibia5
        kit1.servo[7].angle = 125 + coxa_femur_depan #femur1
        kit1.servo[1].angle = 125 + coxa_femur_belakang #femur3
        kit2.servo[11].angle = (55 - coxa_femur_tengah) #femur5

        print("Femur Tibia 1 3 5 Turun")
        sleep(waktu_sleep)
        #coxa femur tibia 1 3 5 balik ke posisi awal
        kit1.servo[8].angle = 90 #coxa1
        kit1.servo[7].angle = 125 #femur1
        kit1.servo[6].angle = 135 #tibia1

        kit1.servo[2].angle = 90 #coxa3
        kit1.servo[1].angle = 125 #femur3
        kit1.servo[0].angle = 135 #tibia3

        kit2.servo[10].angle = 90 #coxa5
        kit2.servo[11].angle = 55 #femur5
        kit2.servo[12].angle = 45 #tibia5
        print("Coxa Femur Tibia 1 3 5 Balik")
        #sleep(0.05)
        #femur 2 4 6 ngangkat
        for i in range(0, 46, 5):
            kit1.servo[4].angle = 125 + i #femur2
            kit1.servo[3].angle = 135 + (i) #tibia2
            kit2.servo[14].angle = 55 - i #femur4
            kit2.servo[15].angle = 45 - (i) #tibia4
            kit2.servo[8].angle = 55 - i #femur6
            kit2.servo[9].angle = 45 - (i) #tibia6
        print("Femur 2 4 6 Ngangkat")
        sleep(waktu_sleep)

        #coxa 2 4 6 maju
        kit1.servo[5].angle = 90 + base_coxa_tengah #coxa2
        kit2.servo[13].angle = 90 - base_coxa_belakang #coxa4
        kit2.servo[7].angle = 90 - base_coxa_depan #coxa6
        print("Coxa 2 4 6 Maju")
        sleep(waktu_sleep)

        #femur 2 4 6 turun dan tibia turun sekalian adjust ngambil kaki
        kit1.servo[3].angle = 135 - femur_tibia_tengah #tibia2
        kit2.servo[15].angle = (45 + femur_tibia_belakang) #tibia4
        kit2.servo[9].angle = (45 + femur_tibia_depan) #tibia6
        kit1.servo[4].angle = 125 + coxa_femur_tengah #femur2
        kit2.servo[14].angle = (55 - coxa_femur_belakang) #femur4
        kit2.servo[8].angle = (55 - coxa_femur_depan) #femur6

        print("Femur Tibia 2 4 6 Turun")
        sleep(waktu_sleep)
        #coxa femur tibia 2 4 6 balik ke poisi awal
        kit1.servo[5].angle = 90 #coxa2
        kit1.servo[4].angle = 125 #femur2
        kit1.servo[3].angle = 135 #tibia2


        kit2.servo[13].angle = 90 #coxa4
        kit2.servo[14].angle = 55 #femur4
        kit2.servo[15].angle = 45 #tibia4


        kit2.servo[7].angle = 90 #coxa6
        kit2.servo[8].angle = 55 #femur6
        kit2.servo[9].angle = 45 #tibia6
        print("Coxa Femur Tibia 2 4 6 Balik")
        #sleep(0.05)
        #femur 1 3 5 ngangkat
        for i in range(0, 46, 5):
            kit1.servo[7].angle = 125 + i #femur1
            kit1.servo[6].angle = 135 + (i) #tibia1
            kit1.servo[1].angle = 125 + i #femur3
            kit1.servo[0].angle = 135 + (i) #tibia3
            kit2.servo[11].angle = 55 -(i) #femur5
            kit2.servo[12].angle = 45 - (i) #tibia5
        print("Femur 1 3 5 Ngangkat")
        sleep(waktu_sleep)

except KeyboardInterrupt:
	kit1.servo[8].angle = 90 #coxa1
	kit1.servo[7].angle = 125 #femur1
	kit1.servo[6].angle = 135 #tibia1

	kit2.servo[7].angle = 90 #coxa6
	kit2.servo[8].angle = 55 #femur6
	kit2.servo[9].angle = 45 #tibia6

	kit1.servo[5].angle = 90 #coxa2
	kit1.servo[4].angle = 125 #femur2
	kit1.servo[3].angle = 135 #tibia2

	kit2.servo[10].angle = 90 #coxa5
	kit2.servo[11].angle = 55 #femur5
	kit2.servo[12].angle = 45 #tibia5

	kit1.servo[2].angle = 90 #coxa3
	kit1.servo[1].angle = 125 #femur3
	kit1.servo[0].angle = 135 #tibia3

	kit2.servo[13].angle = 90 #coxa4
	kit2.servo[14].angle = 55 #femur4
	kit2.servo[15].angle = 45 #tibia4



