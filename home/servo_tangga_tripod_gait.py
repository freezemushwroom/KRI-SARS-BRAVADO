#update dari yang kelima :
# - Penambahan IK
# - coxa belakang belum melebar

# Hal yang perlu di cek:
# - ketinggian kaki belakang (tes pake file tes kestabilan)
# - Tinggi kaki tengah pasti ga nepak tanah (tes pake file tes kestabilan)
# - derajat majunya diliat
# - center of massnya diliat (tes pake file tes kestabilan)
import math
from time import sleep
from adafruit_servokit import ServoKit

panjang_robot = 25
set_panjang_robot= panjang_robot-13 #jarak dari depan
coxa = 2.55
femur = 6.508
tibia = 7.964

angkat = 30

l_depan = 6.2
l_belakang = 5
l_tengah = 6
waktu_sleep = 0.5

kit1 = ServoKit(channels = 16, address = 0x41)
kit2 = ServoKit(channels = 16, address = 0x40)
def IK_berdiri_tangga():
    maju = 0
    alpha1_depan = math.asin(l_depan/femur)
    h_depan = math.sqrt(math.pow(femur,2)+math.pow(tibia,2)-(2*femur*tibia*math.cos(alpha1_depan))-(math.sin(alpha1_depan)*math.sin(alpha1_depan)*femur*femur))
    PD = math.sqrt(math.pow(maju,2)+math.pow((l_depan+coxa),2)-(2*maju*(l_depan+coxa)*math.cos(math.radians(135))))
    sudut_base_coxa_depan = math.degrees(math.acos((math.pow((l_depan+coxa),2)+math.pow(PD,2)-math.pow(maju,2))/(2*(l_depan+coxa)*PD)))
    PD = PD-coxa
    MD = math.sqrt(math.pow(h_depan,2)+math.pow(PD,2)) #panjang garis miring antara femur tibia
    sudut_coxa_femur_1_depan = math.degrees(math.acos((math.pow(femur,2)+math.pow(MD,2)-math.pow(tibia,2))/(2*femur*MD)))
    sudut_coxa_femur_2_depan = math.degrees(math.acos((math.pow(MD,2)+math.pow(h_depan,2)-math.pow(PD,2))/(2*h_depan*MD)))
    sudut_coxa_femur_total_depan = sudut_coxa_femur_1_depan + sudut_coxa_femur_2_depan
    sudut_femur_tibia_depan = math.degrees(math.acos((math.pow(femur,2)+math.pow(tibia,2)-math.pow(MD,2))/(2*tibia*femur)))

    #kaki belakang naik, lnya dikecilin dikit & coxa dilebarin kebelakang buat jaga keseimbangan
    #-----------Belakang--------------#
    h_belakang_seharusnya = math.tan(math.radians(29.05))*panjang_robot
    alpha1_belakang = math.asin(l_belakang/femur)
    alpha1_belakang = math.radians(180) - alpha1_belakang
    h_belakang = math.sqrt(math.pow(femur,2)+math.pow(tibia,2)-(2*femur*tibia*math.cos(alpha1_belakang))-(math.sin(alpha1_belakang)*math.sin(alpha1_belakang)*femur*femur))

    PB = math.sqrt(math.pow(maju,2)+math.pow((l_belakang+coxa),2)-(2*maju*(l_belakang+coxa)*math.cos(math.radians(45))))
    sudut_base_coxa_belakang = math.degrees(math.acos((math.pow((l_belakang+coxa),2)+math.pow(PB,2)-math.pow(maju,2))/(2*(l_belakang+coxa)*PB)))
    PB = PB - coxa
    MB = math.sqrt(math.pow(h_belakang,2)+math.pow(PB,2)) #panjang garis miring antara femur tibia
    sudut_coxa_femur_1_belakang = math.degrees(math.acos((math.pow(femur,2)+math.pow(MB,2)-math.pow(tibia,2))/(2*femur*MB)))
    sudut_coxa_femur_2_belakang = math.degrees(math.acos((math.pow(MB,2)+math.pow(h_belakang,2)-math.pow(PB,2))/(2*h_belakang*MB)))
    sudut_coxa_femur_total_belakang = sudut_coxa_femur_1_belakang + sudut_coxa_femur_2_belakang
    sudut_femur_tibia_belakang = math.degrees(math.acos((math.pow(femur,2)+math.pow(tibia,2)-math.pow(MB,2))/(2*tibia*femur)))
    
    #kaki tengah, ketinggiannya berdasarkan yang belakang, seharusnya lebih
    #-----------------Tengah---------------------#
    h_tengah_seharusnya = (h_belakang*set_panjang_robot)/panjang_robot
    alpha1_tengah = math.asin(l_tengah/femur)
    alpha1_tengah = math.radians(180) - alpha1_tengah
    h_tengah = math.sqrt(math.pow(femur,2)+math.pow(tibia,2)-(2*femur*tibia*math.cos(alpha1_tengah))-(math.sin(alpha1_tengah)*math.sin(alpha1_tengah)*femur*femur))

    sudut_base_coxa_tengah = math.degrees(math.atan(maju/(l_tengah+coxa)))
    P = math.sqrt(math.pow(maju,2)+math.pow((l_tengah+coxa),2)) #panjang diagonal setelah kaki maju
    P = P-coxa
    M = math.sqrt(math.pow(h_tengah,2)+math.pow(P,2)) #panjang garis miring antara femur tibia
    sudut_coxa_femur_1_tengah = math.degrees(math.acos((math.pow(femur,2)+math.pow(M,2)-math.pow(tibia,2))/(2*femur*M)))
    sudut_coxa_femur_2_tengah = math.degrees(math.acos((math.pow(M,2)+math.pow(h_tengah,2)-math.pow(P,2))/(2*h_tengah*M)))
    sudut_coxa_femur_total = sudut_coxa_femur_1_tengah + sudut_coxa_femur_2_tengah
    sudut_femur_tibia_tengah = math.degrees(math.acos((math.pow(femur,2)+math.pow(tibia,2)-math.pow(M,2))/(2*tibia*femur)))
    return (sudut_base_coxa_tengah, sudut_coxa_femur_total, sudut_femur_tibia_tengah, sudut_base_coxa_depan, sudut_coxa_femur_total_depan, sudut_femur_tibia_depan, sudut_base_coxa_belakang, sudut_coxa_femur_total_belakang, sudut_femur_tibia_belakang)


