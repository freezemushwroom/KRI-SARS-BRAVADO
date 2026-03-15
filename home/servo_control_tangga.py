import time
from adafruit_servokit import ServoKit

import math

kit1 = ServoKit(channels = 16, address = 0x41)
kit2 = ServoKit(channels = 16, address = 0x40)

coxa = 2.644
femur = 6.436
tibia = 8.122
l = 6.436

forward = 3.8
yaw_yaw = 0
roll = -13
panjang_depan_belakang = 22
panjang_depan_tengah = 13

lebar_depan_belakang = 24.5
lebar_tengah = 33.5

if yaw_yaw> 5:
    yaw = 5
elif yaw_yaw < -5:
    yaw = -5
else:
    yaw = yaw_yaw

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

def wait(waktu):
    flag = True
    myTime = time.time()
    while flag == True:
        currentTime = time.time()
        if currentTime - myTime < waktu:
            flag = True
        elif currentTime - myTime >= waktu:
            flag = False

delay = 2
hold = 1
def nilai_h(panjang, derajat, maju, derajat_naik_maju):
    #alpha1 = math.asin(l/femur)
    #if derajat != 0:
    #    alpha1 = math.radians(180) - alpha1
    #h = math.sqrt(math.pow(femur,2)+math.pow(tibia,2)-(2*femur*tibia*math.cos(alpha1))-(math.sin(alpha1)*math.sin(alpha1)*femur*femur)) 
    h = tibia + (math.tan(math.radians(derajat))*panjang) #- (math.tan(math.radians(derajat_naik_maju)*maju))
    alpha1 = math.acos(((femur*tibia)-(math.sqrt((math.pow(femur,2)*math.pow(tibia,2))+(math.pow(femur,2)*(math.pow(h,2)-math.pow(tibia,2))))))/math.pow(femur,2))
    l = math.sin(alpha1)*femur
    return h, l


def IK_tengah(maju, yaw, panjang, roll, derajat_naik_maju):
    h,l = nilai_h(panjang, abs(roll), maju, derajat_naik_maju)
    P = math.sqrt(math.pow(maju,2)+math.pow((l+coxa),2)-(2*maju*(l+coxa)*math.cos(math.radians(90-(yaw))))) #panjang diagonal setelah kaki maju
    sudut_base_coxa_tengah = math.degrees(math.acos((math.pow((l+coxa),2)+math.pow(P,2)-math.pow(maju,2))/(2*(l+coxa)*P)))
    P = P-coxa
    M = math.sqrt(math.pow(h,2)+math.pow(P,2)) #panjang garis miring antara femur tibia

    sudut_coxa_femur_1_tengah = math.degrees(math.acos((math.pow(femur,2)+math.pow(M,2)-math.pow(tibia,2))/(2*femur*M)))
    sudut_coxa_femur_2_tengah = math.degrees(math.acos((math.pow(M,2)+math.pow(h,2)-math.pow(P,2))/(2*h*M)))
    sudut_coxa_femur_total = sudut_coxa_femur_1_tengah + sudut_coxa_femur_2_tengah
    sudut_femur_tibia_tengah = math.degrees(math.acos((math.pow(femur,2)+math.pow(tibia,2)-math.pow(M,2))/(2*tibia*femur)))
    return (sudut_base_coxa_tengah, sudut_coxa_femur_total, sudut_femur_tibia_tengah)

def IK_depan(maju,yaw, panjang, roll, derajat_naik_maju):
    h,l = nilai_h(panjang, max(roll, 0), maju, derajat_naik_maju)
    PD = math.sqrt(math.pow(maju,2)+math.pow((l+coxa),2)-(2*maju*(l+coxa)*math.cos(math.radians(135-(yaw)))))
    sudut_base_coxa_depan = math.degrees(math.acos((math.pow((l+coxa),2)+math.pow(PD,2)-math.pow(maju,2))/(2*(l+coxa)*PD)))
    PD = PD-coxa
    MD = math.sqrt(math.pow(h,2)+math.pow(PD,2)) #panjang garis miring antara femur tibia
    sudut_coxa_femur_1_depan = math.degrees(math.acos((math.pow(femur,2)+math.pow(MD,2)-math.pow(tibia,2))/(2*femur*MD)))
    sudut_coxa_femur_2_depan = math.degrees(math.acos((math.pow(MD,2)+math.pow(h,2)-math.pow(PD,2))/(2*h*MD)))
    sudut_coxa_femur_total_depan = sudut_coxa_femur_1_depan + sudut_coxa_femur_2_depan
    sudut_femur_tibia_depan = math.degrees(math.acos((math.pow(femur,2)+math.pow(tibia,2)-math.pow(MD,2))/(2*tibia*femur)))
    return(sudut_base_coxa_depan, sudut_coxa_femur_total_depan, sudut_femur_tibia_depan)

