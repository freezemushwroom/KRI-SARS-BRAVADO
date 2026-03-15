#gait kaki seribu
import math
from time import sleep
from adafruit_servokit import ServoKit

kit1 = ServoKit(channels = 16, address = 0x41)
kit2 = ServoKit(channels = 16, address = 0x40)


coxa = 2.55
femur = 6.508
tibia = 7.964
l = 6.508

waktu_sleep = 0.2
waktu = 0.5
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

    sudut_base_coxa_belakang = math.degrees(math.asin(maju/(l+coxa)))
    PB = math.sqrt(math.pow((l+coxa),2)-math.pow(maju,2)) #panjang diagonal setelah kaki maju
    PB = PB - coxa
    MB = math.sqrt(math.pow(h,2)+math.pow(PB,2)) #panjang garis miring antara femur tibia
    sudut_coxa_femur_1_belakang = math.degrees(math.acos((math.pow(femur,2)+math.pow(MB,2)-math.pow(tibia,2))/(2*femur*M)))
    sudut_coxa_femur_2_belakang = math.degrees(math.acos((math.pow(MB,2)+math.pow(h,2)-math.pow(PB,2))/(2*h*MB)))
    sudut_coxa_femur_total_belakang = sudut_coxa_femur_1_belakang + sudut_coxa_femur_2_belakang
    sudut_femur_tibia_belakang = math.degrees(math.acos((math.pow(femur,2)+math.pow(tibia,2)-math.pow(MB,2))/(2*tibia*femur)))
    return (sudut_base_coxa_tengah, sudut_coxa_femur_total, sudut_femur_tibia_tengah, sudut_base_coxa_depan, sudut_coxa_femur_total_depan, sudut_femur_tibia_depan, sudut_base_coxa_belakang, sudut_coxa_femur_total_belakang, sudut_femur_tibia_belakang)

sudut_base_coxa_tengah_berdiri, sudut_coxa_femur_total_berdiri, sudut_femur_tibia_tengah_berdiri, sudut_base_coxa_depan_berdiri, sudut_coxa_femur_total_depan_berdiri, sudut_femur_tibia_depan_berdiri, sudut_base_coxa_belakang_berdiri, sudut_coxa_femur_total_belakang_berdiri, sudut_femur_tibia_belakang_berdiri = IK_berdiri()


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

    sudut_base_coxa_belakang = math.degrees(math.asin(maju/(l+coxa)))
    PB = math.sqrt(math.pow((l+coxa),2)-math.pow(maju,2)) #panjang diagonal setelah kaki maju
    PB = PB - coxa
    MB = math.sqrt(math.pow(h,2)+math.pow(PB,2)) #panjang garis miring antara femur tibia
    sudut_coxa_femur_1_belakang = math.degrees(math.acos((math.pow(femur,2)+math.pow(MB,2)-math.pow(tibia,2))/(2*femur*M)))
    sudut_coxa_femur_2_belakang = math.degrees(math.acos((math.pow(MB,2)+math.pow(h,2)-math.pow(PB,2))/(2*h*MB)))
    sudut_coxa_femur_total_belakang = sudut_coxa_femur_1_belakang + sudut_coxa_femur_2_belakang
    sudut_femur_tibia_belakang = math.degrees(math.acos((math.pow(femur,2)+math.pow(tibia,2)-math.pow(MB,2))/(2*tibia*femur)))
    base_coxa_tengah, coxa_femur_tengah, femur_tibia_tengah, base_coxa_depan, coxa_femur_depan, femur_tibia_depan, base_coxa_belakang, coxa_femur_belakang, femur_tibia_belakang = IK_berdiri()

    return (sudut_base_coxa_tengah-base_coxa_tengah, sudut_coxa_femur_total-coxa_femur_tengah, sudut_femur_tibia_tengah - femur_tibia_tengah, sudut_base_coxa_depan - base_coxa_depan, sudut_coxa_femur_total_depan - coxa_femur_depan, sudut_femur_tibia_depan - femur_tibia_depan, sudut_base_coxa_belakang - base_coxa_belakang, sudut_coxa_femur_total_belakang - coxa_femur_belakang, sudut_femur_tibia_belakang - femur_tibia_belakang)


