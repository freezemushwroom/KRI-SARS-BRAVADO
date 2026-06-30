#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from std_msgs.msg import Int32MultiArray
from std_msgs.msg import Int32
import math
from adafruit_servokit import ServoKit
import time
import numpy as np

kit1 = ServoKit(channels = 16, address = 0x41) #, reference_clock_speed = 24723456)
kit2 = ServoKit(channels = 16, address = 0x40) #, reference_clock_speed = 24985600)

for i in range (9):
    kit1.servo[i].set_pulse_width_range(320, 2320)
    kit2.servo[15-i].set_pulse_width_range(400, 2400)


#delay = 0.2

def wait(waktu):
    flag = True
    myTime = time.time()
    while flag == True:
        currentTime = time.time()
        if currentTime - myTime < waktu:
            flag = True
        elif currentTime - myTime >= waktu:
            flag = False


class MyNode(Node):
    def __init__(self):
        super().__init__("wave_gait_node")
        self.subscriber_angle = self.create_subscription(Int32MultiArray, "/wave_angle_", self.move, 1)

    def move(self, message = Int32MultiArray):
        rows = message.layout.dim[0].size
        cols = message.layout.dim[1].size
        data = np.array(message.data).reshape(rows, cols)
        self.get_logger().info(f'Received 2D array:\n{data}')

        delay = (0.4*(data[6][17]))-0.2
        #femur 1 angkat
        kit1.servo[7].angle = max(0, min((data[6][4] + 45), 180)) #femur1
        kit1.servo[6].angle =  max(0, min((180 - data[6][5] + 45), 180)) #tibia1
        wait(delay)

        #coxa 1 maju sisanya mundur
        kit1.servo[8].angle = max(0, min((90 + data[0][3]), 180)) #coxa1
        kit2.servo[7].angle = max(0, min((90 - data[1][3+9]), 180)) #coxa6
        kit2.servo[8].angle = max(0, min((180 - data[6][4] - data[1][4+9]), 180)) #femur6
        kit2.servo[9].angle = max(0, min((data[6][5] + data[1][5+9]), 180)) #tibia6
        
        kit1.servo[5].angle = max(0, min((90 + data[5][0]), 180)) #coxa2
        kit1.servo[4].angle = max(0, min((data[6][1] + data[5][1]), 180)) #femur2
        kit1.servo[3].angle = max(0, min((180 - data[6][2] - data[5][2]), 180)) #tibia2

        kit2.servo[10].angle = max(0, min((90 - data[2][0+9]), 180)) #coxa5
        kit2.servo[11].angle = max(0, min((180 - data[6][1] - data[2][1+9]), 180)) #femur5
        kit2.servo[12].angle = max(0, min((data[6][2] + data[2][2+9]), 180)) #tibia5

        kit1.servo[2].angle = max(0, min((90 - data [6][9] + data[4][6]), 180)) #coxa3
        kit1.servo[1].angle = max(0, min((data[6][7] + data[4][7]), 180)) #femur3
        kit1.servo[0].angle = max(0, min((180 - data[6][8] - data[4][8]), 180)) #tibia3

        kit2.servo[13].angle = max(0, min((90 +  data [6][9] - data[3][6+9]), 180)) #coxa4
        kit2.servo[14].angle = max(0, min((180 - data[6][7] - data[3][7+9]), 180)) #femur4
        kit2.servo[15].angle = max(0, min((data[6][8] + data[3][8+9]), 180)) #tibia4
        


        #femur 1 turun dan tibia turun sekalian adjust ngambil kaki
        kit1.servo[6].angle = max(0, min((180 - data[6][5] - data[0][5]), 180)) #tibia1
        wait(0.1)
        kit1.servo[7].angle = max(0, min((data[6][4] + data[0][4]), 180)) #femur1
        wait(delay)

        #femur 2 angkat
        kit1.servo[4].angle = max(0, min((data[6][1] + 45), 180)) #femur2
        kit1.servo[3].angle = max(0, min((180 - data[6][2] + 45), 180)) #tibia2
        wait(delay)

        #coxa 2 maju sisanya mundur
        kit1.servo[8].angle = max(0, min((90 + data[1][3]), 180)) #coxa1
        kit1.servo[7].angle = max(0, min((data[6][4] + data[1][4]), 180)) #femur1
        kit1.servo[6].angle = max(0, min((180 - data[6][5] - data[1][5]), 180)) #tibia1
        
        kit2.servo[7].angle = max(0, min((90 - data[2][3+9]), 180)) #coxa6
        kit2.servo[8].angle = max(0, min((180 - data[6][4] - data[2][4+9]), 180)) #femur6
        kit2.servo[9].angle = max(0, min((data[6][5] + data[2][5+9]), 180)) #tibia6

        kit1.servo[5].angle = max(0, min((90 + data[1][0]), 180)) #coxa2

        kit2.servo[10].angle = max(0, min((90 - data[3][0+9]), 180)) #coxa5
        kit2.servo[11].angle = max(0, min((180 - data[6][1] - data[3][1+9]), 180)) #femur5
        kit2.servo[12].angle = max(0, min((data[6][2] + data[3][2+9]), 180)) #tibia5

        kit1.servo[2].angle = max(0, min((90  - data[6][9] + data[5][6]), 180)) #coxa3
        kit1.servo[1].angle = max(0, min((data[6][7] + data[5][7]), 180)) #femur3
        kit1.servo[0].angle = max(0, min((180 - data[6][8] - data[5][8]), 180)) #tibia3

        kit2.servo[13].angle = max(0, min((90 + data[6][9] - data[4][6+9]), 180)) #coxa4
        kit2.servo[14].angle = max(0, min((180 - data[6][7] - data[4][7+9]), 180)) #femur4
        kit2.servo[15].angle = max(0, min((data[6][8] + data[4][8+9]), 180)) #tibia4

	#femur tibia 2 turun
        kit1.servo[3].angle = max(0, min((180 - data[6][2] - data[1][2]), 180)) #tibia2
        wait(0.1)
        kit1.servo[4].angle = max(0, min((data[6][1] + data[1][1]), 180)) #femur2
        wait(delay)

        #femur tibia 3 naik
        kit1.servo[1].angle = max(0, min((data[6][7] + 45), 180)) #femur3
        kit1.servo[0].angle = max(0, min((180 - data[6][8] + 45), 180)) #tibia3
        wait(delay)

 	#coxa 3 maju sisanya mundur 5 derajat
        kit1.servo[8].angle = max(0, min((90 + data[2][3]), 180)) #coxa1
        kit1.servo[7].angle = max(0, min((data[6][4] + data[2][4]), 180)) #femur1
        kit1.servo[6].angle = max(0, min((180 - data[6][5] - data[2][5]), 180)) #tibia1
        
        kit2.servo[7].angle = max(0, min((90 - data[3][3+9]), 180)) #coxa6
        kit2.servo[8].angle = max(0, min((180 - data[6][4] - data[3][4+9]), 180)) #femur6
        kit2.servo[9].angle = max(0, min((data[6][5] + data[3][5+9]), 180)) #tibia6

        kit1.servo[5].angle = max(0, min((90 + data[1][0]), 180)) #coxa2
        kit1.servo[4].angle = max(0, min((data[6][1] + data[1][1]), 180)) #femur2
        kit1.servo[3].angle = max(0, min((180 - data[6][2] - data[1][2]), 180)) #tibia2

        kit2.servo[10].angle = max(0, min((90 - data[4][0+9]), 180)) #coxa5
        kit2.servo[11].angle = max(0, min((180 - data[6][1] - data[4][1+9]), 180)) #femur5
        kit2.servo[12].angle = max(0, min((data[6][2] + data[4][2+9]), 180)) #tibia5

        kit1.servo[2].angle = max(0, min((90 - data[6][9] + data[0][6]), 180)) #coxa3

        kit2.servo[13].angle = max(0, min((90 + data[6][9] - data[5][6+9]), 180)) #coxa4
        kit2.servo[14].angle = max(0, min((180 - data[6][7] - data[5][7+9]), 180)) #femur4
        kit2.servo[15].angle = max(0, min((data[6][8] + data[5][8+9]), 180)) #tibia4
        

	#femur tibia 3 turun
        kit1.servo[0].angle = max(0, min((180 - data[6][8] - data[0][8]), 180)) #tibia3
        wait(0.1)
        kit1.servo[1].angle = max(0, min((data[6][7] + data[0][7]), 180)) #femur3
        wait(delay)

	#femur 4 angkats
        kit2.servo[14].angle = max(0, min((180 - data[6][7] - 45), 180)) #femur4
        kit2.servo[15].angle = max(0, min((data[6][8] - 45), 180)) #tibia4
        wait(delay)

	#coxa 4 maju sisanya mundur 5 derajat
        kit1.servo[8].angle = max(0, min((90 + data[3][3]), 180)) #coxa1
        kit1.servo[7].angle = max(0, min((data[6][4] + data[3][4]), 180)) #femur1
        kit1.servo[6].angle = max(0, min((180 - data[6][5] - data[3][5]), 180)) #tibia1
        
        kit2.servo[7].angle = max(0, min((90 - data[4][3+9]), 180)) #coxa6
        kit2.servo[8].angle = max(0, min((180 - data[6][4] - data[4][4+9]), 180)) #femur6
        kit2.servo[9].angle = max(0, min((data[6][5] + data[4][5+9]), 180)) #tibia6

        kit1.servo[5].angle = max(0, min((90 + data[2][0]), 180)) #coxa2
        kit1.servo[4].angle = max(0, min((data[6][1] + data[2][1]), 180)) #femur2
        kit1.servo[3].angle = max(0, min((180 - data[6][2] - data[2][2]), 180)) #tibia2

        kit2.servo[10].angle = max(0, min((90 - data[5][0+9]), 180)) #coxa5
        kit2.servo[11].angle = max(0, min((180 - data[6][1] - data[5][1+9]), 180)) #femur5
        kit2.servo[12].angle = max(0, min((data[6][2] + data[5][2+9]), 180)) #tibia5

        kit1.servo[2].angle = max(0, min((90 - data[6][9] + data[1][6]), 180)) #coxa3
        kit1.servo[1].angle = max(0, min((data[6][7] + data[1][7]), 180)) #femur3
        kit1.servo[0].angle = max(0, min((180 - data[6][8] - data[1][8]), 180)) #tibia3

        kit2.servo[13].angle = max(0, min((90 + data[6][9] - data[0][6+9]), 180)) #coxa4

	    
	#femur tibia 4 turun
        kit2.servo[15].angle = max(0, min((data[6][8] + data[0][8+9]), 180)) #tibia4
        wait(0.1)
        kit2.servo[14].angle = max(0, min((180 - data[6][7] - data[0][7+9]), 180)) #femur4
        wait(delay)

	#femur 5 angkat
        kit2.servo[11].angle = max(0, min((180 - data[6][1] - 45), 180)) #femur5
        kit2.servo[12].angle = max(0, min((data[6][2] - 45), 180)) #tibia5
        wait(delay)

	#coxa 5 maju sisanya mundur 5 derajat
        kit1.servo[8].angle = max(0, min((90 + data[4][3]), 180)) #coxa1
        kit1.servo[7].angle = max(0, min((data[6][4] + data[4][4]), 180)) #femur1
        kit1.servo[6].angle = max(0, min((180 - data[6][5] - data[4][5]), 180)) #tibia1
        
        kit2.servo[7].angle = max(0, min((90 - data[5][3+9]), 180)) #coxa6
        kit2.servo[8].angle = max(0, min((180 - data[6][4] - data[5][4+9]), 180)) #femur6
        kit2.servo[9].angle = max(0, min((data[6][5] + data[5][5+9]), 180)) #tibia6

        kit1.servo[5].angle = max(0, min((90 + data[3][0]), 180)) #coxa2
        kit1.servo[4].angle = max(0, min((data[6][1] + data[3][1]), 180)) #femur2
        kit1.servo[3].angle = max(0, min((180 - data[6][2] - data[3][2]), 180)) #tibia2

        kit2.servo[10].angle = max(0, min((90 - data[0][0+9]), 180)) #coxa5

        kit1.servo[2].angle = max(0, min((90 - data[6][9] + data[2][6]), 180)) #coxa3
        kit1.servo[1].angle = max(0, min((data[6][7] + data[2][7]), 180)) #femur3
        kit1.servo[0].angle = max(0, min((180 - data[6][8] - data[2][8]), 180)) #tibia3

        kit2.servo[13].angle = max(0, min((90 + data[6][9] - data[1][6+9]), 180)) #coxa4
        kit2.servo[14].angle = max(0, min((180 - data[6][7] - data[1][7+9]), 180)) #femur4
        kit2.servo[15].angle = max(0, min((data[6][8] + data[1][8+9]), 180)) #tibia4

	    
	#femur tibia 5 turun
        kit2.servo[12].angle = max(0, min((data[6][2] + data[0][2+9]), 180)) #tibia5
        wait(0.1)
        kit2.servo[11].angle = max(0, min((180 - data[6][1] - data[0][1+9]), 180)) #femur5
        wait(delay)

	#femur 6 angkat
        kit2.servo[8].angle = max(0, min((180 - data[6][4] - 45), 180)) #femur6
        kit2.servo[9].angle = max(0, min((data[6][5] - 45), 180)) #tibia6
        wait(delay)

	#coxa 6 maju sisanya mundur 5 derajat
        kit1.servo[8].angle = max(0, min((90 + data[5][3]), 180)) #coxa1
        kit1.servo[7].angle = max(0, min((data[6][4] + data[5][4]), 180)) #femur1
        kit1.servo[6].angle = max(0, min((180 - data[6][5] - data[5][5]), 180)) #tibia1
        
        kit2.servo[7].angle = max(0, min((90 - data[0][3+9]), 180)) #coxa6

        kit1.servo[5].angle = max(0, min((90 + data[4][0]), 180)) #coxa2
        kit1.servo[4].angle = max(0, min((data[6][1] + data[4][1]), 180)) #femur2
        kit1.servo[3].angle = max(0, min((180 - data[6][2] - data[4][2]), 180)) #tibia2

        kit2.servo[10].angle = max(0, min((90 - data[1][0+9]), 180)) #coxa5
        kit2.servo[11].angle = max(0, min((180 - data[6][1] - data[1][1+9]), 180)) #femur5
        kit2.servo[12].angle = max(0, min((data[6][2] + data[1][2+9]), 180)) #tibia5

        kit1.servo[2].angle = max(0, min((90 - data[6][9] + data[3][6]), 180)) #coxa3
        kit1.servo[1].angle = max(0, min((data[6][7] + data[3][7]), 180)) #femur3
        kit1.servo[0].angle = max(0, min((180 - data[6][8] - data[3][8]), 180)) #tibia3

        kit2.servo[13].angle = max(0, min((90 + data[6][9] - data[2][6+9]), 180)) #coxa4
        kit2.servo[14].angle = max(0, min((180 - data[6][7] - data[2][7+9]), 180)) #femur4
        kit2.servo[15].angle = max(0, min((data[6][8] + data[2][8+9]), 180)) #tibia4
	    
	#femur tibia 6 turun
        kit2.servo[9].angle = max(0, min((data[6][5] + data[0][5+9]), 180)) #tibia6
        wait(0.1)
        kit2.servo[8].angle = max(0, min((180 - data[6][4] - data[0][4+9]), 180)) #femur6
        wait(delay)
def main(args=None):
    rclpy.init(args=args)
    node = MyNode()
    rclpy.spin(node)
    rclpy.shutdown()