def IK_belakang(maju,yaw, panjang, roll, derajat_naik_maju):
    h,l = nilai_h(panjang, -min(roll, 0), maju, derajat_naik_maju)
    PB = math.sqrt(math.pow(maju,2)+math.pow((l+coxa),2)-(2*maju*(l+coxa)*math.cos(math.radians(80-45-(yaw)))))
    sudut_base_coxa_belakang = math.degrees(math.acos((math.pow((l+coxa),2)+math.pow(PB,2)-math.pow(maju,2))/(2*(l+coxa)*PB)))
    PB = PB - coxa
    MB = math.sqrt(math.pow(h,2)+math.pow(PB,2)) #panjang garis miring antara femur tibia
    sudut_coxa_femur_1_belakang = math.degrees(math.acos((math.pow(femur,2)+math.pow(MB,2)-math.pow(tibia,2))/(2*femur*MB)))
    sudut_coxa_femur_2_belakang = math.degrees(math.acos((math.pow(MB,2)+math.pow(h,2)-math.pow(PB,2))/(2*h*MB)))
    sudut_coxa_femur_total_belakang = sudut_coxa_femur_1_belakang + sudut_coxa_femur_2_belakang
    sudut_femur_tibia_belakang = math.degrees(math.acos((math.pow(femur,2)+math.pow(tibia,2)-math.pow(MB,2))/(2*tibia*femur)))
    return(sudut_base_coxa_belakang, sudut_coxa_femur_total_belakang, sudut_femur_tibia_belakang)


base_coxa_tengah_berdiri, coxa_femur_tengah_berdiri, femur_tibia_tengah_berdiri = IK_tengah(0,0,panjang_depan_tengah,roll, 0)
base_coxa_depan_berdiri, coxa_femur_depan_berdiri, femur_tibia_depan_berdiri = IK_depan(0,0, panjang_depan_belakang, roll, 0)
base_coxa_belakang_berdiri, coxa_femur_belakang_berdiri, femur_tibia_belakang_berdiri = IK_belakang(0,0, panjang_depan_belakang, roll, 0)


base_coxa_tengah_kiri, coxa_femur_tengah_kiri, femur_tibia_tengah_kiri = IK_tengah(forward_kiri_tengah,(yaw), panjang_depan_tengah, roll, roll)
base_coxa_tengah_kiri = base_coxa_tengah_kiri - base_coxa_tengah_berdiri
coxa_femur_tengah_kiri = coxa_femur_tengah_kiri - coxa_femur_tengah_berdiri
femur_tibia_tengah_kiri = femur_tibia_tengah_kiri - femur_tibia_tengah_berdiri

base_coxa_depan_kiri, coxa_femur_depan_kiri, femur_tibia_depan_kiri = IK_depan(forward_kiri_depan_belakang,(yaw), panjang_depan_belakang, roll, roll)
base_coxa_depan_kiri = base_coxa_depan_kiri - base_coxa_depan_berdiri
coxa_femur_depan_kiri = coxa_femur_depan_kiri - coxa_femur_depan_berdiri
femur_tibia_depan_kiri = femur_tibia_depan_kiri - femur_tibia_depan_berdiri

base_coxa_belakang_kiri, coxa_femur_belakang_kiri, femur_tibia_belakang_kiri = IK_belakang(forward_kiri_depan_belakang,(yaw), panjang_depan_belakang, roll, roll)
base_coxa_belakang_kiri = base_coxa_belakang_kiri - base_coxa_belakang_berdiri
coxa_femur_belakang_kiri = coxa_femur_belakang_kiri - coxa_femur_belakang_berdiri
femur_tibia_belakang_kiri = femur_tibia_belakang_kiri - femur_tibia_belakang_berdiri

base_coxa_tengah_kanan, coxa_femur_tengah_kanan, femur_tibia_tengah_kanan = IK_tengah(forward_kanan_tengah,((-yaw)), panjang_depan_tengah, roll, roll)
base_coxa_tengah_kanan = base_coxa_tengah_kanan - base_coxa_tengah_berdiri
coxa_femur_tengah_kanan = coxa_femur_tengah_kanan - coxa_femur_tengah_berdiri
femur_tibia_tengah_kanan = femur_tibia_tengah_kanan - femur_tibia_tengah_berdiri