sudut = [[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0]]
step = 4
decrement = step/5
# i = 0 itu yang paling depan
for i in range(5):
    base_coxa_tengah, coxa_femur_tengah, femur_tibia_tengah, base_coxa_depan, coxa_femur_depan, femur_tibia_depan, base_coxa_belakang, coxa_femur_belakang, femur_tibia_belakang = IK_maju(step)
    sudut[i] = [base_coxa_tengah, coxa_femur_tengah, femur_tibia_tengah, base_coxa_depan, coxa_femur_depan, femur_tibia_depan, base_coxa_belakang, coxa_femur_belakang, femur_tibia_belakang]
    step = step - decrement

idx = [0,0,0,0,0,0]

def decrement(index):
    for i in range (6):
        if i != index:
            idx[i] = idx[i] + 1

#semua coxa pindah ke posisi paling depan + femur diangkat dulu
kit1.servo[7].angle = 170 #femur1
sleep(waktu)
kit1.servo[8].angle =  90 + sudut[0][3] #coxa1
kit1.servo[7].angle = 125 + sudut[0][4] #femur1
kit1.servo[6].angle = 135 - sudut[0][5] #tibia1
sleep(waktu)
kit2.servo[8].angle = 30 #femur6
sleep(waktu)
kit2.servo[7].angle =  90 - sudut[0][3] #coxa6
kit2.servo[8].angle = 55 - sudut[0][4] #femur6
kit2.servo[9].angle = 45 + sudut[0][5] #tibia6
sleep(waktu)
kit1.servo[4].angle = 170 #femur2
sleep(waktu)
kit1.servo[5].angle = 90 + sudut[0][0] #coxa2
kit1.servo[4].angle = 125 + sudut[0][1] #femur2
kit1.servo[3].angle = 135 - sudut[0][2] #tibia2
sleep(waktu)
kit2.servo[11].angle = 20 #femur5
sleep(waktu)
kit2.servo[10].angle = 90 - sudut[0][0] #coxa5
kit2.servo[11].angle = 55 - sudut[0][1] #femur5
kit2.servo[12].angle = 45 + sudut[0][2] #tibia5
sleep(waktu)
kit1.servo[1].angle = 170 #femur3
sleep(waktu)
kit1.servo[2].angle = 90 + sudut[0][6] #coxa3
kit1.servo[1].angle = 125 + sudut[0][7] #femur3
kit1.servo[0].angle = 135 - sudut[0][8] #tibia3
sleep(waktu)
kit2.servo[14].angle = 20 #femur4
sleep(waktu)
kit2.servo[13].angle = 90 - sudut[0][6] #coxa4
kit2.servo[14].angle = 55 - sudut[0][7] #femur4
kit2.servo[15].angle = 45 + sudut[0][8] #tibia4
print("Kaki Semua Maju")
sleep(waktu_sleep)

#femur 1 angkat
kit1.servo[7].angle = 170 #femur1
kit1.servo[6].angle = 180 #tibia1
print("Femur 1 Ngangkat")
sleep(waktu_sleep)

try:
    while True:
        #coxa 1 maju sisanya mundur
        idx[0] = 0
        decrement(0)
        kit1.servo[8].angle =  90 + sudut[idx[0]][3] #coxa1
        
        kit2.servo[7].angle =  90 - sudut[idx[5]][3] #coxa6
        kit2.servo[8].angle = 55 - sudut[idx[5]][4] #femur6
        kit2.servo[9].angle = 45 + sudut[idx[5]][5] #tibia6

        kit1.servo[5].angle = 90 + sudut[idx[1]][0] #coxa2
        kit1.servo[4].angle = 125 + sudut[idx[1]][1] #femur2
        kit1.servo[3].angle = 135 - sudut[idx[1]][2] #tibia2

        kit2.servo[10].angle = 90 - sudut[idx[4]][0] #coxa5
        kit2.servo[11].angle = 55 - sudut[idx[4]][1] #femur5
        kit2.servo[12].angle = 45 + sudut[idx[4]][2] #tibia5

        kit1.servo[2].angle = 90 + sudut[idx[2]][6] #coxa3
        kit1.servo[1].angle = 125 + sudut[idx[2]][7] #femur3
        kit1.servo[0].angle = 135 - sudut[idx[2]][8] #tibia3

        kit2.servo[13].angle = 90 - sudut[idx[3]][6] #coxa4
        kit2.servo[14].angle = 55 - sudut[idx[3]][7] #femur4
        kit2.servo[15].angle = 45 + sudut[idx[3]][8] #tibia4
        print("Coxa 1 Maju dari posisi berdiri, sisanya mundur")
