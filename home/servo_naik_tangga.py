from time import sleep
from adafruit_servokit import ServoKit

waktu_sleep = 0.5

kit1 = ServoKit(channels = 16, address = 0x41)
kit2 = ServoKit(channels = 16, address = 0x40)

kit1.servo[2].angle = 70 #coxa3
kit1.servo[4].angle = 120 #femur2
kit1.servo[1].angle = 80 #femur3
kit2.servo[14].angle = 100 #femur4
kit2.servo[11].angle = 65 #femur5

kit2.servo[13].angle = 110 #coxa4
kit1.servo[3].angle = 125 #tibia2
kit1.servo[0].angle = 90 #tibia3
kit2.servo[15].angle = 95 #tibia4
kit2.servo[12].angle = 55 #tibia5

sleep(5)
#femur 1 3 5 ngangkat
kit1.servo[7].angle = 180 #femur1
kit1.servo[1].angle = 120 #femur3
kit2.servo[11].angle = 0 #femur5
print("Femur 1 3 5 Ngangkat")
sleep(waktu_sleep)

try:
    while True:
        #coxa 1 3 5 maju
        kit1.servo[8].angle = 120 #coxa1
        kit1.servo[2].angle = 100 #coxa3
        kit2.servo[10].angle = 60 #coxa5
        print("Coxa 1 3 5 Maju")
        sleep(waktu_sleep)
        

        #femur 1 3 5 turun dan tibia turun sekalian adjust ngambil kaki
        for i in range (10, 50, 10):
            kit1.servo[7].angle = 180 - i #femur1
            kit1.servo[6].angle = 180 - (i-10) #tibia1
            kit1.servo[1].angle = 120 - i #femur3
            kit1.servo[0].angle = 120 - (i-10) #tibia3
            kit2.servo[11].angle = 20 + (i+5) #femur5
            kit2.servo[12].angle = 20 + (i-5) #tibia5
        print("Femur Tibia 1 3 5 Turun")
        sleep(waktu_sleep)
        #coxa femur tibia 1 3 5 balik ke posisi awal
        kit1.servo[8].angle = 90 #coxa1
        kit1.servo[7].angle = 140 #femur1
        kit1.servo[6].angle = 150 #tibia1

        kit1.servo[2].angle = 70 #coxa3
        kit1.servo[1].angle = 80 #femur3
        kit1.servo[0].angle = 90 #tibia3

        kit2.servo[10].angle = 90 #coxa5
        kit2.servo[11].angle = 65 #femur5
        kit2.servo[12].angle = 55 #tibia5
        print("Coxa Femur Tibia 1 3 5 Balik")
        #sleep(0.05)
        #femur 2 4 6 ngangkat
        kit1.servo[4].angle = 180 #femur2
        kit2.servo[14].angle = 60 #femur4
        kit2.servo[8].angle = 0 #femur6
        print("Femur 2 4 6 Ngangkat")
        sleep(waktu_sleep)

        #coxa 2 4 6 maju
        kit1.servo[5].angle = 120 #coxa2
        kit2.servo[13].angle = 80 #coxa4
        kit2.servo[7].angle = 60 #coxa6
        print("Coxa 2 4 6 Maju")
        sleep(waktu_sleep)

        #femur 2 4 6 turun dan tibia turun sekalian adjust ngambil kaki
        for i in range (10, 50, 10):
            kit1.servo[4].angle = 160 - (i) #femur2
            kit1.servo[3].angle = 160 - (i-5) #tibia2
            kit2.servo[14].angle = 60 + i #femur4
            kit2.servo[15].angle = 60 + (i-5) #tibia4
            kit2.servo[8].angle = 0 + i #femur6
            kit2.servo[9].angle = 0 + (i-10) #tibia6
        
        print("Femur Tibia 2 4 6 Turun")
        sleep(waktu_sleep)
        #coxa femur tibia 2 4 6 balik ke poisi awal
        kit1.servo[5].angle = 90 #coxa2
        kit1.servo[4].angle = 120 #femur2
        kit1.servo[3].angle = 125 #tibia2


        kit2.servo[13].angle = 110 #coxa4
        kit2.servo[14].angle = 100 #femur4
        kit2.servo[15].angle = 95 #tibia4


        kit2.servo[7].angle = 90 #coxa6
        kit2.servo[8].angle = 40 #femur6
        kit2.servo[9].angle = 30 #tibia6
        print("Coxa Femur Tibia 2 4 6 Balik")
        #sleep(0.05)
        #femur 1 3 5 ngangkat
        kit1.servo[7].angle = 180 #femur1
        kit1.servo[1].angle = 120 #femur3
        kit2.servo[11].angle = 0 #femur5
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
	kit1.servo[4].angle = 140 #femur2
	kit1.servo[3].angle = 145 #tibia2

	kit2.servo[10].angle = 90 #coxa5
	kit2.servo[11].angle = 45 #femur5
	kit2.servo[12].angle = 35 #tibia5

	kit1.servo[2].angle = 90 #coxa3
	kit1.servo[1].angle = 140 #femur3
	kit1.servo[0].angle = 150 #tibia3

	kit2.servo[13].angle = 90 #coxa4
	kit2.servo[14].angle = 40 #femur4
	kit2.servo[15].angle = 35 #tibia4