def IK_maju_tangga(maju):
    alpha1_depan = math.asin(l_depan/femur)
    h_depan = math.sqrt(math.pow(femur,2)+math.pow(tibia,2)-(2*femur*tibia*math.cos(alpha1_depan))-(math.sin(alpha1_depan)*math.sin(alpha1_depan)*femur*femur))
    PD = math.sqrt(math.pow(maju,2)+math.pow((l_depan+coxa),2)-(2*maju*(l_depan+coxa)*math.cos(math.radians(135))))
    sudut_base_coxa_depan = math.degrees(math.acos((math.pow((l_depan+coxa),2)+math.pow(PD,2)-math.pow(maju,2))/(2*(l_depan+coxa)*PD)))
    PD = PD-coxa
    MD = math.sqrt(math.pow(h_depan,2)+math.pow(PD,2)) #panjang garis miring antara femur tibia
    sudut_coxa_femur_1_depan = math.degrees(math.acos((math.pow(femur,2)+math.pow(MD,2)-math.pow(tibia,2))/(2*femur*MD)))
    sudut_coxa_femur_2_depan = math.degrees(math.acos((math.pow(MD,2)+math.pow(h_depan,2)-math.pow(PD,2))/(2*h_depan*MD)))
    sudut_coxa_femur_total_depan = sudut_coxa_femur_1_depan + sudut_coxa_femur_2_depan
    sudut_femur_tibia_depan = math.degrees(math.acos((math.pow(femur,2)+math.pow(tibia,2)-math.pow(MD,2))/(2*tibia*femur)))

    #kaki belakang naik, lnya dikecilin dikit & coxa dilebarin kebelakang buat jaga keseimbangan
    #-----------Belakang--------------#
    h_belakang_seharusnya = math.tan(math.radians(29.05))*panjang_robot
    alpha1_belakang = math.asin(l_belakang/femur)
    alpha1_belakang = math.radians(180) - alpha1_belakang
    h_belakang = math.sqrt(math.pow(femur,2)+math.pow(tibia,2)-(2*femur*tibia*math.cos(alpha1_belakang))-(math.sin(alpha1_belakang)*math.sin(alpha1_belakang)*femur*femur))

    PB = math.sqrt(math.pow(maju,2)+math.pow((l_belakang+coxa),2)-(2*maju*(l_belakang+coxa)*math.cos(math.radians(45))))
    sudut_base_coxa_belakang = math.degrees(math.acos((math.pow((l_belakang+coxa),2)+math.pow(PB,2)-math.pow(maju,2))/(2*(l_belakang+coxa)*PB)))
    PB = PB - coxa
    MB = math.sqrt(math.pow(h_belakang,2)+math.pow(PB,2)) #panjang garis miring antara femur tibia
    sudut_coxa_femur_1_belakang = math.degrees(math.acos((math.pow(femur,2)+math.pow(MB,2)-math.pow(tibia,2))/(2*femur*MB)))
    sudut_coxa_femur_2_belakang = math.degrees(math.acos((math.pow(MB,2)+math.pow(h_belakang,2)-math.pow(PB,2))/(2*h_belakang*MB)))
    sudut_coxa_femur_total_belakang = sudut_coxa_femur_1_belakang + sudut_coxa_femur_2_belakang
    sudut_femur_tibia_belakang = math.degrees(math.acos((math.pow(femur,2)+math.pow(tibia,2)-math.pow(MB,2))/(2*tibia*femur)))

    #kaki tengah, ketinggiannya berdasarkan yang belakang, seharusnya lebih
    #-----------------Tengah---------------------#
    h_tengah_seharusnya = (h_belakang*set_panjang_robot)/panjang_robot
    alpha1_tengah = math.asin(l_tengah/femur)
    alpha1_tengah = math.radians(180) - alpha1_tengah
    h_tengah = math.sqrt(math.pow(femur,2)+math.pow(tibia,2)-(2*femur*tibia*math.cos(alpha1_tengah))-(math.sin(alpha1_tengah)*math.sin(alpha1_tengah)*femur*femur))

    sudut_base_coxa_tengah = math.degrees(math.atan(maju/(l_tengah+coxa)))
    P = math.sqrt(math.pow(maju,2)+math.pow((l_tengah+coxa),2)) #panjang diagonal setelah kaki maju
    P = P-coxa
    M = math.sqrt(math.pow(h_tengah,2)+math.pow(P,2)) #panjang garis miring antara femur tibia
    sudut_coxa_femur_1_tengah = math.degrees(math.acos((math.pow(femur,2)+math.pow(M,2)-math.pow(tibia,2))/(2*femur*M)))
    sudut_coxa_femur_2_tengah = math.degrees(math.acos((math.pow(M,2)+math.pow(h_tengah,2)-math.pow(P,2))/(2*h_tengah*M)))
    sudut_coxa_femur_total = sudut_coxa_femur_1_tengah + sudut_coxa_femur_2_tengah
    sudut_femur_tibia_tengah = math.degrees(math.acos((math.pow(femur,2)+math.pow(tibia,2)-math.pow(M,2))/(2*tibia*femur)))

    return (sudut_base_coxa_tengah, sudut_coxa_femur_total, sudut_femur_tibia_tengah, sudut_base_coxa_depan, sudut_coxa_femur_total_depan, sudut_femur_tibia_depan, sudut_base_coxa_belakang, sudut_coxa_femur_total_belakang, sudut_femur_tibia_belakang)