#        sleep(waktu_sleep)


        #femur 1 turun dan tibia turun sekalian adjust ngambil kaki
        kit1.servo[6].angle = 135 - sudut[idx[0]][5] #tibia1
        sleep(0.1)
        kit1.servo[7].angle = 125 + sudut[idx[0]][4] #femur1
        print("Femur Tibia 1 Turun")
        sleep(waktu_sleep)

        #femur 2 angkat
        kit1.servo[4].angle = 170 #femur2
        kit1.servo[3].angle = 180 #tibia2
        print("Femur Tibia 2 Angkat")
        sleep(waktu_sleep)

        #coxa 2 maju sisanya mundur
        idx[1] = 0
        decrement(1)
        kit1.servo[8].angle =  90 + sudut[idx[0]][3] #coxa1
        kit1.servo[7].angle = 125 + sudut[idx[0]][4] #femur1
        kit1.servo[6].angle = 135 - sudut[idx[0]][5] #tibia1
        
        kit2.servo[7].angle =  90 - sudut[idx[5]][3] #coxa6
        kit2.servo[8].angle = 55 - sudut[idx[5]][4] #femur6
        kit2.servo[9].angle = 45 + sudut[idx[5]][5] #tibia6

        kit1.servo[5].angle = 90 + sudut[idx[1]][0] #coxa2

        kit2.servo[10].angle = 90 - sudut[idx[4]][0] #coxa5
        kit2.servo[11].angle = 55 - sudut[idx[4]][1] #femur5
        kit2.servo[12].angle = 45 + sudut[idx[4]][2] #tibia5

        kit1.servo[2].angle = 90 + sudut[idx[2]][6] #coxa3
        kit1.servo[1].angle = 125 + sudut[idx[2]][7] #femur3
        kit1.servo[0].angle = 135 - sudut[idx[2]][8] #tibia3

        kit2.servo[13].angle = 90 - sudut[idx[3]][6] #coxa4
        kit2.servo[14].angle = 55 - sudut[idx[3]][7] #femur4
        kit2.servo[15].angle = 45 + sudut[idx[3]][8] #tibia4
        print("Coxa 2 Maju dari posisi berdiri, sisanya mundur")
#        sleep(waktu_sleep)

	    #femur tibia 2 turun
        kit1.servo[3].angle = 135 - sudut[idx[1]][2] #tibia2
        sleep(0.1)
        kit1.servo[4].angle = 125 + sudut[idx[1]][1] #femur2
        print("Femur 2 Turun")
        sleep(waktu_sleep)

        #femur tibia 3 naik
        kit1.servo[1].angle = 170 #femur3
        kit1.servo[0].angle = 180 #tibia3
        sleep(waktu_sleep)

 	    #coxa 3 maju sisanya mundur 5 derajat
        idx[2] = 0
        decrement(2)
        kit1.servo[8].angle =  90 + sudut[idx[0]][3] #coxa1
        kit1.servo[7].angle = 125 + sudut[idx[0]][4] #femur1
        kit1.servo[6].angle = 135 - sudut[idx[0]][5] #tibia1
        
        kit2.servo[7].angle =  90 - sudut[idx[5]][3] #coxa6
        kit2.servo[8].angle = 55 - sudut[idx[5]][4] #femur6
        kit2.servo[9].angle = 45 + sudut[idx[5]][5] #tibia6

        kit1.servo[5].angle = 90 + sudut[idx[1]][0] #coxa2
        kit1.servo[4].angle = 125 + sudut[idx[1]][1] #femur2
        kit1.servo[3].angle = 135 - sudut[idx[1]][2] #tibia2

        kit2.servo[10].angle = 90 - sudut[idx[4]][0] #coxa5
        kit2.servo[11].angle = 55 - sudut[idx[4]][1] #femur5
        kit2.servo[12].angle = 45 + sudut[idx[4]][2] #tibia5

        kit1.servo[2].angle = 90 + sudut[idx[2]][6] #coxa3

        kit2.servo[13].angle = 90 - sudut[idx[3]][6] #coxa4
        kit2.servo[14].angle = 55 - sudut[idx[3]][7] #femur4
        kit2.servo[15].angle = 45 + sudut[idx[3]][8] #tibia4
        print("Coxa 3 Maju dari posisi berdiri, sisanya mundur")
