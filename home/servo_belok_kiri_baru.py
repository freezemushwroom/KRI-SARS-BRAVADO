#Update: kakinya tegak lurus (dinaikin)

from time import sleep
from adafruit_servokit import ServoKit

waktu_sleep = 0.2

kit1 = ServoKit(channels = 16, address = 0x41)
kit2 = ServoKit(channels = 16, address = 0x40)

#femur 1 3 5 ngangkat
kit1.servo[7].angle = 180 #femur1
kit1.servo[1].angle = 180 #femur3
kit2.servo[11].angle = 0 #femur5
print("Femur 1 3 5 Ngangkat")
sleep(waktu_sleep)

try:
    while True:
        #coxa 1 3 mundur 5 maju
        kit1.servo[8].angle = 60 #coxa1
        kit1.servo[2].angle = 60 #coxa3
        kit2.servo[10].angle = 60 #coxa5
        print("Coxa 1 3 Mundur 5 Maju")
        sleep(waktu_sleep)
        

        #femur 1 3 5 turun dan tibia turun sekalian adjust ngambil kaki
        for i in range (0, 50, 5):
            kit1.servo[7].angle = 180 - (i+10) #femur1
            kit1.servo[6].angle = 180 - (i) #tibia1
            kit1.servo[1].angle = 180 - (i+10) #femur3
            kit1.servo[0].angle = 180 - (i) #tibia3
            kit2.servo[11].angle = 0 + (i+10) #femur5
            kit2.servo[12].angle = 0 + (i) #tibia5
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
        kit1.servo[4].angle = 180 #femur2
        kit2.servo[14].angle = 0 #femur4
        kit2.servo[8].angle = 0 #femur6
        print("Femur 2 4 6 Ngangkat")
        sleep(waktu_sleep)

        #coxa 2 mundur 4 6 maju
        kit1.servo[5].angle = 60 #coxa2
        kit2.servo[13].angle = 60 #coxa4
        kit2.servo[7].angle = 60 #coxa6
        print("Coxa 2 Mundur Coxa 4 6 Maju")
        sleep(waktu_sleep)

        #femur 2 4 6 turun dan tibia turun sekalian adjust ngambil kaki
        for i in range (0, 50, 5):
            kit1.servo[4].angle = 180 - (i+10) #femur2
            kit1.servo[3].angle = 180 - (i) #tibia2
            kit2.servo[14].angle = 0 + (i+10) #femur4
            kit2.servo[15].angle = 0 + (i) #tibia4
            kit2.servo[8].angle = 0 + (i+10) #femur6
            kit2.servo[9].angle = 0 + (i) #tibia6
        
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
        kit1.servo[7].angle = 180 #femur1
        kit1.servo[1].angle = 180 #femur3
        kit2.servo[11].angle = 0 #femur5
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