base_coxa_tengah1, coxa_femur_tengah1, femur_tibia_tengah1, base_coxa_depan1, coxa_femur_depan1, femur_tibia_depan1, base_coxa_belakang1, coxa_femur_belakang1, femur_tibia_belakang1 = IK_berdiri_tangga()


base_coxa_tengah, coxa_femur_tengah, femur_tibia_tengah, base_coxa_depan, coxa_femur_depan, femur_tibia_depan, base_coxa_belakang, coxa_femur_belakang, femur_tibia_belakang = IK_maju_tangga(3.5)

base_coxa_tengah = base_coxa_tengah - base_coxa_tengah1
coxa_femur_tengah = coxa_femur_tengah - coxa_femur_tengah1
femur_tibia_tengah = femur_tibia_tengah - femur_tibia_tengah1
base_coxa_depan = base_coxa_depan - base_coxa_depan1
coxa_femur_depan = coxa_femur_depan - coxa_femur_depan1
femur_tibia_depan = femur_tibia_depan - femur_tibia_depan1
base_coxa_belakang = base_coxa_belakang - base_coxa_belakang1
coxa_femur_belakang = coxa_femur_belakang - coxa_femur_belakang1
femur_tibia_belakang = femur_tibia_belakang - femur_tibia_belakang1


#perhtungan derajat angkat
if ((180-femur_tibia_depan1) + 45 + angkat) > 180:
    derajat_tibia1 = 180
else:
    derajat_tibia1 = ((180-femur_tibia_depan1) + 45 + angkat)
if ((180-femur_tibia_tengah1) + 45 + angkat) > 180:
    derajat_tibia2 = 180
else:
    derajat_tibia2 = ((180-femur_tibia_tengah1) + 45 + angkat)
if ((180-femur_tibia_belakang1) + 45 + angkat) > 180:
    derajat_tibia3 = 180
