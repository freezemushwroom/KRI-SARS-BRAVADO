#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from std_msgs.msg import Int32MultiArray
from std_msgs.msg import Int32
import time
import RPi.GPIO as GPIO
from adafruit_servokit import ServoKit
import board
import busio#

delay = 0.2


GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.BUTTON = 18
GPIO.LED = 23

GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  #Button
GPIO.setup(23, GPIO.OUT)  # LED
GPIO.output(23, GPIO.LOW)

def wait(waktu):
    flag = True
    myTime = time.time()
    while flag == True:
        currentTime = time.time()
        if currentTime - myTime < waktu:
            flag = True
        elif currentTime - myTime >= waktu:
            flag = False

TRIG = [19, 6, 22, 17, 21, 16, 25]
ECHO = [26, 13, 5, 27, 20, 12, 24]
for i in range (0,7):
    GPIO.setup(TRIG[i],GPIO.OUT)
    GPIO.output(TRIG[i], False)
    GPIO.setup(ECHO[i],GPIO.IN)

def ultrasonic(TRIG, ECHO):
    timeout = 100
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)
    pulse_start = time.time()
    time_timeout = time.time()
    while GPIO.input(ECHO)==0:
        if ((time.time() - time_timeout) *1000) > timeout:
            distance = 30
            return distance
        pulse_start = time.time()

    while GPIO.input(ECHO)==1:
        if ((time.time() - time_timeout) *1000) > timeout:
            distance = 30
            return distance
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150
    distance = round(distance, 2)
    return distance

class MyNode(Node):
    def __init__(self):
        super().__init__("process_node")
        self.timer_ = self.create_timer(1, self.process)

        self.subscriber_flag = self.create_subscription(Int32, "/flag_", self.flag_change, 1)

        self.publish_state = self.create_publisher(Int32MultiArray, "/state_", 1)
        self.publish_calibrate = self.create_publisher(Int32, "/calibrate_", 1)
        self.publish_count_time = self.create_publisher(Int32, "/count_time_", 1)
        self.publish_turn_on_roll = self.create_publisher(Int32, "/turn_on_roll_", 1)
        self.publish_turn_on_pitch = self.create_publisher(Int32, "/turn_on_pitch_", 1)
        self.publish_correction = self.create_publisher(Int32, "/correction_", 1)


        self.jarak = [0,0,0,0,0,0,0]
        self.flag = False
        self.constraint = 10

        #dibawah adalah variabel penghitung langkah
        self.forward_movement = 0
        self.last_forward_movement = 0
        self.backward_movement = 0
        self.right_movement = 0
        self.left_movement = 0
        self.turn_left = 0
        self.turn_right = 0
        #

        self.loop = 0

        self.mode = 0
        self.stop = 2
        self.add_delay = 0 #0.4
        self.constraint_left = [11,8.5] #[27,16] #[11,8.5]

    def flag_change(self, message:Int32):
        self.flag = not self.flag

    def process(self):
        if self.stop == 1: #looping berhenti setelah kelar ngitung
            state = Int32MultiArray()
            state.data = [9,0]
            self.publish_state.publish(state)
            return
        elif self.stop == 2: #trigger mulai ngitung waktu (buat ambil data)
            count_time = Int32()
            count_time.data = 1
            self.publish_count_time.publish(count_time)
            self.stop = 0

        self.jarak[0] = ultrasonic(TRIG[0], ECHO[0]) #ultrasonic depan
        if self.flag == True and self.mode == -4: #flag buat ganti detect depan (kondisi setelah naik tangga)
            self.constraint = -99 #???
            self.constraint_left = [27,15.5]
            self.add_delay = 0.4
            self.flag = False
            wait(5)
            #berhenti trus ngeluarin time elapsed#
#            count_time = Int32()
#            count_time.data = 1
#            self.publish_count_time.publish(count_time)
#            self.stop = 1
            #end of line#
