#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from std_msgs.msg import Int32MultiArray, MultiArrayDimension
from std_msgs.msg import Int32
import time
import math
import numpy as np

coxa = 2.644
femur = 6.436
tibia = 8.122
l = 6.436


#0 tripod, 1 wave, 2 tetrapod
gait = 0


lebar_depan_belakang = 24.5
lebar_tengah = 33.5

panjang_depan_belakang = 23.3
panjang_depan_tengah = 13

def nilai_h(panjang, derajat, maju, geser, nambah):
    h = tibia + (math.tan(math.radians(derajat))*panjang) + nambah
    alpha1 = math.acos(((femur*tibia)-(math.sqrt((math.pow(femur,2)*math.pow(tibia,2))+(math.pow(femur,2)*(math.pow(h,2)-math.pow(tibia,2))))))/math.pow(femur,2))
    l = math.sin(alpha1)*femur - geser
    return h, l


def IK_tengah(maju, yaw, panjang, roll, geser, nambah):
#    h_belakang = tibia + (math.tan(math.radians(abs(min(roll,15))))*panjang_depan_belakang/2)
#    h_tengah = ((panjang_depan_belakang/2)/panjang_depan_belakang)*h_belakang
    h,l = nilai_h(panjang, abs(roll), maju, geser, nambah)
    P = math.sqrt(math.pow(maju,2)+math.pow((l+coxa),2)-(2*maju*(l+coxa)*math.cos(math.radians(90-(yaw))))) #panjang diagonal setelah kaki maju
    sudut_base_coxa_tengah = math.degrees(math.acos((math.pow((l+coxa),2)+math.pow(P,2)-math.pow(maju,2))/(2*(l+coxa)*P)))
    P = P-coxa
    M = math.sqrt(math.pow(h,2)+math.pow(P,2)) #panjang garis miring antara femur tibia

    sudut_coxa_femur_1_tengah = math.degrees(math.acos((math.pow(femur,2)+math.pow(M,2)-math.pow(tibia,2))/(2*femur*M)))
    sudut_coxa_femur_2_tengah = math.degrees(math.acos((math.pow(M,2)+math.pow(h,2)-math.pow(P,2))/(2*h*M)))
    sudut_coxa_femur_total = sudut_coxa_femur_1_tengah + sudut_coxa_femur_2_tengah
    sudut_femur_tibia_tengah = math.degrees(math.acos((math.pow(femur,2)+math.pow(tibia,2)-math.pow(M,2))/(2*tibia*femur)))
    return (sudut_base_coxa_tengah, sudut_coxa_femur_total, sudut_femur_tibia_tengah)

def IK_depan(maju,yaw, panjang, roll, geser):
    h,l = nilai_h(panjang, max(-15, roll), maju, geser, 0)
    PD = math.sqrt(math.pow(maju,2)+math.pow((l+coxa),2)-(2*maju*(l+coxa)*math.cos(math.radians(135-(yaw)))))
    sudut_base_coxa_depan = math.degrees(math.acos((math.pow((l+coxa),2)+math.pow(PD,2)-math.pow(maju,2))/(2*(l+coxa)*PD)))
    PD = PD-coxa
    MD = math.sqrt(math.pow(h,2)+math.pow(PD,2)) #panjang garis miring antara femur tibia
    sudut_coxa_femur_1_depan = math.degrees(math.acos((math.pow(femur,2)+math.pow(MD,2)-math.pow(tibia,2))/(2*femur*MD)))
    sudut_coxa_femur_2_depan = math.degrees(math.acos((math.pow(MD,2)+math.pow(h,2)-math.pow(PD,2))/(2*h*MD)))
    sudut_coxa_femur_total_depan = sudut_coxa_femur_1_depan + sudut_coxa_femur_2_depan
    sudut_femur_tibia_depan = math.degrees(math.acos((math.pow(femur,2)+math.pow(tibia,2)-math.pow(MD,2))/(2*tibia*femur)))
    return(sudut_base_coxa_depan, sudut_coxa_femur_total_depan, sudut_femur_tibia_depan)