else:
    derajat_tibia3 = ((180-femur_tibia_belakang1) + 45 + angkat)
if (femur_tibia_belakang1 - 45 - angkat) < 0:
    derajat_tibia4 = 0
else:
    derajat_tibia4 = (femur_tibia_belakang1 - 45 - angkat)
if (femur_tibia_tengah1 - 45 - angkat) < 0:
    derajat_tibia5 = 0
else:
    derajat_tibia5 = (femur_tibia_tengah1 - 45 - angkat)
if (femur_tibia_depan1 - 45 - angkat) < 0:
    derajat_tibia6 = 0
else:
    derajat_tibia6 = (femur_tibia_depan1 - 45 - angkat)

#stance berdiri tangga
kit1.servo[8].angle = 90 #coxa1
kit1.servo[7].angle = coxa_femur_depan1 + 35 #femur1
kit1.servo[6].angle = (180-femur_tibia_depan1) + 45 #tibia1

kit2.servo[7].angle = 90 #coxa6
kit2.servo[8].angle = (180-coxa_femur_depan1) - 35 #femur6
kit2.servo[9].angle = (femur_tibia_depan1) - 45 #tibia6

kit1.servo[5].angle = 90 #coxa2
kit1.servo[4].angle = coxa_femur_tengah1 + 35 #femur2
kit1.servo[3].angle = (180-femur_tibia_tengah1) + 45 #tibia2

kit2.servo[10].angle = 90 #coxa5
kit2.servo[11].angle = (180-coxa_femur_tengah1) - 35 #femur5
kit2.servo[12].angle = (femur_tibia_tengah1) - 45 #tibia5

kit1.servo[2].angle = 90 #coxa3
kit1.servo[1].angle = coxa_femur_belakang1 + 35 #femur3
kit1.servo[0].angle = (180-femur_tibia_belakang1) + 45 #tibia3

kit2.servo[13].angle = 90 #coxa4
kit2.servo[14].angle = (180-coxa_femur_belakang1) - 35 #femur4
kit2.servo[15].angle =  (femur_tibia_belakang1) - 45 #tibia4

sleep(3)

#femur 1 3 5 ngangkat
kit1.servo[7].angle = coxa_femur_depan1 + 35 + angkat #femur1
kit1.servo[6].angle = derajat_tibia1 #tibia1
kit1.servo[1].angle = coxa_femur_belakang1 + 35 + angkat #femur3
kit1.servo[0].angle = derajat_tibia3 #tibia3
kit2.servo[11].angle = (180-coxa_femur_tengah1) - 35 - angkat #femur5
kit2.servo[12].angle = derajat_tibia5 #tibia5