#            return

        self.get_logger().info("Jarak Depan: " + str(self.jarak[0]))
        self.get_logger().info("Constraint " + str(self.constraint))
        self.get_logger().info("Constraint Kiri: " + str(self.constraint_left))
        state = Int32MultiArray()
        calibrate = Int32()


        if self.constraint == -99 and self.loop != 3:
            self.loop += 1
        if self.constraint == -99 and self.loop == 3:
            self.constraint = 38


        if self.jarak[0] <= self.constraint: #kalo jarak depan lebih kecil dari constraintnya
            wait(2)
            state.data = [9,0] #berhenti
            self.publish_state.publish(state)
            wait(3)
            self.jarak[1] = ultrasonic(TRIG[2], ECHO[2])
            self.jarak[2] = ultrasonic(TRIG[5], ECHO[5])
            self.get_logger().info("Jarak Kanan : " + str(self.jarak[1]))
            self.get_logger().info("Jarak Kiri  : " + str(self.jarak[2]))
            wait(1)
            if self.mode == -2 or self.mode == -4: #jalan strafe ke kiri, yaitu di mode akhir
                if self.mode == -4:
                    turn_on = Int32()
                    turn_on.data = 1
                    self.publish_turn_on_pitch.publish(turn_on)
                state.data = [11,0] #strafe kiri
                self.publish_state.publish(state)
                while True:
                    state.data = [11,0]
                    self.publish_state.publish(state)
                    wait(2 + self.add_delay)
                    self.jarak[2] = ultrasonic(TRIG[5], ECHO[5]) #ultrasonic kiri (6)
                    self.get_logger().info("Jarak Kiri : " + str(self.jarak[2]))
                    if self.jarak[2] <= self.constraint_left[0] and self.jarak[2] >= self.constraint_left[1]:
                        # kalau masih strafe maak mode -2, kalau udah akhir maka mode -4
                        if self.mode == -2: #setelah strafe kiri, yawnya berubah, constraintnya berubah
                            self.mode = 3
                            self.constraint = 20
                            correction = Int32()
                            correction.data = 20
                            self.publish_correction.publish(correction)
                            #berhenti trus ngeluarin time elapsed#
#                            count_time = Int32()
#                            count_time.data = 1
#                            self.publish_count_time.publish(count_time)
#                            self.stop = 1
                            #end of line#
                            break
                        elif self.mode == -4: #udah mentok kiri sampai titik finish
                            #looping stop
                            #berhenti trus ngeluarin time elapsed#
                            count_time = Int32()
                            count_time.data = 1
                            self.publish_count_time.publish(count_time)
                            self.stop = 1
                            #end of line#
                            break
            elif self.mode == 3: #setelah selesai bagian 3, yawnya berubah balik, constraintnya diperpendek, rollnya diaktifin
                self.constraint = 0
                flag_data = Int32()
                flag_data.data = 0
                self.publish_correction.publish(flag_data)
                flag_data.data = 1
                self.publish_turn_on_roll.publish(flag_data)
                self.mode = -4
                #berhenti trus ngeluarin time elapsed#
#                count_time = Int32()
#                count_time.data = 1
#                self.publish_count_time.publish(count_time)
#                self.stop = 1
                #end of line#
            else: # akan masuk sini kalau mode == 0, lalu menentukan apakah belok kiri atau belok kanan, tergantung jarak kiri dan kanan, kalau sama maka default belok kiri
                if self.jarak[1] < self.jarak[2] or self.jarak[2] < self.jarak[1]:  #logika belok kiri (harusnya ga ada belok kanan jadinya force belok kiri)
                    state.data = [1,0] # 1 belok kiri atau 2 belok kanan
                    self.publish_state.publish(state)
                    wait(1.2)
                    self.publish_state.publish(state)
                    wait(1.2)
                    self.publish_state.publish(state)
                    wait(1.2)
                    self.publish_state.publish(state)
                    wait(2)
                    calibrate.data = -1
                    self.mode = self.mode - 1
                    self.publish_calibrate.publish(calibrate)
                    wait(2)
                    state.data = [9,0]
                    self.publish_state.publish(state)
                    wait(3)
                    #berhenti trus ngeluarin time elapsed#