def IK_belakang(maju, yaw, panjang, roll, mundur, geser):
    h,l = nilai_h(panjang, -min(roll, 15), maju, geser, 0)
    PB = math.sqrt(math.pow(maju,2)+math.pow((l+coxa),2)-(2*maju*(l+coxa)*math.cos(math.radians(90-mundur-45-(yaw)))))
    sudut_base_coxa_belakang = math.degrees(math.acos((math.pow((l+coxa),2)+math.pow(PB,2)-math.pow(maju,2))/(2*(l+coxa)*PB)))
    PB = PB - coxa
    MB = math.sqrt(math.pow(h,2)+math.pow(PB,2)) #panjang garis miring antara femur tibia
    sudut_coxa_femur_1_belakang = math.degrees(math.acos((math.pow(femur,2)+math.pow(MB,2)-math.pow(tibia,2))/(2*femur*MB)))
    sudut_coxa_femur_2_belakang = math.degrees(math.acos((math.pow(MB,2)+math.pow(h,2)-math.pow(PB,2))/(2*h*MB)))
    sudut_coxa_femur_total_belakang = sudut_coxa_femur_1_belakang + sudut_coxa_femur_2_belakang
    sudut_femur_tibia_belakang = math.degrees(math.acos((math.pow(femur,2)+math.pow(tibia,2)-math.pow(MB,2))/(2*tibia*femur)))
    return(sudut_base_coxa_belakang, sudut_coxa_femur_total_belakang, sudut_femur_tibia_belakang)

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
        super().__init__("gait_node")

        self.subscriber_move = self.create_subscription(Int32MultiArray, "/gait_", self.move, 1) #fungsi buat mulai jalan tapi harus dapet data gyro dulu dengan fungsi trigger

        self.publish_tripod_angle = self.create_publisher(Int32MultiArray, "/tripod_angle_", 1)
        self.publish_wave_angle = self.create_publisher(Int32MultiArray, "/wave_angle_", 1)
        self.publish_tetrapod_angle = self.create_publisher(Int32MultiArray, "/tetrapod_angle_", 1)
        self.publish_tetrapod_tangga_angle = self.create_publisher(Int32MultiArray, "tetrapod_tangga_angle_", 1)
        self.publish_turn_angle = self.create_publisher(Int32MultiArray, "/turn_angle_", 1)
        self.publish_stop_angle = self.create_publisher(Int32MultiArray, "/stop_angle_", 1)
        self.publish_strafe_angle = self.create_publisher(Int32MultiArray, "/strafe_angle_", 1)

        self.publish_flag = self.create_publisher(Int32, "/flag_", 1)

        self.roll = 0
        self.pitch = 0
        self.mundur = 0
        self.temp = 0
        self.flag = 1
        self.forward = 4
        self.delay = 1
        self.mepet = 0
        self.flag_stop_tangga = 0 #0
        self.roll_flag = 0 #0
        self.tambah_tinggi_kaki_tengah = 0


    def move(self, message = Int32MultiArray):
        self.get_logger().info("Receiving Yaw = " + str(message.data[0])+ ", & Roll = " + str(message.data[1]) + ", & Pitch = " + str(message.data[4]) + ", & State = " + str(message.data[2]) + " Mepet = " + str(message.data[3]))
        self.temp = message.data[1]
        self.mepet = message.data[3]*2

        if self.temp <= -5 and self.temp > -14 and self.roll_flag == 0:
            self.tambah_tinggi_kaki_tengah = (-0.25 * max(self.temp, -15)) - 1.25 #   map_value(self.roll, -10, 30, 0, 2)
            self.roll = max(message.data[1], -15)
            self.delay = 2

        if self.temp <= -14 and self.flag_stop_tangga == 0:
            if gait == 0:
                self.mundur = 10
                self.roll = -24
            if gait == 2:
                self.mundur = -20
                self.roll = -20
            self.flag = 0
            self.forward = 4
            self.delay = 2
            self.mepet = 0
            self.flag_stop_tangga = 1
            self.roll_flag = 1
            self.tambah_tinggi_kaki_tengah = 0

        if self.temp >= 9 and self.flag == 0:
            self.mundur = 0
            self.roll = 0
            self.flag = 1
            self.forward = 4
            self.delay = 1
            trig = Int32()
            trig.data = 1
            self.publish_flag.publish(trig)
            self.mepet = 0
            self.flag_stop_tangga = 1

        self.get_logger().info("Nilai Roll Clamp = " + str(self.roll))
        base_coxa_tengah_berdiri, coxa_femur_tengah_berdiri, femur_tibia_tengah_berdiri = IK_tengah(0,0,0,self.roll, 0, self.tambah_tinggi_kaki_tengah)
        base_coxa_depan_berdiri, coxa_femur_depan_berdiri, femur_tibia_depan_berdiri = IK_depan(0,0, panjang_depan_belakang/2, self.roll, 0)
        base_coxa_belakang_berdiri, coxa_femur_belakang_berdiri, femur_tibia_belakang_berdiri = IK_belakang(0,0, panjang_depan_belakang/2, self.roll, self.mundur, 0)
        if self.flag_stop_tangga == 1:
            wait(6)
            self.flag_stop_tangga = 2
            angle = Int32MultiArray()
            angle.data = [90, int(coxa_femur_tengah_berdiri+35), int(femur_tibia_tengah_berdiri-45), 90, int(coxa_femur_depan_berdiri+35), int(femur_tibia_depan_berdiri-45), 90, int(coxa_femur_belakang_berdiri+35), int(femur_tibia_belakang_berdiri-45)]
            self.get_logger().info("Stop")
            self.get_logger().info(f"Published: {angle.data}")
            self.publish_stop_angle.publish(angle)
            wait(2)
            return

        if message.data[2] == 0: #maju
            if message.data[0] > 6:
                yaw = 6.8
            elif message.data[0] < -6:
                yaw = -6.8
            else:
                yaw = message.data[0]
            forward_compen_depan_belakang = math.tan(math.radians(yaw))*lebar_depan_belakang
            forward_compen_tengah = math.tan(math.radians(yaw))*lebar_tengah
            if yaw > 0:
                forward_kiri_depan_belakang = self.forward
                forward_kiri_tengah = self.forward
                forward_kanan_depan_belakang = self.forward - forward_compen_depan_belakang
                forward_kanan_tengah = self.forward - forward_compen_tengah
            elif yaw < 0:
                forward_kiri_depan_belakang = self.forward + forward_compen_depan_belakang
                forward_kiri_tengah = self.forward + forward_compen_tengah
                forward_kanan_depan_belakang = self.forward
                forward_kanan_tengah = self.forward
            else:
                forward_kiri_depan_belakang = self.forward
                forward_kiri_tengah = self.forward
                forward_kanan_depan_belakang = self.forward
                forward_kanan_tengah = self.forward
            self.get_logger().info("Nilai Yaw Clamp: " + str(yaw))
            self.get_logger().info("Nilai Geser Mepet: " + str(self.mepet))
            if gait == 0: #tripod
                angle = Int32MultiArray()
                base_coxa_tengah_kiri, coxa_femur_tengah_kiri, femur_tibia_tengah_kiri = IK_tengah(forward_kiri_tengah, (yaw), 0, self.roll, self.mepet, self.tambah_tinggi_kaki_tengah)
                base_coxa_tengah_kiri = base_coxa_tengah_kiri - base_coxa_tengah_berdiri
                coxa_femur_tengah_kiri = coxa_femur_tengah_kiri - coxa_femur_tengah_berdiri
                femur_tibia_tengah_kiri = femur_tibia_tengah_kiri - femur_tibia_tengah_berdiri

                base_coxa_depan_kiri, coxa_femur_depan_kiri, femur_tibia_depan_kiri = IK_depan(forward_kiri_depan_belakang, (yaw), panjang_depan_belakang/2, self.roll, self.mepet)
                base_coxa_depan_kiri = base_coxa_depan_kiri - base_coxa_depan_berdiri
                coxa_femur_depan_kiri = coxa_femur_depan_kiri - coxa_femur_depan_berdiri
                femur_tibia_depan_kiri = femur_tibia_depan_kiri - femur_tibia_depan_berdiri

                base_coxa_belakang_kiri, coxa_femur_belakang_kiri, femur_tibia_belakang_kiri = IK_belakang(forward_kiri_depan_belakang, (yaw), panjang_depan_belakang/2, self.roll, self.mundur, self.mepet)
                base_coxa_belakang_kiri = base_coxa_belakang_kiri - base_coxa_belakang_berdiri
                coxa_femur_belakang_kiri = coxa_femur_belakang_kiri - coxa_femur_belakang_berdiri
                femur_tibia_belakang_kiri = femur_tibia_belakang_kiri - femur_tibia_belakang_berdiri

                base_coxa_tengah_kanan, coxa_femur_tengah_kanan, femur_tibia_tengah_kanan = IK_tengah(forward_kanan_tengah, ((-yaw)), 0, self.roll, -self.mepet, self.tambah_tinggi_kaki_tengah)
                base_coxa_tengah_kanan = base_coxa_tengah_kanan - base_coxa_tengah_berdiri
                coxa_femur_tengah_kanan = coxa_femur_tengah_kanan - coxa_femur_tengah_berdiri
                femur_tibia_tengah_kanan = femur_tibia_tengah_kanan - femur_tibia_tengah_berdiri

                base_coxa_depan_kanan, coxa_femur_depan_kanan, femur_tibia_depan_kanan = IK_depan(forward_kanan_depan_belakang, ((-yaw)), panjang_depan_belakang/2, self.roll, -self.mepet)
                base_coxa_depan_kanan = base_coxa_depan_kanan - base_coxa_depan_berdiri
                coxa_femur_depan_kanan = coxa_femur_depan_kanan - coxa_femur_depan_berdiri
                femur_tibia_depan_kanan = femur_tibia_depan_kanan - femur_tibia_depan_berdiri

                base_coxa_belakang_kanan, coxa_femur_belakang_kanan, femur_tibia_belakang_kanan = IK_belakang(forward_kanan_depan_belakang, ((-yaw)), panjang_depan_belakang/2, self.roll, self.mundur, -self.mepet)
                base_coxa_belakang_kanan = base_coxa_belakang_kanan - base_coxa_belakang_berdiri
                coxa_femur_belakang_kanan = coxa_femur_belakang_kanan - coxa_femur_belakang_berdiri
                femur_tibia_belakang_kanan = femur_tibia_belakang_kanan - femur_tibia_belakang_berdiri

                angle.data = [int(base_coxa_tengah_kiri), int(coxa_femur_tengah_kiri)*self.flag, int(femur_tibia_tengah_kiri)*self.flag, int(base_coxa_depan_kiri), int(coxa_femur_depan_kiri)*self.flag, int(femur_tibia_depan_kiri)*self.flag, int(base_coxa_belakang_kiri), int(coxa_femur_belakang_kiri)*self.flag, int(femur_tibia_belakang_kiri)*self.flag, int(base_coxa_tengah_kanan), int(coxa_femur_tengah_kanan)*self.flag, int(femur_tibia_tengah_kanan)*self.flag, int(base_coxa_depan_kanan), int(coxa_femur_depan_kanan)*self.flag, int(femur_tibia_depan_kanan)*self.flag, int(base_coxa_belakang_kanan), int(coxa_femur_belakang_kanan)*self.flag, int(femur_tibia_belakang_kanan)*self.flag, int(coxa_femur_tengah_berdiri+35), int(femur_tibia_tengah_berdiri-45), int(coxa_femur_depan_berdiri+35), int(femur_tibia_depan_berdiri-45), int(coxa_femur_belakang_berdiri+35), int(femur_tibia_belakang_berdiri-45), self.mundur, self.delay]
                if self.flag == 0:
                #    angle.data = [int(30), int(0), int(0), int(30), int(0), int(0), int(25), int(0), int(0), int(20), int(0), int(0), int(21), int(0), int(0), int(21), int(0), int(0), int(coxa_femur_tengah_berdiri+35), int(femur_tibia_tengah_berdiri-45), int(coxa_femur_depan_berdiri+35), int(femur_tibia_depan_berdiri-45), int(coxa_femur_belakang_berdiri+35), int(femur_tibia_belakang_berdiri-45), self.mundur, self.delay]
                    angle.data = [int(base_coxa_tengah_kiri*1.521739), int(0), int(0), int(base_coxa_depan_kiri*2.30769), int(0), int(0), int(base_coxa_belakang_kiri*0.8323), int(0), int(0), int(base_coxa_tengah_kanan*1.221739), int(0), int(0), int(base_coxa_depan_kanan*2.00769), int(0), int(0), int(base_coxa_belakang_kanan*1.04176), int(0), int(0), int(coxa_femur_tengah_berdiri+35), int(femur_tibia_tengah_berdiri-45), int(coxa_femur_depan_berdiri+35), int(femur_tibia_depan_berdiri-45), int(coxa_femur_belakang_berdiri+35), int(femur_tibia_belakang_berdiri-45), self.mundur, self.delay]
                self.get_logger().info(f"Published: {angle.data}")
                self.get_logger().info("Sending Tripod Angle")
                self.publish_tripod_angle.publish(angle)

            if gait == 1: #wave
                angle = Int32MultiArray()
                step_wave = [forward_kiri_depan_belakang, forward_kiri_tengah, forward_kanan_depan_belakang, forward_kanan_tengah]