#print("Femur 1 3 5 Ngangkat")
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
        kit1.servo[7].angle = coxa_femur_depan1 + 35  + coxa_femur_depan#femur1
        kit1.servo[6].angle = (180-femur_tibia_depan1) + 45 - femur_tibia_depan #tibia1
        kit1.servo[1].angle = coxa_femur_belakang1 + 35 + coxa_femur_belakang #femur3
        kit1.servo[0].angle = (180-femur_tibia_belakang1) + 45 - femur_tibia_belakang #tibia3
        kit2.servo[11].angle = (180-coxa_femur_tengah1) - 35 - coxa_femur_tengah #femur5
        kit2.servo[12].angle = (femur_tibia_tengah1) - 45 + femur_tibia_tengah #tibia5
        print("Femur Tibia 1 3 5 Turun")
        sleep(waktu_sleep)
        #coxa femur tibia 1 3 5 balik ke posisi awal
        kit1.servo[8].angle = 90 #coxa1
        kit1.servo[7].angle = coxa_femur_depan1 + 35 #femur1
        kit1.servo[6].angle = (180-femur_tibia_depan1) + 45 #tibia1

        kit1.servo[2].angle = 90 #coxa3
        kit1.servo[1].angle = coxa_femur_belakang1 + 35 #femur3
        kit1.servo[0].angle = (180-femur_tibia_belakang1) + 45 #tibia3

        kit2.servo[10].angle = 90 #coxa5
        kit2.servo[11].angle = (180-coxa_femur_tengah1) - 35 #femur5
        kit2.servo[12].angle = (femur_tibia_tengah1) - 45 #tibia5
        print("Coxa Femur Tibia 1 3 5 Balik")
        #sleep(0.05)
        #femur 2 4 6 ngangkat
        kit1.servo[4].angle = coxa_femur_tengah1 + 35 + angkat #femur2
        kit1.servo[3].angle = derajat_tibia2 #tibia2
        kit2.servo[14].angle = (180-coxa_femur_belakang1) - 35 - angkat #femur4
        kit2.servo[15].angle =  derajat_tibia4 #tibia4
        kit2.servo[8].angle = (180-coxa_femur_depan1) - 35 - angkat #femur6
        kit2.servo[9].angle = derajat_tibia6 #tibia6
        print("Femur 2 4 6 Ngangkat")
        sleep(waktu_sleep)

        #coxa 2 4 6 maju
        kit1.servo[5].angle = 90 + base_coxa_tengah #coxa2
        kit2.servo[13].angle = 90 - base_coxa_belakang #coxa4
        kit2.servo[7].angle = 90 - base_coxa_depan #coxa6
        print("Coxa 2 4 6 Maju")
        sleep(waktu_sleep)

        #femur 2 4 6 turun dan tibia turun sekalian adjust ngambil kaki
        kit1.servo[4].angle = coxa_femur_tengah1 + 35 + coxa_femur_tengah #femur2
        kit1.servo[3].angle = (180-femur_tibia_tengah1) + 45 - femur_tibia_tengah #tibia2
        kit2.servo[14].angle = (180-coxa_femur_belakang1) - 35 - coxa_femur_belakang #femur4
        kit2.servo[15].angle =  (femur_tibia_belakang1) - 45 + femur_tibia_belakang #tibia4
        kit2.servo[8].angle = (180-coxa_femur_depan1) - 35 - coxa_femur_depan #femur6
        kit2.servo[9].angle = (femur_tibia_depan1) - 45 + femur_tibia_depan #tibia6
        
        print("Femur Tibia 2 4 6 Turun")
        sleep(waktu_sleep)
        #coxa femur tibia 2 4 6 balik ke poisi awal
        kit1.servo[5].angle = 90 #coxa2
        kit1.servo[4].angle = coxa_femur_tengah1 + 35 #femur2
        kit1.servo[3].angle = (180-femur_tibia_tengah1) + 45 #tibia2


        kit2.servo[13].angle = 90 #coxa4
        kit2.servo[14].angle = (180-coxa_femur_belakang1) - 35 #femur4
        kit2.servo[15].angle =  (femur_tibia_belakang1) - 45 #tibia4


        kit2.servo[7].angle = 90 #coxa6
        kit2.servo[8].angle = (180-coxa_femur_depan1) - 35 #femur6
        kit2.servo[9].angle = (femur_tibia_depan1) - 45 #tibia6
        print("Coxa Femur Tibia 2 4 6 Balik")
        #sleep(0.05)
        #femur 1 3 5 ngangkat
        kit1.servo[7].angle = coxa_femur_depan1 + 35 + angkat #femur1
        kit1.servo[6].angle = derajat_tibia1 #tibia1
        kit1.servo[1].angle = coxa_femur_belakang1 + 35 + angkat #femur3
        kit1.servo[0].angle = derajat_tibia3 #tibia3
        kit2.servo[11].angle = (180-coxa_femur_tengah1) - 35 - angkat #femur5
        kit2.servo[12].angle = derajat_tibia5 #tibia5
        print("Femur 1 3 5 Ngangkat")
        sleep(waktu_sleep)

except KeyboardInterrupt:
    kit1.servo[8].angle = 90 #coxa1
    kit1.servo[7].angle = coxa_femur_depan1 + 35 #femur1
    kit1.servo[6].angle = (180-femur_tibia_depan1) + 45 #tibia1

    kit2.servo[7].angle = 90 #coxa6
    kit2.servo[8].angle = (180-coxa_femur_depan1) - 35 #femur6
    kit2.servo[9].angle = (femur_tibia_depan1) - 45 #tibia6

    kit1.servo[5].angle = 90 #coxa2
    kit1.servo[4].angle = coxa_femur_tengah1 + 35 #femur2
    kit1.servo[3].angle = (180-femur_tibia_tengah1) + 45 #tibia2

    kit2.servo[10].angle = 90 #coxa5
    kit2.servo[11].angle = (180-coxa_femur_tengah1) - 35 #femur5
    kit2.servo[12].angle = (femur_tibia_tengah1) - 45 #tibia5

    kit1.servo[2].angle = 90 #coxa3
    kit1.servo[1].angle = coxa_femur_belakang1 + 35 #femur3
    kit1.servo[0].angle = (180-femur_tibia_belakang1) + 45 #tibia3

    kit2.servo[13].angle = 90 #coxa4
    kit2.servo[14].angle = (180-coxa_femur_belakang1) - 35 #femur4
    kit2.servo[15].angle =  (femur_tibia_belakang1) - 45 #tibia4



