from time import sleep
from adafruit_servokit import ServoKit


kit1 = ServoKit(channels = 16, address = 0x41)
kit2 = ServoKit(channels = 16, address = 0x40)

#coxa ke tengah
kit1.servo[8].angle = 90 #coxa1
kit2.servo[7].angle = 90 #coxa6
kit1.servo[5].angle = 90 #coxa2
kit2.servo[10].angle = 90 #coxa5
kit1.servo[2].angle = 90 #coxa3
kit2.servo[13].angle = 90 #coxa4
sleep(1)
#femur naik
kit1.servo[7].angle = 180 #femur1
kit2.servo[8].angle = 0 #femur6
kit1.servo[4].angle = 180 #femur2
kit2.servo[11].angle = 0 #femur5
kit1.servo[1].angle = 180 #femur3
kit2.servo[14].angle = 0 #femur4

kit1.servo[6].angle = 100 #tibia1
kit2.servo[9].angle = 80 #tibia6
kit1.servo[3].angle = 100 #tibia2
kit2.servo[12].angle = 80 #tibia5
kit1.servo[0].angle = 100 #tibia3
kit2.servo[15].angle = 80 #tibia4
sleep(3)
#tibia naik
kit1.servo[6].angle = 180
kit2.servo[9].angle = 0
kit1.servo[3].angle = 180
kit2.servo[12].angle = 0
kit1.servo[0].angle = 180
kit2.servo[15].angle = 0
sleep(0.5)
#femur turun berdiri + tibia adjust
for i in range (10, 50, 10):
    kit1.servo[6].angle = 180 - (i-10) #tibia1
    kit2.servo[9].angle = 0 + (i-10) #tibia6
    kit1.servo[3].angle = 180 - (i-5) #tibia2
    kit2.servo[12].angle = 0 + (i-5) #tibia5
    kit1.servo[0].angle = 180 - (i-10) #tibia3
    kit2.servo[15].angle = 0 + (i-5) #tibia4
    kit1.servo[7].angle = 180 - i #femur1
    kit2.servo[8].angle = 0 + i #femur6
    kit1.servo[4].angle = 180 - (i) #femur2
    kit2.servo[11].angle = 0 + (i+5) #femur5
    kit1.servo[1].angle = 180 - i #femur3
    kit2.servo[14].angle = 0 + i #femur4