#                self.get_logger().info(f"Step_wave: {step_wave}")
                decrement_wave = [0,0,0,0]
                angle_temp = np.zeros((7,18), dtype = int)
                self.mepet = self.mepet * 1
                decrement_mepet = 0
                decrement_mepet = self.mepet/6
                for i in range (4):
                    decrement_wave[i] = step_wave[i]/5
                for i in range (6):
                    base_coxa_tengah_kiri, coxa_femur_tengah_kiri, femur_tibia_tengah_kiri = IK_tengah(step_wave[1],(yaw), 0, self.roll, self.mepet)
                    base_coxa_tengah_kiri = base_coxa_tengah_kiri - base_coxa_tengah_berdiri
                    coxa_femur_tengah_kiri = coxa_femur_tengah_kiri - coxa_femur_tengah_berdiri
                    femur_tibia_tengah_kiri = femur_tibia_tengah_kiri - femur_tibia_tengah_berdiri

                    base_coxa_depan_kiri, coxa_femur_depan_kiri, femur_tibia_depan_kiri = IK_depan(step_wave[0],(yaw), panjang_depan_belakang/2, self.roll, self.mepet)
                    base_coxa_depan_kiri = base_coxa_depan_kiri - base_coxa_depan_berdiri
                    coxa_femur_depan_kiri = coxa_femur_depan_kiri - coxa_femur_depan_berdiri
                    femur_tibia_depan_kiri = femur_tibia_depan_kiri - femur_tibia_depan_berdiri

                    base_coxa_belakang_kiri, coxa_femur_belakang_kiri, femur_tibia_belakang_kiri = IK_belakang(step_wave[0],(yaw), panjang_depan_belakang/2, self.roll, self.mundur, self.mepet)
                    base_coxa_belakang_kiri = base_coxa_belakang_kiri - base_coxa_belakang_berdiri
                    coxa_femur_belakang_kiri = coxa_femur_belakang_kiri - coxa_femur_belakang_berdiri
                    femur_tibia_belakang_kiri = femur_tibia_belakang_kiri - femur_tibia_belakang_berdiri

                    base_coxa_tengah_kanan, coxa_femur_tengah_kanan, femur_tibia_tengah_kanan = IK_tengah(step_wave[3],((-yaw)), 0, self.roll, -self.mepet)
                    base_coxa_tengah_kanan = base_coxa_tengah_kanan - base_coxa_tengah_berdiri
                    coxa_femur_tengah_kanan = coxa_femur_tengah_kanan - coxa_femur_tengah_berdiri
                    femur_tibia_tengah_kanan = femur_tibia_tengah_kanan - femur_tibia_tengah_berdiri

                    base_coxa_depan_kanan, coxa_femur_depan_kanan, femur_tibia_depan_kanan = IK_depan(step_wave[2],((-yaw)), panjang_depan_belakang/2, self.roll, -self.mepet)
                    base_coxa_depan_kanan = base_coxa_depan_kanan - base_coxa_depan_berdiri
                    coxa_femur_depan_kanan = coxa_femur_depan_kanan - coxa_femur_depan_berdiri
                    femur_tibia_depan_kanan = femur_tibia_depan_kanan - femur_tibia_depan_berdiri

                    base_coxa_belakang_kanan, coxa_femur_belakang_kanan, femur_tibia_belakang_kanan = IK_belakang(step_wave[2],((-yaw)), panjang_depan_belakang/2, self.roll, self.mundur, -self.mepet)
                    base_coxa_belakang_kanan = base_coxa_belakang_kanan - base_coxa_belakang_berdiri
                    coxa_femur_belakang_kanan = coxa_femur_belakang_kanan - coxa_femur_belakang_berdiri
                    femur_tibia_belakang_kanan = femur_tibia_belakang_kanan - femur_tibia_belakang_berdiri

                    angle_temp[i] = [int(base_coxa_tengah_kiri), int(coxa_femur_tengah_kiri)*self.flag, int(femur_tibia_tengah_kiri)*self.flag, int(base_coxa_depan_kiri), int(coxa_femur_depan_kiri)*self.flag, int(femur_tibia_depan_kiri)*self.flag, int(base_coxa_belakang_kiri), int(coxa_femur_belakang_kiri)*self.flag, int(femur_tibia_belakang_kiri)*self.flag, int(base_coxa_tengah_kanan), int(coxa_femur_tengah_kanan)*self.flag, int(femur_tibia_tengah_kanan)*self.flag, int(base_coxa_depan_kanan), int(coxa_femur_depan_kanan)*self.flag, int(femur_tibia_depan_kanan)*self.flag, int(base_coxa_belakang_kanan), int(coxa_femur_belakang_kanan)*self.flag, int(femur_tibia_belakang_kanan)*self.flag]

                    for i in range (4):
                        step_wave[i] = step_wave[i] - decrement_wave[i]
                    self.mepet = self.mepet - decrement_mepet
                if self.flag == 0:
                    angle_temp[0] = [30, 0, 0, 25, 0, 0, 25, 0, 0, 20, 0, 0, 21, 0, 0, 21, 0, 0]
                    angle_temp[1] = [24, 0, 0, 20, 0, 0, 20, 0, 0, 16, 0, 0, 17, 0, 0, 17, 0, 0]
                    angle_temp[2] = [18, 0, 0, 15, 0, 0, 15, 0, 0, 12, 0, 0, 13, 0, 0, 13, 0, 0]
                    angle_temp[3] = [12, 0, 0, 10, 0, 0, 10, 0, 0, 8, 0, 0, 9, 0, 0, 9, 0, 0]
                    angle_temp[4] = [6, 0, 0, 5, 0, 0, 5, 0, 0, 4, 0, 0, 4, 0, 0, 4, 0, 0]
                angle_temp[6] = [int(base_coxa_tengah_berdiri), int(coxa_femur_tengah_berdiri+35), int(femur_tibia_tengah_berdiri-45), int(base_coxa_depan_berdiri), int(coxa_femur_depan_berdiri+35), int(femur_tibia_depan_berdiri-45), int(base_coxa_belakang_berdiri), int(coxa_femur_belakang_berdiri+35), int(femur_tibia_belakang_berdiri-45), self.mundur, 0, 0, 0, 0, 0, 0, 0, self.delay]
                angle.data = angle_temp.flatten().tolist()
                angle.layout.dim.append(MultiArrayDimension(label="rows", size=7, stride=7*18))
                angle.layout.dim.append(MultiArrayDimension(label="cols", size=18, stride=18))
                #self.get_logger().info(f"Published: {angle.data}")
                self.get_logger().info("Sending Wave Angle")
                self.publish_wave_angle.publish(angle)

            if gait == 2: #tetrapod
                angle = Int32MultiArray()
                step_tetrapod = [forward_kiri_depan_belakang, forward_kiri_tengah, forward_kanan_depan_belakang, forward_kanan_tengah]
                if self.flag == 1:
                    decrement_tetrapod = [0,0,0,0]
                    decrement_mepet = 0
                    self.mepet = self.mepet * 2
                    angle_temp = np.zeros((4,18), dtype = int)
                    for i in range (4):
                        decrement_tetrapod[i] = step_tetrapod[i]/2
                    decrement_mepet = self.mepet/3
                    for i in range (3):
                        base_coxa_tengah_kiri, coxa_femur_tengah_kiri, femur_tibia_tengah_kiri = IK_tengah(step_tetrapod[1], (yaw), 0, self.roll, max(0,self.mepet), self.tambah_tinggi_kaki_tengah)
                        base_coxa_tengah_kiri = base_coxa_tengah_kiri - base_coxa_tengah_berdiri
                        coxa_femur_tengah_kiri = coxa_femur_tengah_kiri - coxa_femur_tengah_berdiri
                        femur_tibia_tengah_kiri = femur_tibia_tengah_kiri - femur_tibia_tengah_berdiri

                        base_coxa_depan_kiri, coxa_femur_depan_kiri, femur_tibia_depan_kiri = IK_depan(step_tetrapod[0],(yaw), panjang_depan_belakang/2, self.roll, max(0,self.mepet))
                        base_coxa_depan_kiri = base_coxa_depan_kiri - base_coxa_depan_berdiri
                        coxa_femur_depan_kiri = coxa_femur_depan_kiri - coxa_femur_depan_berdiri
                        femur_tibia_depan_kiri = femur_tibia_depan_kiri - femur_tibia_depan_berdiri

                        base_coxa_belakang_kiri, coxa_femur_belakang_kiri, femur_tibia_belakang_kiri = IK_belakang(step_tetrapod[0],(yaw), panjang_depan_belakang/2, self.roll, self.mundur, max(0,self.mepet))
                        base_coxa_belakang_kiri = base_coxa_belakang_kiri - base_coxa_belakang_berdiri
                        coxa_femur_belakang_kiri = coxa_femur_belakang_kiri - coxa_femur_belakang_berdiri
                        femur_tibia_belakang_kiri = femur_tibia_belakang_kiri - femur_tibia_belakang_berdiri

                        base_coxa_tengah_kanan, coxa_femur_tengah_kanan, femur_tibia_tengah_kanan = IK_tengah(step_tetrapod[3],((-yaw)), 0, self.roll, max(0,-self.mepet), self.tambah_tinggi_kaki_tengah)
                        base_coxa_tengah_kanan = base_coxa_tengah_kanan - base_coxa_tengah_berdiri
                        coxa_femur_tengah_kanan = coxa_femur_tengah_kanan - coxa_femur_tengah_berdiri
                        femur_tibia_tengah_kanan = femur_tibia_tengah_kanan - femur_tibia_tengah_berdiri

                        base_coxa_depan_kanan, coxa_femur_depan_kanan, femur_tibia_depan_kanan = IK_depan(step_tetrapod[2],((-yaw)), panjang_depan_belakang/2, self.roll, max(0,-self.mepet))
                        base_coxa_depan_kanan = base_coxa_depan_kanan - base_coxa_depan_berdiri
                        coxa_femur_depan_kanan = coxa_femur_depan_kanan - coxa_femur_depan_berdiri
                        femur_tibia_depan_kanan = femur_tibia_depan_kanan - femur_tibia_depan_berdiri

                        base_coxa_belakang_kanan, coxa_femur_belakang_kanan, femur_tibia_belakang_kanan = IK_belakang(step_tetrapod[2],((-yaw)), panjang_depan_belakang/2, self.roll, self.mundur, max(0,-self.mepet))
                        base_coxa_belakang_kanan = base_coxa_belakang_kanan - base_coxa_belakang_berdiri
                        coxa_femur_belakang_kanan = coxa_femur_belakang_kanan - coxa_femur_belakang_berdiri
                        femur_tibia_belakang_kanan = femur_tibia_belakang_kanan - femur_tibia_belakang_berdiri


                        angle_temp[i] = [int(base_coxa_tengah_kiri), int(coxa_femur_tengah_kiri)*self.flag, int(femur_tibia_tengah_kiri)*self.flag, int(base_coxa_depan_kiri), int(coxa_femur_depan_kiri)*self.flag, int(femur_tibia_depan_kiri)*self.flag, min(30,int(base_coxa_belakang_kiri)), int(coxa_femur_belakang_kiri)*self.flag, int(femur_tibia_belakang_kiri)*self.flag, int(base_coxa_tengah_kanan), int(coxa_femur_tengah_kanan)*self.flag, int(femur_tibia_tengah_kanan)*self.flag, int(base_coxa_depan_kanan), int(coxa_femur_depan_kanan)*self.flag, int(femur_tibia_depan_kanan)*self.flag, int(base_coxa_belakang_kanan), int(coxa_femur_belakang_kanan)*self.flag, int(femur_tibia_belakang_kanan)*self.flag]

                        for i in range (4):
                            step_tetrapod[i] = step_tetrapod[i] - decrement_tetrapod[i]
                        self.mepet = self.mepet - decrement_mepet
                    angle_temp[3] = [int(base_coxa_tengah_berdiri), int(coxa_femur_tengah_berdiri+35), int(femur_tibia_tengah_berdiri-45), int(base_coxa_depan_berdiri), int(coxa_femur_depan_berdiri+35), int(femur_tibia_depan_berdiri-45), int(base_coxa_belakang_berdiri), int(coxa_femur_belakang_berdiri+35), int(femur_tibia_belakang_berdiri-45), self.mundur, 0, 0, 0, 0, 0, 0, 0, self.delay]
                    angle.data = angle_temp.flatten().tolist()
                    angle.layout.dim.append(MultiArrayDimension(label="rows", size=4, stride=4*18))
                    angle.layout.dim.append(MultiArrayDimension(label="cols", size=18, stride=18))
                    self.get_logger().info("Sending Tetrapod Angle")
                    self.publish_tetrapod_angle.publish(angle)
                elif self.flag == 0:
                    angle_tangga = Int32MultiArray()
                    base_coxa_tengah_kiri, coxa_femur_tengah_kiri, femur_tibia_tengah_kiri = IK_tengah(forward_kiri_tengah, (yaw), 0, self.roll, self.mepet, self.tambah_tinggi_kaki_tengah)
                    base_coxa_tengah_kiri = base_coxa_tengah_kiri - base_coxa_tengah_berdiri
                    coxa_femur_tengah_kiri = coxa_femur_tengah_kiri - coxa_femur_tengah_berdiri
                    femur_tibia_tengah_kiri = femur_tibia_tengah_kiri - femur_tibia_tengah_berdiri

                    base_coxa_depan_kiri, coxa_femur_depan_kiri, femur_tibia_depan_kiri = IK_depan(forward_kiri_depan_belakang, (yaw), panjang_depan_belakang/2, self.roll, self.mepet)
                    base_coxa_depan_kiri = base_coxa_depan_kiri - base_coxa_depan_berdiri
                    coxa_femur_depan_kiri = coxa_femur_depan_kiri - coxa_femur_depan_berdiri
                    femur_tibia_depan_kiri = femur_tibia_depan_kiri - femur_tibia_depan_berdiri

                    base_coxa_belakang_kiri, coxa_femur_belakang_kiri, femur_tibia_belakang_kiri = IK_belakang(-forward_kiri_depan_belakang, (yaw), panjang_depan_belakang/2, self.roll, self.mundur, self.mepet)
                    base_coxa_belakang_kiri = (180-base_coxa_belakang_kiri) - (180-base_coxa_belakang_berdiri)
                    coxa_femur_belakang_kiri = coxa_femur_belakang_kiri - coxa_femur_belakang_berdiri
                    femur_tibia_belakang_kiri = femur_tibia_belakang_kiri - femur_tibia_belakang_berdiri

                    base_coxa_tengah_kanan, coxa_femur_tengah_kanan, femur_tibia_tengah_kanan = IK_tengah(forward_kanan_tengah, ((-yaw)), 0, self.roll, -self.mepet, self.tambah_tinggi_kaki_tengah)
                    base_coxa_tengah_kanan = base_coxa_tengah_kanan - base_coxa_tengah_berdiri
                    coxa_femur_tengah_kanan = coxa_femur_tengah_kanan - coxa_femur_tengah_berdiri
                    femur_tibia_tengah_kanan = femur_tibia_tengah_kanan - femur_tibia_tengah_berdiri

                    base_coxa_depan_kanan, coxa_femur_depan_kanan, femur_tibia_depan_kanan = IK_depan(forward_kanan_depan_belakang, ((-yaw)), panjang_depan_belakang/2, self.roll, -self.mepet)
                    base_coxa_depan_kanan = base_coxa_depan_kanan - base_coxa_depan_berdiri
                    coxa_femur_depan_kanan = coxa_femur_depan_kanan - coxa_femur_depan_berdiri
                    femur_tibia_depan_kanan = femur_tibia_depan_kanan - femur_tibia_depan_berdiri

                    base_coxa_belakang_kanan, coxa_femur_belakang_kanan, femur_tibia_belakang_kanan = IK_belakang(-forward_kanan_depan_belakang, ((-yaw)), panjang_depan_belakang/2, self.roll, self.mundur, -self.mepet)
                    base_coxa_belakang_kanan = (180-base_coxa_belakang_kanan) - (180-base_coxa_belakang_berdiri)
                    coxa_femur_belakang_kanan = coxa_femur_belakang_kanan - coxa_femur_belakang_berdiri
                    femur_tibia_belakang_kanan = femur_tibia_belakang_kanan - femur_tibia_belakang_berdiri
                    angle_tangga.data = [int(base_coxa_tengah_kiri), int(coxa_femur_tengah_kiri), int(femur_tibia_tengah_kiri), int(base_coxa_depan_kiri), int(coxa_femur_depan_kiri), int(femur_tibia_depan_kiri), int(base_coxa_belakang_kiri), int(coxa_femur_belakang_kiri), int(femur_tibia_belakang_kiri), int(base_coxa_tengah_kanan), int(coxa_femur_tengah_kanan), int(femur_tibia_tengah_kanan), int(base_coxa_depan_kanan), int(coxa_femur_depan_kanan), int(femur_tibia_depan_kanan), int(base_coxa_belakang_kanan), int(coxa_femur_belakang_kanan), int(femur_tibia_belakang_kanan), int(coxa_femur_tengah_berdiri+35), int(femur_tibia_tengah_berdiri-45), int(coxa_femur_depan_berdiri+35), int(femur_tibia_depan_berdiri-45), int(coxa_femur_belakang_berdiri+35), int(femur_tibia_belakang_berdiri-45), self.mundur, self.delay]
                    self.get_logger().info("Sending Tetrapod Stair Angle")
                    self.get_logger().info(f"Published: {angle_tangga.data}")
                    self.publish_tetrapod_tangga_angle.publish(angle_tangga)

        if message.data[2] == 1: #kiri
            angle = Int32MultiArray()
            angle.data = [60, int(coxa_femur_tengah_berdiri+35), int(femur_tibia_tengah_berdiri-45), 60, int(coxa_femur_depan_berdiri+35), int(femur_tibia_depan_berdiri-45), 60, int(coxa_femur_belakang_berdiri+35), int(femur_tibia_belakang_berdiri-45)]
            self.get_logger().info("Sending Angle Left")
            self.publish_turn_angle.publish(angle)

        if message.data[2] == 2 :
            angle = Int32MultiArray()
            angle.data = [120, int(coxa_femur_tengah_berdiri+35), int(femur_tibia_tengah_berdiri-45), 120, int(coxa_femur_depan_berdiri+35), int(femur_tibia_depan_berdiri-45), 120, int(coxa_femur_belakang_berdiri+35), int(femur_tibia_belakang_berdiri-45)]
            self.get_logger().info("Sending Angle Right")
            self.publish_turn_angle.publish(angle)

        if message.data[2] == 11:
            angle = Int32MultiArray()
            geser = -4
            if self.flag_stop_tangga == 2:
                delay = 3
                self.roll = -6
            else:
                delay = 1
                self.roll = 0

            base_coxa_tengah_kiri, coxa_femur_tengah_kiri, femur_tibia_tengah_kiri = IK_tengah(0,0, 0, self.roll, geser, 0)
            base_coxa_tengah_kiri = base_coxa_tengah_kiri - base_coxa_tengah_berdiri
            coxa_femur_tengah_kiri = coxa_femur_tengah_kiri - coxa_femur_tengah_berdiri
            femur_tibia_tengah_kiri = femur_tibia_tengah_kiri - femur_tibia_tengah_berdiri

            base_coxa_depan_kiri, coxa_femur_depan_kiri, femur_tibia_depan_kiri = IK_depan(0,0, panjang_depan_belakang/2, self.roll, geser)
            base_coxa_depan_kiri = base_coxa_depan_kiri - base_coxa_depan_berdiri
            coxa_femur_depan_kiri = coxa_femur_depan_kiri - coxa_femur_depan_berdiri
            femur_tibia_depan_kiri = femur_tibia_depan_kiri - femur_tibia_depan_berdiri

            base_coxa_belakang_kiri, coxa_femur_belakang_kiri, femur_tibia_belakang_kiri = IK_belakang(0,0, panjang_depan_belakang/2, self.roll, 0, geser)
            base_coxa_belakang_kiri = base_coxa_belakang_kiri - base_coxa_belakang_berdiri
            coxa_femur_belakang_kiri = coxa_femur_belakang_kiri - coxa_femur_belakang_berdiri
            femur_tibia_belakang_kiri = femur_tibia_belakang_kiri - femur_tibia_belakang_berdiri

            base_coxa_tengah_kanan, coxa_femur_tengah_kanan, femur_tibia_tengah_kanan = IK_tengah(0,0, 0, self.roll, -geser, 0)
            base_coxa_tengah_kanan = base_coxa_tengah_kanan - base_coxa_tengah_berdiri
            coxa_femur_tengah_kanan = coxa_femur_tengah_kanan - coxa_femur_tengah_berdiri
            femur_tibia_tengah_kanan = femur_tibia_tengah_kanan - femur_tibia_tengah_berdiri

            base_coxa_depan_kanan, coxa_femur_depan_kanan, femur_tibia_depan_kanan = IK_depan(0,0, panjang_depan_belakang/2, self.roll, -geser)
            base_coxa_depan_kanan = base_coxa_depan_kanan - base_coxa_depan_berdiri
            coxa_femur_depan_kanan = coxa_femur_depan_kanan - coxa_femur_depan_berdiri
            femur_tibia_depan_kanan = femur_tibia_depan_kanan - femur_tibia_depan_berdiri

            base_coxa_belakang_kanan, coxa_femur_belakang_kanan, femur_tibia_belakang_kanan = IK_belakang(0,0, panjang_depan_belakang/2, self.roll, 0, -geser)
            base_coxa_belakang_kanan = base_coxa_belakang_kanan - base_coxa_belakang_berdiri
            coxa_femur_belakang_kanan = coxa_femur_belakang_kanan - coxa_femur_belakang_berdiri
            femur_tibia_belakang_kanan = femur_tibia_belakang_kanan - femur_tibia_belakang_berdiri

            angle.data = [int(base_coxa_tengah_kiri), int(coxa_femur_tengah_kiri), int(femur_tibia_tengah_kiri), int(base_coxa_depan_kiri), int(coxa_femur_depan_kiri),int(femur_tibia_depan_kiri), int(base_coxa_belakang_kiri), int(coxa_femur_belakang_kiri), int(femur_tibia_belakang_kiri), int(base_coxa_tengah_kanan), int(coxa_femur_tengah_kanan), int(femur_tibia_tengah_kanan), int(base_coxa_depan_kanan), int(coxa_femur_depan_kanan), int(femur_tibia_depan_kanan), int(base_coxa_belakang_kanan), int(coxa_femur_belakang_kanan), int(femur_tibia_belakang_kanan), int(coxa_femur_tengah_berdiri+35), int(femur_tibia_tengah_berdiri-45), int(coxa_femur_depan_berdiri+35), int(femur_tibia_depan_berdiri-45), int(coxa_femur_belakang_berdiri+35), int(femur_tibia_belakang_berdiri-45), delay, message.data[0]]
            self.get_logger().info(f"Published: {angle.data}")
            self.get_logger().info("Strafe Left")
            self.publish_strafe_angle.publish(angle)

        if message.data[2] == 22:
            angle = Int32MultiArray()
            geser = 4
            base_coxa_tengah_kiri, coxa_femur_tengah_kiri, femur_tibia_tengah_kiri = IK_tengah(0,0, 0, 0, geser, 0)
            base_coxa_tengah_kiri = base_coxa_tengah_kiri - base_coxa_tengah_berdiri
            coxa_femur_tengah_kiri = coxa_femur_tengah_kiri - coxa_femur_tengah_berdiri
            femur_tibia_tengah_kiri = femur_tibia_tengah_kiri - femur_tibia_tengah_berdiri

            base_coxa_depan_kiri, coxa_femur_depan_kiri, femur_tibia_depan_kiri = IK_depan(0,0, panjang_depan_belakang/2, 0, geser)
            base_coxa_depan_kiri = base_coxa_depan_kiri - base_coxa_depan_berdiri
            coxa_femur_depan_kiri = coxa_femur_depan_kiri - coxa_femur_depan_berdiri
            femur_tibia_depan_kiri = femur_tibia_depan_kiri - femur_tibia_depan_berdiri

            base_coxa_belakang_kiri, coxa_femur_belakang_kiri, femur_tibia_belakang_kiri = IK_belakang(0,0, panjang_depan_belakang/2, 0, 0, geser)
            base_coxa_belakang_kiri = base_coxa_belakang_kiri - base_coxa_belakang_berdiri
            coxa_femur_belakang_kiri = coxa_femur_belakang_kiri - coxa_femur_belakang_berdiri
            femur_tibia_belakang_kiri = femur_tibia_belakang_kiri - femur_tibia_belakang_berdiri

            base_coxa_tengah_kanan, coxa_femur_tengah_kanan, femur_tibia_tengah_kanan = IK_tengah(0,0, 0, 0, -geser, 0)
            base_coxa_tengah_kanan = base_coxa_tengah_kanan - base_coxa_tengah_berdiri
            coxa_femur_tengah_kanan = coxa_femur_tengah_kanan - coxa_femur_tengah_berdiri
            femur_tibia_tengah_kanan = femur_tibia_tengah_kanan - femur_tibia_tengah_berdiri

            base_coxa_depan_kanan, coxa_femur_depan_kanan, femur_tibia_depan_kanan = IK_depan(0,0, panjang_depan_belakang/2, 0, -geser)
            base_coxa_depan_kanan = base_coxa_depan_kanan - base_coxa_depan_berdiri
            coxa_femur_depan_kanan = coxa_femur_depan_kanan - coxa_femur_depan_berdiri
            femur_tibia_depan_kanan = femur_tibia_depan_kanan - femur_tibia_depan_berdiri

            base_coxa_belakang_kanan, coxa_femur_belakang_kanan, femur_tibia_belakang_kanan = IK_belakang(0,0, panjang_depan_belakang/2, 0, 0, -geser)
            base_coxa_belakang_kanan = base_coxa_belakang_kanan - base_coxa_belakang_berdiri
            coxa_femur_belakang_kanan = coxa_femur_belakang_kanan - coxa_femur_belakang_berdiri
            femur_tibia_belakang_kanan = femur_tibia_belakang_kanan - femur_tibia_belakang_berdiri
            angle.data = [int(base_coxa_tengah_kiri), int(coxa_femur_tengah_kiri), int(femur_tibia_tengah_kiri), int(base_coxa_depan_kiri), int(coxa_femur_depan_kiri),int(femur_tibia_depan_kiri), int(base_coxa_belakang_kiri), int(coxa_femur_belakang_kiri), int(femur_tibia_belakang_kiri), int(base_coxa_tengah_kanan), int(coxa_femur_tengah_kanan), int(femur_tibia_tengah_kanan), int(base_coxa_depan_kanan), int(coxa_femur_depan_kanan), int(femur_tibia_depan_kanan), int(base_coxa_belakang_kanan), int(coxa_femur_belakang_kanan), int(femur_tibia_belakang_kanan), int(coxa_femur_tengah_berdiri+35), int(femur_tibia_tengah_berdiri-45), int(coxa_femur_depan_berdiri+35), int(femur_tibia_depan_berdiri-45), int(coxa_femur_belakang_berdiri+35), int(femur_tibia_belakang_berdiri-45), 3]
            self.get_logger().info("Strafe Right")
            self.publish_strafe_angle.publish(angle)

        if message.data[2] == 9 :
            angle = Int32MultiArray()
            angle.data = [90, int(coxa_femur_tengah_berdiri+35), int(femur_tibia_tengah_berdiri-45), 90, int(coxa_femur_depan_berdiri+35), int(femur_tibia_depan_berdiri-45), 90, int(coxa_femur_belakang_berdiri+35), int(femur_tibia_belakang_berdiri-45)]
            self.get_logger().info("Stop")
            self.get_logger().info(f"Published: {angle.data}")
            self.publish_stop_angle.publish(angle)

def main(args=None):
    rclpy.init(args=args)
    node = MyNode()
    rclpy.spin(node)
    rclpy.shutdown()
