from time import sleep
from adafruit_servokit import ServoKit

import math

coxa = 2.55
femur = 6.508
tibia = 7.964
l = 6.508
forward = 4
derajat_yaw = 0

lebar_depan_belakang = 24.5
lebar_tengah = 33.5

panjang_depan_tengah = 11.4
panjang_depan_belakang = 23.3

if derajat_yaw > 6:
    yaw = 6
elif derajat_yaw < -6:
    yaw = -6
else:
    yaw = derajat_yaw
forward_compen_depan_belakang = math.tan(math.radians(yaw))*lebar_depan_belakang
forward_compen_tengah = math.tan(math.radians(yaw))*lebar_tengah

if yaw > 0:
    forward_kiri_depan_belakang = forward
    forward_kiri_tengah = forward
    forward_kanan_depan_belakang = forward - forward_compen_depan_belakang
    forward_kanan_tengah = forward - forward_compen_tengah
elif yaw < 0:
    forward_kiri_depan_belakang = forward + forward_compen_depan_belakang
    forward_kiri_tengah = forward + forward_compen_tengah
    forward_kanan_depan_belakang = forward
    forward_kanan_tengah = forward
else:
    forward_kiri_depan_belakang = forward
    forward_kiri_tengah = forward
    forward_kanan_depan_belakang = forward
    forward_kanan_tengah = forward

def h_fix():
    alpha1 = math.asin(l/femur)
    h = math.sqrt(math.pow(femur,2)+math.pow(tibia,2)-(2*femur*tibia*math.cos(alpha1))-(math.sin(alpha1)*math.sin(alpha1)*femur*femur))
    return h


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
    sudut_coxa_femur_1_belakang = math.degrees(math.acos((math.pow(femur,2)+math.pow(MB,2)-math.pow(tibia,2))/(2*femur*MB)))
    sudut_coxa_femur_2_belakang = math.degrees(math.acos((math.pow(MB,2)+math.pow(h,2)-math.pow(PB,2))/(2*h*MB)))
    sudut_coxa_femur_total_belakang = sudut_coxa_femur_1_belakang + sudut_coxa_femur_2_belakang
    sudut_femur_tibia_belakang = math.degrees(math.acos((math.pow(femur,2)+math.pow(tibia,2)-math.pow(MB,2))/(2*tibia*femur)))
    return (sudut_base_coxa_tengah, sudut_coxa_femur_total, sudut_femur_tibia_tengah, sudut_base_coxa_depan, sudut_coxa_femur_total_depan, sudut_femur_tibia_depan, sudut_base_coxa_belakang, sudut_coxa_femur_total_belakang, sudut_femur_tibia_belakang)

base_coxa_tengah_berdiri, coxa_femur_tengah_berdiri, femur_tibia_tengah_berdiri, base_coxa_depan_berdiri, coxa_femur_depan_berdiri, femur_tibia_depan_berdiri, base_coxa_belakang_berdiri, coxa_femur_belakang_berdiri, femur_tibia_belakang_berdiri = IK_berdiri()

def IK_maju_tengah(maju,derajat):
    h = h_fix()
    P = math.sqrt(math.pow(maju,2)+math.pow((l+coxa),2)-(2*maju*(l+coxa)*math.cos(math.radians(90-(derajat))))) #panjang diagonal setelah kaki maju
    sudut_base_coxa_tengah = math.degrees(math.acos((math.pow((l+coxa),2)+math.pow(P,2)-math.pow(maju,2))/(2*(l+coxa)*P)))
    P = P-coxa
    M = math.sqrt(math.pow(h,2)+math.pow(P,2)) #panjang garis miring antara femur tibia

    sudut_coxa_femur_1_tengah = math.degrees(math.acos((math.pow(femur,2)+math.pow(M,2)-math.pow(tibia,2))/(2*femur*M)))
    sudut_coxa_femur_2_tengah = math.degrees(math.acos((math.pow(M,2)+math.pow(h,2)-math.pow(P,2))/(2*h*M)))
    sudut_coxa_femur_total = sudut_coxa_femur_1_tengah + sudut_coxa_femur_2_tengah
    sudut_femur_tibia_tengah = math.degrees(math.acos((math.pow(femur,2)+math.pow(tibia,2)-math.pow(M,2))/(2*tibia*femur)))
    return (sudut_base_coxa_tengah-base_coxa_tengah_berdiri, sudut_coxa_femur_total-coxa_femur_tengah_berdiri, sudut_femur_tibia_tengah - femur_tibia_tengah_berdiri)
            
def IK_maju_depan(maju,derajat):
    h = h_fix()
    PD = math.sqrt(math.pow(maju,2)+math.pow((l+coxa),2)-(2*maju*(l+coxa)*math.cos(math.radians(135-(derajat)))))
    sudut_base_coxa_depan = math.degrees(math.acos((math.pow((l+coxa),2)+math.pow(PD,2)-math.pow(maju,2))/(2*(l+coxa)*PD)))
    PD = PD-coxa
    MD = math.sqrt(math.pow(h,2)+math.pow(PD,2)) #panjang garis miring antara femur tibia
    sudut_coxa_femur_1_depan = math.degrees(math.acos((math.pow(femur,2)+math.pow(MD,2)-math.pow(tibia,2))/(2*femur*MD)))
    sudut_coxa_femur_2_depan = math.degrees(math.acos((math.pow(MD,2)+math.pow(h,2)-math.pow(PD,2))/(2*h*MD)))
    sudut_coxa_femur_total_depan = sudut_coxa_femur_1_depan + sudut_coxa_femur_2_depan
    sudut_femur_tibia_depan = math.degrees(math.acos((math.pow(femur,2)+math.pow(tibia,2)-math.pow(MD,2))/(2*tibia*femur)))
    return(sudut_base_coxa_depan - base_coxa_depan_berdiri, sudut_coxa_femur_total_depan - coxa_femur_depan_berdiri, sudut_femur_tibia_depan - femur_tibia_depan_berdiri)
           