#        sleep(waktu_sleep)

	#femur tibia 3 turun
        kit1.servo[0].angle = 135 - sudut[idx[2]][8] #tibia3
        sleep(0.1)
        kit1.servo[1].angle = 125 + sudut[idx[2]][7] #femur3
        print("Femur Tibia 3 Turun")
        sleep(waktu_sleep)

	#femur 4 angkat
        kit2.servo[14].angle = 10 #femur4
        kit2.servo[15].angle = 0 #tibia4
        print("Femur 4 Ngangkat")
        sleep(waktu_sleep)

	#coxa 4 maju sisanya mundur 5 derajat
        idx[3] = 0
        decrement(3)
        kit1.servo[8].angle =  90 + sudut[idx[0]][3] #coxa1
        kit1.servo[7].angle = 125 + sudut[idx[0]][4] #femur1
        kit1.servo[6].angle = 135 - sudut[idx[0]][5] #tibia1
        
        kit2.servo[7].angle =  90 - sudut[idx[5]][3] #coxa6
        kit2.servo[8].angle = 55 - sudut[idx[5]][4] #femur6
        kit2.servo[9].angle = 45 + sudut[idx[5]][5] #tibia6

        kit1.servo[5].angle = 90 + sudut[idx[1]][0] #coxa2
        kit1.servo[4].angle = 125 + sudut[idx[1]][1] #femur2
        kit1.servo[3].angle = 135 - sudut[idx[1]][2] #tibia2

        kit2.servo[10].angle = 90 - sudut[idx[4]][0] #coxa5
        kit2.servo[11].angle = 55 - sudut[idx[4]][1] #femur5
        kit2.servo[12].angle = 45 + sudut[idx[4]][2] #tibia5

        kit1.servo[2].angle = 90 + sudut[idx[2]][6] #coxa3
        kit1.servo[1].angle = 125 + sudut[idx[2]][7] #femur3
        kit1.servo[0].angle = 135 - sudut[idx[2]][8] #tibia3

        kit2.servo[13].angle = 90 - sudut[idx[3]][6] #coxa4

        print("Coxa 4 Maju dari posisi berdiri, sisanya mundur")
#        sleep(waktu_sleep)
	    
	#femur tibia 4 turun
        kit2.servo[15].angle = 45 + sudut[idx[3]][8] #tibia4
        sleep(0.1)
        kit2.servo[14].angle = 55 - sudut[idx[3]][7] #femur4
        print("Femur Tibia 4 Turun")
        sleep(waktu_sleep)

	#femur 5 angkat
        kit2.servo[11].angle = 10 #femur5
        kit2.servo[12].angle = 0 #tibia5
        print("Femur 5 Ngangkat")
        sleep(waktu_sleep)

	#coxa 5 maju sisanya mundur 5 derajat
        idx[4] = 0
        decrement(4)
        kit1.servo[8].angle =  90 + sudut[idx[0]][3] #coxa1
        kit1.servo[7].angle = 125 + sudut[idx[0]][4] #femur1
        kit1.servo[6].angle = 135 - sudut[idx[0]][5] #tibia1
        
        kit2.servo[7].angle =  90 - sudut[idx[5]][3] #coxa6
        kit2.servo[8].angle = 55 - sudut[idx[5]][4] #femur6
        kit2.servo[9].angle = 45 + sudut[idx[5]][5] #tibia6

        kit1.servo[5].angle = 90 + sudut[idx[1]][0] #coxa2
        kit1.servo[4].angle = 125 + sudut[idx[1]][1] #femur2
        kit1.servo[3].angle = 135 - sudut[idx[1]][2] #tibia2

        kit2.servo[10].angle = 90 - sudut[idx[4]][0] #coxa5

        kit1.servo[2].angle = 90 + sudut[idx[2]][6] #coxa3
        kit1.servo[1].angle = 140 + sudut[idx[2]][7] #femur3
        kit1.servo[0].angle = 150 - sudut[idx[2]][8] #tibia3

        kit2.servo[13].angle = 90 - sudut[idx[3]][6] #coxa4
        kit2.servo[14].angle = 55 - sudut[idx[3]][7] #femur4
        kit2.servo[15].angle = 45 + sudut[idx[3]][8] #tibia4
        print("Coxa 5 Maju dari posisi berdiri, sisanya mundur")