#                    count_time = Int32()
#                    count_time.data = 1
#                    self.publish_count_time.publish(count_time)
#                    self.stop = 1
                    #end of line#
                else: #kalo logika diatas ga ada yang ketrima, jalan lurus terus, tergantung self trigger_Strafenya, mepetnya ke trigger
                    # ini brarti robot lagi perlu strafe ke kiri
                    if self.mode == -2:
                        self.jarak[3] = ultrasonic(TRIG[2],ECHO[2])
                        self.get_logger().info("Jarak Kanan : " + str(self.jarak[3]))
                        if self.jarak[3] >= 10:
                            state.data = [0,1]
                        else:
                            state.data = [0,0]
                    else:
                        state.data = [0,0]
                    self.publish_state.publish(state)
        else:
            if self.mode == -2:
                self.jarak[3] = ultrasonic(TRIG[2],ECHO[2])
                self.get_logger().info("Jarak Kanan : " + str(self.jarak[3]))
                if self.jarak[3] >= 10:
                    state.data = [0,1]
                else:
                    state.data = [0,0]
            else: # disini dia maju terus aja, dan mode == 0
                state.data = [0,0]
            self.publish_state.publish(state)

    def process2(self):
        if self.stop == 1: #looping berhenti setelah kelar ngitung
            state = Int32MultiArray()
            state.data = [9,0]
            self.publish_state.publish(state)
            return
        elif self.stop == 2: #trigger mulai ngitung waktu (buat ambil data)
            count_time = Int32()
            count_time.data = 1
            self.publish_count_time.publish(count_time)
            self.stop = 0
        
        self.jarak[0] = ultrasonic(TRIG[0], ECHO[0]) #ultrasonic depan
        self.get_logger().info("Jarak Depan: " + str(self.jarak[0]))
        self.get_logger().info("Constraint " + str(self.constraint))
        self.get_logger().info("Constraint Kiri: " + str(self.constraint_left))
        state = Int32MultiArray()
        calibrate = Int32()

        if self.jarak[0] <= self.constraint: #kalo jarak depan lebih kecil dari constraintnya
            # dibawah kita ngecek kiri dan kanan apakah ada dinding
            wait(2)
            state.data = [9,0] #berhenti
            self.publish_state.publish(state)
            wait(3)
            self.jarak[1] = ultrasonic(TRIG[2], ECHO[2])
            self.jarak[2] = ultrasonic(TRIG[5], ECHO[5])
            self.get_logger().info("Jarak Kanan : " + str(self.jarak[1]))
            self.get_logger().info("Jarak Kiri  : " + str(self.jarak[2]))
            wait(1)
            # disini cek apakah sudah pengambilan korban atau belum 
            if self.mode == -1 or self.mode == -3: #brarti sudah mengambil korban dan belum mundur
                # kita mundur dulu biar ultrasonik nggak kehalang
                # ini buat mode -1 perpindahan ke mode -2
                # atau mode -3 perpindahan ke mode -4
                
                # selesai belok kanan, sekarang siap taruh korban
                # selesai taruh korban
                # lalu kita mundur lagi
                if self.mode == -1:
                    self.data = [-1, 0] # mundur
                    self.publish_state.publish(state)
                    wait(1.2)
                    for i in range(4):
                        self.data = [2, 0] # belok kanan
                        self.publish_state.publish(state)
                        wait(1.2)
                    self.data = [9, 0] # stop
                    self.publish_state.publish(state)
                    wait(1.2)
                elif self.mode == -3:
                    # sebenernya langsung taro korban aja
                    self.data = [9, 0] # stop
                    self.publish_state.publish(state)
                # disini mdoe menaru korban
                # selesai menaruh korban, sekarang kita mundur lagi
                self.data = [-1, 0] # mundur
                self.publish_state.publish(state)
                for i in range(8):
                    self.data = [1, 0] # belok kiri
                    self.publish_state.publish(state)
                    wait(1.2)
                self.mode = self.mode -1 # sekarang mode -2
                # atau menjadi -4
                # sekarang kita kembali jalan maju 5 langkah 
                self.last_forward_movement = self.forward_movement # simpan counter terakhir
            if self.mode == -4 and self.forward_movement - self.last_forward_movement >= 3:
                # disini sudah mode 4 yaitu strafe kiri, dan setidaknya sudah jalan maju 3 langkah dari titik terakhir, maka kita stop aja
                state.data = [11,0] #strafe kiri
                self.publish_state.publish(state)w
                while True:
                    state.data = [11,0]
                    self.publish_state.publish(state)
                    wait(2 + self.add_delay)
                    self.jarak[2] = ultrasonic(TRIG[5], ECHO[5])
                    self.get_logger().info("Jarak Kiri : " + str(self.jarak[2]))
                    if self.jarak[2] <= self.constraint_left[0] and self.jarak[2] >= self.constraint_left[1]:
                        # kalau masih strafe maak mode -2, kalau udah akhir maka mode -4
                        if self.mode == -4: #setelah strafe kiri, yawnya berubah, constraintnya berubah
                            self.mode = self.mode -1 # sekarang mode -5
                            self.constraint = 20
                            correction = Int32()
                            correction.data = 20 # ini tuh biar yawnya balik ke 0, karena sebelumnya yawnya -20
                            self.publish_correction.publish(correction)
                            # karena mode 4, maka pas maju udah ada correctionnya
                            break
                        elif self.mode == -6: #udah mentok kiri sampai titik finish
                            #looping stop
                            #berhenti trus ngeluarin time elapsed#
                            count_time = Int32()
                            count_time.data = 1
                            self.publish_count_time.publish(count_time)
                            self.stop = 1
                            #end of line#
                            break # dari sini sudah return jadi selesai

            elif self.mode == -5: # artinya lagi siapin buat ke tangga
                # dari mode -5 ke -6
                self.constraint = 0
                flag_data = Int32()
                flag_data.data = 0  
                self.publish_correction.publish(flag_data)
                flag_data.data = 1
                self.publish_turn_on_roll.publish(flag_data)
                self.mode = self.mode -1 # sekarang mode -6
                # berarti persiapan buat naik tangga
        else: # ini adalah mode 0 kalau tidak terdeteksi apapun
            #kita akan mengukur berapa langkah kaki sampai korban pertama
            if self.forward_movement < 7 or (self.forward_movement > 7 and (self.mode == -1 or self.mode == -4 or self.mode == -6)): # kita anggap 7 langkah dulu
                # ini buat mode 0
                # buat mode -2
                # atau mode -4
                state.data = [0,0] #maju
                self.publish_state.publish(state)
                self.forward_movement += 1
            elif self.forward_movement == 7 or self.forward_movement - self.last_forward_movement == 5:
                # move == 7(step ke korban pertama)
                # delta move == 5 (step ke korban kedua)
                # ini buat mode 0 dan perpindahan ke mode -1
                # atau mode -2 ke mode -3
                # putar kiri
                state.data = [9,0] #berhenti
                self.publish_state.publish(state)
                wait(3)
                state.data = [1,0] # disini kita belok kiri
                self.publish_state.publish(state)
                wait(1.2)
                self.publish_state.publish(state)
                wait(1.2)
                self.publish_state.publish(state)
                wait(1.2)
                self.publish_state.publish(state)
                wait(2)
                # proses deteksi korban dan mengambil korban pertama
                # end proses atau, atau end publish state  
                calibrate.data = -1
                self.mode = self.mode -1 # sekarang mode -1
                # or mode -3
                self.publish_calibrate.publish(calibrate)
                wait(2)
                state.data = [9,0] #stop
                self.publish_state.publish(state)
                wait(3)
                # lalu putar kanan
                state.data = [-1, 0] # mundur
                self.publish_state.publish(state)
                wait(1.2)
                for i in range(4):
                    self.data = [2, 0] # belok kanan
                    self.publish_state.publish(state)
                    wait(1.2)

                