base_coxa_depan_kanan, coxa_femur_depan_kanan, femur_tibia_depan_kanan = IK_depan(forward_kanan_depan_belakang,((-yaw)), panjang_depan_belakang, roll, roll)
base_coxa_depan_kanan = base_coxa_depan_kanan - base_coxa_depan_berdiri
coxa_femur_depan_kanan = coxa_femur_depan_kanan - coxa_femur_depan_berdiri
femur_tibia_depan_kanan = femur_tibia_depan_kanan - femur_tibia_depan_berdiri

base_coxa_belakang_kanan, coxa_femur_belakang_kanan, femur_tibia_belakang_kanan = IK_belakang(forward_kanan_depan_belakang,((-yaw)), panjang_depan_belakang, roll, roll)
base_coxa_belakang_kanan = base_coxa_belakang_kanan - base_coxa_belakang_berdiri
coxa_femur_belakang_kanan = coxa_femur_belakang_kanan - coxa_femur_belakang_berdiri
femur_tibia_belakang_kanan = femur_tibia_belakang_kanan - femur_tibia_belakang_berdiri

data = [int(base_coxa_tengah_kiri), int(coxa_femur_tengah_kiri), int(femur_tibia_tengah_kiri), int(base_coxa_depan_kiri), int(coxa_femur_depan_kiri),int(femur_tibia_depan_kiri), int(base_coxa_belakang_kiri), int(coxa_femur_belakang_kiri), int(femur_tibia_belakang_kiri), int(base_coxa_tengah_kanan), int(coxa_femur_tengah_kanan), int(femur_tibia_tengah_kanan), int(base_coxa_depan_kanan), int(coxa_femur_depan_kanan), int(femur_tibia_depan_kanan), int(base_coxa_belakang_kanan), int(coxa_femur_belakang_kanan), int(femur_tibia_belakang_kanan), int(coxa_femur_tengah_berdiri+35), int(femur_tibia_tengah_berdiri-45), int(coxa_femur_depan_berdiri+35), int(femur_tibia_depan_berdiri-45), int(coxa_femur_belakang_berdiri+35), int(femur_tibia_belakang_berdiri-45)]

print("Base - Coxa Tengah Kiri: " + str(base_coxa_tengah_kiri))
print("Coxa - Femur Tengah Kiri: " + str(coxa_femur_tengah_kiri))
print("Femur - Tibia Tengah Kiri: " + str(femur_tibia_tengah_kiri))

print("Base - Coxa Depan Kiri: " + str(base_coxa_depan_kiri))
print("Coxa - Femur Depan Kiri: " + str(coxa_femur_depan_kiri))
print("Femur - Tibia Depan Kiri: " + str(femur_tibia_depan_kiri))

print("Base - Coxa Belakang Kiri: " + str(base_coxa_belakang_kiri))
print("Coxa - Femur Belakang Kiri: " + str(coxa_femur_belakang_kiri))
print("Femur - Tibia Belakang Kiri: " + str(femur_tibia_belakang_kiri))

print("")

print("Base - Coxa Tengah Kanan: " + str(base_coxa_tengah_kanan))
print("Coxa - Femur Tengah Kanan: " + str(coxa_femur_tengah_kanan))
print("Femur - Tibia Tengah Kanan: " + str(femur_tibia_tengah_kanan))

print("Base - Coxa Depan Kanan: " + str(base_coxa_depan_kanan))
print("Coxa - Femur Depan Kanan: " + str(coxa_femur_depan_kanan))
print("Femur - Tibia Depan Kanan: " + str(femur_tibia_depan_kanan))

print("Base - Coxa Belakang Kanan: " + str(base_coxa_belakang_kanan))
print("Coxa - Femur Belakang Kanan: " + str(coxa_femur_belakang_kanan))
print("Femur - Tibia Belakang Kanan: " + str(femur_tibia_belakang_kanan))

#femur 1 3 5 ngangkat
#kit1.servo[7].angle = max(0, min((data[11+9] + 45), 180)) #femur1
#kit1.servo[6].angle = max(0, min((180 - data[12+9] + 45),180)) #tibia1
kit1.servo[1].angle = max(0, min((data[13+9] + 45),180)) #femur3
kit1.servo[0].angle = max(0, min((180 - data[14+9] + 45), 180)) #tibia3
#kit2.servo[11].angle = max(0, min((180 - data[9+9] - 45), 180)) #femur5
#kit2.servo[12].angle = max(0, min((data[10+9] - 45), 180)) #tibia5
wait(delay)