#        sleep(waktu_sleep)
	    
	#femur tibia 5 turun
        kit2.servo[12].angle = 45 + sudut[idx[4]][2] #tibia5
        sleep(0.1)
        kit2.servo[11].angle = 55 - sudut[idx[4]][1] #femur5
        print("Femur Tibia 5 Turun")
        sleep(waktu_sleep)

	#femur 6 angkat
        kit2.servo[8].angle = 10 #femur6
        kit2.servo[9].angle = 0 #tibia6
        print("Femur 6 Ngangkat")
        sleep(waktu_sleep)

	#coxa 6 maju sisanya mundur 5 derajat
        idx[5] = 0
        decrement(5)
        kit1.servo[8].angle =  90 + sudut[idx[0]][3] #coxa1
        kit1.servo[7].angle = 125 + sudut[idx[0]][4] #femur1
        kit1.servo[6].angle = 135 - sudut[idx[0]][5] #tibia1
        
        kit2.servo[7].angle =  90 - sudut[idx[5]][3] #coxa6

        kit1.servo[5].angle = 90 + sudut[idx[1]][0] #coxa2
        kit1.servo[4].angle = 125 + sudut[idx[1]][1] #femur2
        kit1.servo[3].angle = 135 - sudut[idx[1]][2] #tibia2

        kit2.servo[10].angle = 90 - sudut[idx[4]][0] #coxa5
        kit2.servo[11].angle = 55 - sudut[idx[4]][1] #femur5
        kit2.servo[12].angle = 45 + sudut[idx[4]][2] #tibia5

        kit1.servo[2].angle = 90 + sudut[idx[2]][6] #coxa3
        kit1.servo[1].angle = 125 + sudut[idx[2]][7] #femur3
        kit1.servo[0].angle = 135 - sudut[idx[2]][8] #tibia3

        kit2.servo[13].angle = 90 - sudut[idx[3]][6] #coxa4
        kit2.servo[14].angle = 55 - sudut[idx[3]][7] #femur4
        kit2.servo[15].angle = 45 + sudut[idx[3]][8] #tibia4
        print("Coxa 6 Maju 30 Derajat dari posisi berdiri, sisanya mundur 5 Derajat")
#        sleep(waktu_sleep)
	    
	#femur tibia 6 turun
        kit2.servo[9].angle = 45 + sudut[idx[5]][5] #tibia6
        sleep(0.1)
        kit2.servo[8].angle = 55 - sudut[idx[5]][4] #femur6
        print("Femur Tibia 6 Turun")
        sleep(waktu_sleep)
	    
	#femur 1 angkat
        kit1.servo[7].angle = 170 #femur1
        kit1.servo[6].angle = 180 #tibia1
        print("Femur 1 Ngangkat")
        sleep(waktu_sleep)

except KeyboardInterrupt:
	kit1.servo[8].angle = 90 #coxa1
	kit1.servo[7].angle = 125 #femur1
	kit1.servo[6].angle = 135 #tibia1

	kit2.servo[7].angle = 90 #coxa6
	kit2.servo[8].angle = 55  #femur6
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