# bagian kode dibawah kita ignore dulu
        
        if self.mode == 0:
            # mode awal dan maju dulu lalu nanti belok kiri
            state.data = [0,0]
            self.publish_state.publish(state)

        elif self.mode == 1:
            # mode mengambil korban dan menaruh pada titik drop
        
        elif self.mode == 2:
            # mode jaaln mundur dan belok kiri untuk mengambil korban kedua
        
        elif self.mode == 3:
            # mode belok kanan dan taruh korban kedua pada titik drop
        
        elif self.mode == 4:
            # mode belok kiri dan maju serta strafe
        
        elif self.mode == 5:
            # mode tangga
        
        elif self.mode == 6:
            # mode setelah tangga, dan jalan strafe kiri
        
        elif self.mode == 7:
            # mode akhir dan selesai
        
        else:
            # exception saja

        #

def main(args=None):
    rclpy.init(args=args)
    node = MyNode()
    #coxa ke tengah
#    kit1.servo[8].angle = 90 #coxa1
#    kit2.servo[7].angle = 90 #coxa6
#    kit1.servo[5].angle = 90 #coxa2
#    kit2.servo[10].angle = 90 #coxa5
#    kit1.servo[2].angle = 90 #coxa3
#    kit2.servo[13].angle = 90 #coxa4
#    wait(1)
    #femur naik