#coxa 1 3 5 maju
#kit1.servo[8].angle = max(0, min((90 + data[3]), 180)) #coxa1
kit1.servo[2].angle = max(0, min((80 + data[6]), 180)) #coxa3
#kit2.servo[10].angle = max(0, min((90 - data[0+9]), 180)) #coxa5
wait(delay)


#femur 1 3 5 turun dan tibia turun sekalian adjust ngambil kaki
#kit1.servo[6].angle = max(0, min(((180 - data[12+9]) - data[5]), 180)) #tibia1
kit1.servo[0].angle = max(0, min(((180 - data[14+9]) - data[8]), 180)) #tibia3
#kit2.servo[12].angle = max(0, min((data[10+9] + data[2+9]), 180)) #tibia5
wait(0.1)
#kit1.servo[7].angle = max(0, min((data[11+9] + data[4]), 180)) #femur1
kit1.servo[1].angle = max(0, min((data[13+9] + data[7]), 180)) #femur3
#kit2.servo[11].angle = max(0, min(((180 - data[9+9])- data[1+9]), 180)) #femur5
wait(delay)

#coxa femur tibia 1 3 5 balik ke posisi awal
#kit1.servo[8].angle = 90 #coxa1
#kit1.servo[7].angle = data[11+9] #femur1
#kit1.servo[6].angle = 180 - data[12+9] #tibia1

kit1.servo[2].angle = 80 #coxa3
kit1.servo[1].angle = data[13+9] #femur3
kit1.servo[0].angle = 180 - data[14+9] #tibia3

#kit2.servo[10].angle = 90 #coxa5
#kit2.servo[11].angle = 180 - data[9+9] #femur5
#kit2.servo[12].angle = data[10+9] #tibia5

wait(0.02)
#femur 2 4 6 ngangkat
#kit1.servo[4].angle = max(0, min((data[9+9] + 45), 180)) #femur2
#kit1.servo[3].angle = max(0, min((180 - data[10+9] + 45), 180)) #tibia2

kit2.servo[14].angle = max(0, min((180 - data[13+9] - 45), 180)) #femur4
kit2.servo[15].angle = max(0, min((data[14+9] - 45), 180)) #tibia4

#kit2.servo[8].angle = max(0, min((180 - data[11+9] - 45), 180)) #femur6
#kit2.servo[9].angle =  max(0, min((data[12+9] - 45), 180)) #tibia6
wait(delay)

#coxa 2 4 6 maju
#kit1.servo[5].angle = max(0, min((90 + data[0]), 180)) #coxa2
kit2.servo[13].angle = max(0, min((100 - data[6+9]), 180)) #coxa4
#kit2.servo[7].angle = max(0, min((90 - data[3+9]), 180)) #coxa6
wait(delay)

#femur 2 4 6 turun dan tibia turun sekalian adjust ngambil kaki
#kit1.servo[3].angle = max(0, min(((180 - data[10+9]) - data[2]), 180)) #tibia2
kit2.servo[15].angle = max(0, min((data[14+9] + data[8+9]), 180)) #tibia4
#kit2.servo[9].angle = max(0, min((data[12+9] + data[5+9]), 180)) #tibia6

#kit1.servo[4].angle = max(0, min((data[9+9] + data[1]), 180)) #femur2
kit2.servo[14].angle = max(0, min(((180 - data[13+9]) - data[7+9]), 180)) #femur4
#kit2.servo[8].angle = max(0, min(((180 - data[11+9]) - data[4+9]), 180)) #femur6
wait(delay)

#coxa femur tibia 2 4 6 balik ke poisi awal
#kit1.servo[5].angle = 90 #coxa2
#kit1.servo[4].angle = data[9+9] #femur2
#kit1.servo[3].angle = 180 -data[10+9] #tibia2

kit2.servo[13].angle = 100 #coxa4
kit2.servo[14].angle = 180 - data[13+9] #femur4
kit2.servo[15].angle = data[14+9] #tibia4

#kit2.servo[7].angle = 90 #coxa6
#kit2.servo[8].angle = 180 - data[11+9] #femur6
#kit2.servo[9].angle = data[12+9] #tibia6
wait(0.02)
