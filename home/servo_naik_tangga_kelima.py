#update dari yang keempat :
# - Kaki depan diturunin supaya lebih datar, ga ada IK karena terlalu kompleks
# - Ada gait tambahan dikit sebelum kaki ditinggiin, biar ga nyeret
# - Ambil langkah maju lebih dikit (objektif: pengambilannya tepat ditengah anak tangga)
# - Angkat kakinya lebih rendah supaya pas turun ga ngebanting (Biar I2C ga putus2), objektif: diangkat setinggi anak tangganya

# Hal yang perlu di cek:
# - ketinggian kaki belakang (tes pake file tes kestabilan)
# - Tinggi kaki tengah pasti ga nepak tanah (tes pake file tes kestabilan)
# - derajat majunya diliat
# - center of massnya diliat (tes pake file tes kestabilan)
from time import sleep
from adafruit_servokit import ServoKit

waktu_sleep = 0.5

kit1 = ServoKit(channels = 16, address = 0x41)
kit2 = ServoKit(channels = 16, address = 0x40)

#femur angkat buat coxa belakang ngelebar 
kit1.servo[1].angle = 160 #femur3
sleep(0.1)
kit1.servo[2].angle = 100 #coxa3
kit1.servo[1].angle = 140 #femur3
sleep(1)
kit2.servo[14].angle = 20 #femur4
sleep(0.1)
kit2.servo[13].angle = 80 #coxa4
kit2.servo[14].angle = 40 #femur4
sleep(1)
#femur blakang naik
for i in range(0, 66, 1):
    kit1.servo[1].angle = 140 - i #femur3
    kit2.servo[14].angle = 40 + i #femur4

    kit1.servo[0].angle = 150 - i #tibia3
    kit2.servo[15].angle = 30 + i #tibia4

sleep(3)
#femur 1 3 5 ngangkat
for i in range (0, 31, 1):
    kit1.servo[7].angle = 140 + i #femur1
    kit1.servo[6].angle = 150 + (i) #tibia1
    kit1.servo[1].angle = 75 + i #femur3
    kit1.servo[0].angle = 85 + (i) #tibia3
    kit2.servo[11].angle = 65 - (i) #femur5
    kit2.servo[12].angle = 55 - (i) #tibia5

#print("Femur 1 3 5 Ngangkat")
sleep(waktu_sleep)

try:
    while True:
        #coxa 1 3 5 maju
        for i in range (0, 26, 1):
            kit1.servo[8].angle = 90 + i #coxa1
            kit1.servo[2].angle = 100 + i #coxa3
            kit2.servo[10].angle = 90 - i #coxa5
        print("Coxa 1 3 5 Maju")
        sleep(waktu_sleep)
        

        #femur 1 3 5 turun dan tibia turun sekalian adjust ngambil kaki
        for i in range (0, 31, 1):
            kit1.servo[7].angle = 170 - i #femur1
            kit1.servo[6].angle = 180 - (i) #tibia1
            kit1.servo[1].angle = 105 - i #femur3
            kit1.servo[0].angle = 115 - (i) #tibia3
            kit2.servo[11].angle = 35 + (i) #femur5
            kit2.servo[12].angle = 25 + (i) #tibia5
        print("Femur Tibia 1 3 5 Turun")
        sleep(waktu_sleep)
        #coxa femur tibia 1 3 5 balik ke posisi awal
        kit1.servo[8].angle = 90 #coxa1
        kit1.servo[7].angle = 140 #femur1
        kit1.servo[6].angle = 150 #tibia1

        kit1.servo[2].angle = 100 #coxa3
        kit1.servo[1].angle = 75 #femur3
        kit1.servo[0].angle = 85 #tibia3

        kit2.servo[10].angle = 90 #coxa5
        kit2.servo[11].angle = 65 #femur5
        kit2.servo[12].angle = 55 #tibia5
        print("Coxa Femur Tibia 1 3 5 Balik")
        #sleep(0.05)
        #femur 2 4 6 ngangkat
        for i in range(0, 31,1):
            kit1.servo[4].angle = 115 + (i) #femur2
            kit1.servo[3].angle = 125 + (i) #tibia2
            kit2.servo[14].angle = 105 - i #femur4
            kit2.servo[15].angle = 95 - (i) #tibia4
            kit2.servo[8].angle = 40 - i #femur6
            kit2.servo[9].angle = 30 - (i) #tibia6
        print("Femur 2 4 6 Ngangkat")
        sleep(waktu_sleep)

        #coxa 2 4 6 maju
        for i in range (0, 26, 1):
            kit1.servo[5].angle = 90 + i #coxa2
            kit2.servo[13].angle = 80 - i #coxa4
            kit2.servo[7].angle = 90 - i #coxa6
        print("Coxa 2 4 6 Maju")
        sleep(waktu_sleep)

        #femur 2 4 6 turun dan tibia turun sekalian adjust ngambil kaki
        for i in range (0, 31, 1):
            kit1.servo[4].angle = 145 - (i) #femur2
            kit1.servo[3].angle = 155 - (i) #tibia2
            kit2.servo[14].angle = 75 + i #femur4
            kit2.servo[15].angle = 65 + (i) #tibia4
            kit2.servo[8].angle = 10 + i #femur6
            kit2.servo[9].angle = 0 + (i) #tibia6
        
        print("Femur Tibia 2 4 6 Turun")
        sleep(waktu_sleep)
        #coxa femur tibia 2 4 6 balik ke poisi awal
        kit1.servo[5].angle = 90 #coxa2
        kit1.servo[4].angle = 115 #femur2
        kit1.servo[3].angle = 125 #tibia2


        kit2.servo[13].angle = 80 #coxa4
        kit2.servo[14].angle = 105 #femur4
        kit2.servo[15].angle = 95 #tibia4


        kit2.servo[7].angle = 90 #coxa6
        kit2.servo[8].angle = 30 #femur6
        kit2.servo[9].angle = 20 #tibia6
        print("Coxa Femur Tibia 2 4 6 Balik")
        #sleep(0.05)
        #femur 1 3 5 ngangkat
        for i in range (0, 31, 1):
            kit1.servo[7].angle = 140 + i #femur1
            kit1.servo[6].angle = 150 + (i) #tibia1
            kit1.servo[1].angle = 75 + i #femur3
            kit1.servo[0].angle = 85 + (i) #tibia3
            kit2.servo[11].angle = 65 - (i) #femur5
            kit2.servo[12].angle = 55 - (i) #tibia5
        print("Femur 1 3 5 Ngangkat")
        sleep(waktu_sleep)

except KeyboardInterrupt:
	kit1.servo[8].angle = 90 #coxa1
	kit1.servo[7].angle = 140 #femur1
	kit1.servo[6].angle = 150 #tibia1

	kit2.servo[7].angle = 90 #coxa6
	kit2.servo[8].angle = 40  #femur6
	kit2.servo[9].angle = 30 #tibia6

	kit1.servo[5].angle = 90 #coxa2
	kit1.servo[4].angle = 115 #femur2
	kit1.servo[3].angle = 125 #tibia2

	kit2.servo[10].angle = 90 #coxa5
	kit2.servo[11].angle = 65 #femur5
	kit2.servo[12].angle = 55 #tibia5

	kit1.servo[2].angle = 100 #coxa3
	kit1.servo[1].angle = 75 #femur3
	kit1.servo[0].angle = 85 #tibia3

	kit2.servo[13].angle = 80 #coxa4
	kit2.servo[14].angle = 105 #femur4
	kit2.servo[15].angle = 95 #tibia4



