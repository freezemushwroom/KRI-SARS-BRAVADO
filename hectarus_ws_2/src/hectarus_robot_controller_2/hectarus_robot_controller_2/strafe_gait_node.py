#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from std_msgs.msg import Int32MultiArray
from std_msgs.msg import Int32
import math
from adafruit_servokit import ServoKit
import time

kit1 = ServoKit(channels = 16, address = 0x41) #, reference_clock_speed = 24723456)
kit2 = ServoKit(channels = 16, address = 0x40) #, reference_clock_speed = 24985600)

for i in range (9):
    kit1.servo[i].set_pulse_width_range(320, 2320)
    kit2.servo[15-i].set_pulse_width_range(400, 2400)



def wait(waktu):
    flag = True
    myTime = time.time()
    while flag == True:
        currentTime = time.time()
        if currentTime - myTime < waktu:
            flag = True
        elif currentTime - myTime >= waktu:
            flag = False

delay = 0.35

class MyNode(Node):
    def __init__(self):
        super().__init__("strafe_gait_node")
        self.subscriber_angle = self.create_subscription(Int32MultiArray, "/strafe_angle_", self.strafe, 1)

    def strafe(self, message = Int32MultiArray):
        kit1.servo[8].angle = 90 - 30 #coxa1
        kit1.servo[5].angle = 90
        kit1.servo[2].angle = 90 + 30 #coxa3
        kit2.servo[13].angle = 90 - 30 #coxa4
        kit2.servo[10].angle = 90
        kit2.servo[7].angle = 90 + 30 #coxa6

        if message.data[15+9] == 3:
            if message.data[16+9] <= -3 or message.data[16+9] >= 3:
                #femur angkat, kalo ada error yaw, kaki kiri langsung angkat koreksi base-coxa
                kit1.servo[8].angle = 90 - 30 + max(0, min(30, message.data[16+9]*3))#coxa1
                kit1.servo[7].angle = 180 #femur1
                kit1.servo[6].angle = 170 # tibia1
                kit1.servo[2].angle = 90 + 30 + max(-30, min(0, message.data[16+9]*3)) #coxa3
                kit1.servo[1].angle = 180 #femur3
                kit1.servo[0].angle = 170 #tibia3
                kit2.servo[11].angle = max(0, min((180 - message.data[9+9] -  20 - (10*message.data[15+9] - 10)), 180)) #femur5
                #kit2.servo[12].angle = max(0, min((message.data[10+9] - 20 - (10*message.data[15+9] - 10)), 180)) #tibia5
                wait(delay)

                #femur 1 3 5 turun dan tibia turun sekalian adjust ngambil kaki
                kit1.servo[6].angle = max(0, min((180 - message.data[12+9]), 180)) #tibia1
                kit1.servo[0].angle = max(0, min((180 - message.data[14+9]), 180)) #tibia3
                kit2.servo[12].angle = 0 #max(0, min((message.data[10+9] + message.data[2+9] - 10), 180)) #tibia5
                wait(0.1*message.data[15+9])
                kit1.servo[7].angle = max(0, min((message.data[11+9]), 180)) #femur1
                kit1.servo[1].angle = max(0, min((message.data[13+9]), 180)) #femur3
                kit2.servo[11].angle = max(0, min((180 - message.data[9+9]- message.data[1+9]), 180)) #femur5

                wait(delay)

                # femur tibia 1 3 5 balik ke posisi awal
                kit1.servo[8].angle = 90 - 30 - max(-30, min(0, message.data[16+9]*2)) #coxa1
                kit1.servo[7].angle = message.data[11+9] #femur1
                kit1.servo[6].angle = 180 - message.data[12+9] #tibia1

                kit1.servo[2].angle = 90 + 30 - max(0, min(30, message.data[16+9]*2)) #coxa3
                kit1.servo[1].angle = message.data[13+9] #femur3
                kit1.servo[0].angle = 180 - message.data[14+9] #tibia3

                kit2.servo[11].angle = 180 - message.data[9+9] #femur5
                kit2.servo[12].angle = message.data[10+9] #tibia5

                wait(0.02)
            else:
                #femur angkat, kalo ada error yaw, kaki kiri langsung angkat koreksi base-coxa
                kit1.servo[7].angle = max(0, min((message.data[11+9] + 20 + (10*message.data[15+9] - 10)), 180)) #femur1
                kit1.servo[6].angle = max(0, min((180 - message.data[12+9] +  20 + (10*message.data[15+9] - 10)), 180)) #tibia1
                kit1.servo[1].angle = max(0, min((message.data[13+9] + 20 + (10*message.data[15+9] - 10)), 180)) #femur3
                kit1.servo[0].angle = max(0, min((180 - message.data[14+9] +  20 + (10*message.data[15+9] - 10)), 180)) #tibia3
                kit2.servo[11].angle = max(0, min((180 - message.data[9+9] -  20 - (10*message.data[15+9] - 10)), 180)) #femur5
                #kit2.servo[12].angle = max(0, min((message.data[10+9] - 20 - (10*message.data[15+9] - 10)), 180)) #tibia5
                wait(delay)

                #femur 1 3 5 turun dan tibia turun sekalian adjust ngambil kaki
                kit1.servo[6].angle = max(0, min((180 - message.data[12+9] - message.data[5]), 180)) #tibia1
                kit1.servo[0].angle = max(0, min((180 - message.data[14+9] - message.data[8]), 180)) #tibia3
                kit2.servo[12].angle = 0 #max(0, min((message.data[10+9] + message.data[2+9] - 10), 180)) #tibia5
                wait(0.1*message.data[15+9])
                kit1.servo[7].angle = max(0, min((message.data[11+9] + message.data[4]), 180)) #femur1
                kit1.servo[1].angle = max(0, min((message.data[13+9] + message.data[7]), 180)) #femur3
                kit2.servo[11].angle = max(0, min((180 - message.data[9+9]- message.data[1+9]), 180)) #femur5

                wait(delay)

                # femur tibia 1 3 5 balik ke posisi awal
                kit1.servo[7].angle = message.data[11+9] #femur1
                kit1.servo[6].angle = 180 - message.data[12+9] #tibia1

                kit1.servo[1].angle = message.data[13+9] #femur3
                kit1.servo[0].angle = 180 - message.data[14+9] #tibia3

                kit2.servo[11].angle = 180 - message.data[9+9] #femur5
                kit2.servo[12].angle = message.data[10+9] #tibia5

                wait(0.02)
            # femur 2 4 6 angkat
            kit1.servo[4].angle = max(0, min((message.data[9+9] + 20 + (10*message.data[15+9] - 10)), 180)) #femur2
            kit1.servo[3].angle = max(0, min((180 - message.data[10+9] + 20 + (10*message.data[15+9])), 180)) #tibia2
            kit2.servo[14].angle = max(0, min((180 - message.data[13+9] -  20 - (10*message.data[15+9] - 10)), 180)) #femur4
            #kit2.servo[15].angle = max(0, min((message.data[14+9] - 20 - (10*message.data[15+9] - 10)), 180)) #tibia4
            kit2.servo[8].angle = max(0, min((180 - message.data[11+9] -  20 - (10*message.data[15+9] - 10)), 180)) #femur6
            #kit2.servo[9].angle =  max(0, min((message.data[12+9] - 20 - (10*message.data[15+9] - 10)), 180)) #tibia6
            wait(delay)

            #femur 2 4 6 turun dan tibia turun sekalian adjust ngambil kaki
            kit1.servo[3].angle = max(0, min((180 - message.data[10+9] - message.data[2]), 180)) #tibia2
            kit2.servo[15].angle = max(0, min((message.data[14+9] + message.data[8+9] - 10), 180)) #tibia4
            kit2.servo[9].angle = max(0, min((message.data[12+9] + message.data[5+9] - 10), 180)) #tibia6
            wait(0.1*message.data[15+9])
            kit1.servo[4].angle = max(0, min((message.data[9+9] + message.data[1]), 180)) #femur2
            kit2.servo[14].angle = max(0, min((180 - message.data[13+9] - message.data[7+9]), 180)) #femur4
            kit2.servo[8].angle = max(0, min((180 - message.data[11+9] - message.data[4+9]), 180)) #femur6
            wait(delay)

            #femur tibia 2 4 6 balik ke poisi awal
            kit1.servo[4].angle = message.data[9+9] #femur2
            kit1.servo[3].angle = 180 -message.data[10+9] #tibia2

            kit2.servo[14].angle = 180 - message.data[13+9] #femur4
            kit2.servo[15].angle = message.data[14+9] #tibia4

            kit2.servo[8].angle = 180 - message.data[11+9] #femur6
            kit2.servo[9].angle = message.data[12+9] #tibia6
                
        else:
            if message.data[16+9] <= -5 or message.data[16+9] >= 5:
                #femur angkat, kalo ada error yaw, kaki kiri langsung angkat koreksi base-coxa
                kit1.servo[8].angle = 90 - 30 + max(0, min(30, 2*message.data[16+9]))#coxa1
                kit1.servo[7].angle = 180 #femur1
                kit1.servo[6].angle = 170 # tibia1
                kit1.servo[2].angle = 90 + 30 + max(-30, min(0, 2*message.data[16+9])) #coxa3
                kit1.servo[1].angle = 180 #femur3
                kit1.servo[0].angle = 170 #tibia3
                kit2.servo[11].angle = max(0, min((180 - message.data[9+9] -  20 - (10*message.data[15+9] - 10)), 180)) #femur5
                kit2.servo[12].angle = max(0, min((message.data[10+9] - 20 - (10*message.data[15+9] - 10)), 180)) #tibia5
                wait(delay)

                #femur 1 3 5 turun dan tibia turun sekalian adjust ngambil kaki
                kit1.servo[6].angle = max(0, min((180 - message.data[12+9]), 180)) #tibia1
                kit1.servo[0].angle = max(0, min((180 - message.data[14+9]), 180)) #tibia3
                kit2.servo[12].angle = max(0, min((message.data[10+9] + message.data[2+9] - 10), 180)) #tibia5
                wait(0.1*message.data[15+9])
                kit1.servo[7].angle = max(0, min((message.data[11+9]), 180)) #femur1
                kit1.servo[1].angle = max(0, min((message.data[13+9]), 180)) #femur3
                kit2.servo[11].angle = max(0, min((180 - message.data[9+9]- message.data[1+9]), 180)) #femur5

                wait(delay)

                # femur tibia 1 3 5 balik ke posisi awal
                kit1.servo[8].angle = 90 - 30 - max(-30, min(0, 2*message.data[16+9])) #coxa1
                kit1.servo[7].angle = message.data[11+9] #femur1
                kit1.servo[6].angle = 180 - message.data[12+9] #tibia1

                kit1.servo[2].angle = 90 + 30 - max(0, min(30, 2*message.data[16+9])) #coxa3
                kit1.servo[1].angle = message.data[13+9] #femur3
                kit1.servo[0].angle = 180 - message.data[14+9] #tibia3

                kit2.servo[11].angle = 180 - message.data[9+9] #femur5
                kit2.servo[12].angle = message.data[10+9] #tibia5

                wait(0.02)
            else:
                #femur angkat, kalo ada error yaw, kaki kiri langsung angkat koreksi base-coxa
                kit1.servo[7].angle = max(0, min((message.data[11+9] + 20 + (10*message.data[15+9] - 10)), 180)) #femur1
                kit1.servo[6].angle = max(0, min((180 - message.data[12+9] +  20 + (10*message.data[15+9] - 10)), 180)) #tibia1
                kit1.servo[1].angle = max(0, min((message.data[13+9] + 20 + (10*message.data[15+9] - 10)), 180)) #femur3
                kit1.servo[0].angle = max(0, min((180 - message.data[14+9] +  20 + (10*message.data[15+9] - 10)), 180)) #tibia3
                kit2.servo[11].angle = max(0, min((180 - message.data[9+9] -  20 - (10*message.data[15+9] - 10)), 180)) #femur5
                kit2.servo[12].angle = max(0, min((message.data[10+9] - 20 - (10*message.data[15+9] - 10)), 180)) #tibia5
                wait(delay)

                #femur 1 3 5 turun dan tibia turun sekalian adjust ngambil kaki
                kit1.servo[6].angle = max(0, min((180 - message.data[12+9] - message.data[5]), 180)) #tibia1
                kit1.servo[0].angle = max(0, min((180 - message.data[14+9] - message.data[8]), 180)) #tibia3
                kit2.servo[12].angle = max(0, min((message.data[10+9] + message.data[2+9]), 180)) #tibia5
                wait(0.1*message.data[15+9])
                kit1.servo[7].angle = max(0, min((message.data[11+9] + message.data[4]), 180)) #femur1
                kit1.servo[1].angle = max(0, min((message.data[13+9] + message.data[7]), 180)) #femur3
                kit2.servo[11].angle = max(0, min((180 - message.data[9+9]- message.data[1+9]), 180)) #femur5

                wait(delay)

                # femur tibia 1 3 5 balik ke posisi awal
                kit1.servo[7].angle = message.data[11+9] #femur1
                kit1.servo[6].angle = 180 - message.data[12+9] #tibia1

                kit1.servo[1].angle = message.data[13+9] #femur3
                kit1.servo[0].angle = 180 - message.data[14+9] #tibia3

                kit2.servo[11].angle = 180 - message.data[9+9] #femur5
                kit2.servo[12].angle = message.data[10+9] #tibia5

                wait(0.02)

            # femur 2 4 6 angkat
            kit1.servo[4].angle = max(0, min((message.data[9+9] + 20 + (10*message.data[15+9] - 10)), 180)) #femur2
            kit1.servo[3].angle = max(0, min((180 - message.data[10+9] + 20 + (10*message.data[15+9])), 180)) #tibia2
            kit2.servo[14].angle = max(0, min((180 - message.data[13+9] -  20 - (10*message.data[15+9] - 10)), 180)) #femur4
            kit2.servo[15].angle = max(0, min((message.data[14+9] - 20 - (10*message.data[15+9] - 10)), 180)) #tibia4
            kit2.servo[8].angle = max(0, min((180 - message.data[11+9] -  20 - (10*message.data[15+9] - 10)), 180)) #femur6
            kit2.servo[9].angle =  max(0, min((message.data[12+9] - 20 - (10*message.data[15+9] - 10)), 180)) #tibia6
            wait(delay)

            #femur 2 4 6 turun dan tibia turun sekalian adjust ngambil kaki
            kit1.servo[3].angle = max(0, min((180 - message.data[10+9] - message.data[2]), 180)) #tibia2
            kit2.servo[15].angle = max(0, min((message.data[14+9] + message.data[8+9]), 180)) #tibia4
            kit2.servo[9].angle = max(0, min((message.data[12+9] + message.data[5+9]), 180)) #tibia6
            wait(0.1*message.data[15+9])
            kit1.servo[4].angle = max(0, min((message.data[9+9] + message.data[1]), 180)) #femur2
            kit2.servo[14].angle = max(0, min((180 - message.data[13+9] - message.data[7+9]), 180)) #femur4
            kit2.servo[8].angle = max(0, min((180 - message.data[11+9] - message.data[4+9]), 180)) #femur6
            wait(delay)

            #femur tibia 2 4 6 balik ke poisi awal
            kit1.servo[4].angle = message.data[9+9] #femur2
            kit1.servo[3].angle = 180 -message.data[10+9] #tibia2

            kit2.servo[14].angle = 180 - message.data[13+9] #femur4
            kit2.servo[15].angle = message.data[14+9] #tibia4

            kit2.servo[8].angle = 180 - message.data[11+9] #femur6
            kit2.servo[9].angle = message.data[12+9] #tibia6
def main(args=None):
    rclpy.init(args=args)
    node = MyNode()
    rclpy.spin(node)
    rclpy.shutdown()