def IK_maju_belakang(maju,derajat):
    h = h_fix()
    PB = math.sqrt(math.pow(maju,2)+math.pow((l+coxa),2)-(2*maju*(l+coxa)*math.cos(math.radians(45-(derajat)))))
    sudut_base_coxa_belakang = math.degrees(math.acos((math.pow((l+coxa),2)+math.pow(PB,2)-math.pow(maju,2))/(2*(l+coxa)*PB)))
    PB = PB - coxa
    MB = math.sqrt(math.pow(h,2)+math.pow(PB,2)) #panjang garis miring antara femur tibia
    sudut_coxa_femur_1_belakang = math.degrees(math.acos((math.pow(femur,2)+math.pow(MB,2)-math.pow(tibia,2))/(2*femur*MB)))
    sudut_coxa_femur_2_belakang = math.degrees(math.acos((math.pow(MB,2)+math.pow(h,2)-math.pow(PB,2))/(2*h*MB)))
    sudut_coxa_femur_total_belakang = sudut_coxa_femur_1_belakang + sudut_coxa_femur_2_belakang
    sudut_femur_tibia_belakang = math.degrees(math.acos((math.pow(femur,2)+math.pow(tibia,2)-math.pow(MB,2))/(2*tibia*femur)))

    return(sudut_base_coxa_belakang - base_coxa_belakang_berdiri, sudut_coxa_femur_total_belakang - coxa_femur_belakang_berdiri, sudut_femur_tibia_belakang - femur_tibia_belakang_berdiri)
print(IK_maju_tengah (forward_kiri_tengah, yaw))
print(IK_maju_depan(forward_kiri_depan_belakang, yaw))
print(IK_maju_belakang(forward_kiri_depan_belakang, yaw))

print(IK_maju_tengah (forward_kanan_tengah, yaw))
print(IK_maju_depan(forward_kanan_depan_belakang, yaw))
print(IK_maju_belakang(forward_kanan_depan_belakang, yaw))



waktu_sleep = 0.2

kit1 = ServoKit(channels = 16, address = 0x41)
kit2 = ServoKit(channels = 16, address = 0x40)

base_coxa_tengah_kiri, coxa_femur_tengah_kiri, femur_tibia_tengah_kiri = IK_maju_tengah(forward_kiri_tengah,(yaw))
base_coxa_depan_kiri, coxa_femur_depan_kiri, femur_tibia_depan_kiri = IK_maju_depan(forward_kiri_depan_belakang,(yaw))
base_coxa_belakang_kiri, coxa_femur_belakang_kiri, femur_tibia_belakang_kiri = IK_maju_belakang(forward_kiri_depan_belakang,(yaw))

base_coxa_tengah_kanan, coxa_femur_tengah_kanan, femur_tibia_tengah_kanan = IK_maju_tengah(forward_kanan_tengah,((-yaw)))
base_coxa_depan_kanan, coxa_femur_depan_kanan, femur_tibia_depan_kanan = IK_maju_depan(forward_kanan_depan_belakang,((-yaw)))
base_coxa_belakang_kanan, coxa_femur_belakang_kanan, femur_tibia_belakang_kanan = IK_maju_belakang(forward_kanan_depan_belakang,((-yaw)))

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
        kit1.servo[8].angle = 90 + base_coxa_depan_kiri #coxa1
        kit1.servo[2].angle = 90 + base_coxa_belakang_kiri #coxa3
        kit2.servo[10].angle = 90 - base_coxa_tengah_kanan #coxa5
        print("Coxa 1 3 5 Maju")
        sleep(waktu_sleep)
        

        #femur 1 3 5 turun dan tibia turun sekalian adjust ngambil kaki
        kit1.servo[6].angle = 135 - femur_tibia_depan_kiri #tibia1
        kit1.servo[0].angle = 135 - femur_tibia_belakang_kiri #tibia3
        kit2.servo[12].angle = (45 + femur_tibia_tengah_kanan) #tibia5
        sleep(0.1)
        kit1.servo[7].angle = 125 + coxa_femur_depan_kiri #femur1
        kit1.servo[1].angle = 125 + coxa_femur_belakang_kiri #femur3
        kit2.servo[11].angle = (55 - coxa_femur_tengah_kanan) #femur5

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
        kit1.servo[5].angle = 90 + base_coxa_tengah_kiri #coxa2
        kit2.servo[13].angle = 90 - base_coxa_belakang_kanan #coxa4
        kit2.servo[7].angle = 90 - base_coxa_depan_kanan #coxa6
        print("Coxa 2 4 6 Maju")
        sleep(waktu_sleep)

        #femur 2 4 6 turun dan tibia turun sekalian adjust ngambil kaki
        kit1.servo[3].angle = 135 - femur_tibia_tengah_kiri #tibia2
        kit2.servo[15].angle = (45 + femur_tibia_belakang_kanan) #tibia4
        kit2.servo[9].angle = (45 + femur_tibia_depan_kanan) #tibia6
        kit1.servo[4].angle = 125 + coxa_femur_tengah_kiri #femur2
        kit2.servo[14].angle = (55 - coxa_femur_belakang_kanan) #femur4
        kit2.servo[8].angle = (55 - coxa_femur_depan_kanan) #femur6

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