#    kit1.servo[7].angle = 170 #femur1
#    kit2.servo[8].angle = 10 #femur6
#    kit1.servo[4].angle = 170 #femur2
#    kit2.servo[11].angle = 10 #femur5
#    kit1.servo[1].angle = 170 #femur3
#    kit2.servo[14].angle = 10 #femur4

#    kit1.servo[6].angle = 100 #tibia1
#    kit2.servo[9].angle = 80 #tibia6
#    kit1.servo[3].angle = 100 #tibia2
#    kit2.servo[12].angle = 80 #tibia5
#    kit1.servo[0].angle = 100 #tibia3
#    kit2.servo[15].angle = 80 #tibia4
#    wait(0.5)
    #tibia naik
#    kit1.servo[6].angle = 180
#    kit2.servo[9].angle = 0
#    kit1.servo[3].angle = 180
#    kit2.servo[12].angle = 0
#    kit1.servo[0].angle = 180
#    kit2.servo[15].angle = 0
#    wait(0.5)
    #femur turun berdiri + tibia adjust
#    for i in range (0, 46, 5):
#        kit1.servo[6].angle = 180 - (i) #tibia1
#        kit2.servo[9].angle = 0 + (i) #tibia6
#        kit1.servo[3].angle = 180 - (i) #tibia2
#        kit2.servo[12].angle = 0 + (i) #tibia5
#        kit1.servo[0].angle = 180 - (i) #tibia3
#        kit2.servo[15].angle = 0 + (i) #tibia4
#        kit1.servo[7].angle = 180 - (i+5) #femur1
#        kit2.servo[8].angle = 0 + (i+10) #femur6
#        kit1.servo[4].angle = 180 - (i+5) #femur2
#        kit2.servo[11].angle = 0 + (i+10) #femur5
#        kit1.servo[1].angle = 180 - (i+5) #femur3
#        kit2.servo[14].angle = 0 + (i+10) #femur4
    time.sleep(5)
    GPIO.output(23, GPIO.HIGH)
    node.get_logger().info("System Ready")
    #while True:
    #    if GPIO.input(18)==1:
    #        GPIO.output(23, GPIO.LOW)
    #        break
    rclpy.spin(node)
    rclpy.shutdown()
