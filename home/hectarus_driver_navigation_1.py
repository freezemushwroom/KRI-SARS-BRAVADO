#!/usr/bin/env python3

import threading

import rclpy
from rclpy.node import Node

from std_msgs.msg import Float32MultiArray
from std_msgs.msg import Bool

import pygame
import time
import sys
import threading
import RPi.GPIO as GPIO
from time import sleep
from adafruit_servokit import ServoKit
import math

waktu_sleep = 0.2
movement_counter = 0


kit1 = ServoKit(channels = 16, address = 0x41) #, reference_clock_speed = 24930632)
kit2 = ServoKit(channels = 16, address = 0x40) #, reference_clock_speed = 25220628)

for i in range (10):
    kit1.servo[i].set_pulse_width_range(320, 2320)
    kit2.servo[15-i].set_pulse_width_range(400, 2400)

coxa = 2.55
femur = 6.508
tibia = 7.964

def lebar(l):
    maju = 0
    alpha1 = math.asin(l/femur)
    h = math.sqrt(math.pow(femur,2)+math.pow(tibia,2)-(2*femur*tibia*math.cos(alpha1))-(math.sin(alpha1)*math.sin(alpha1)*femur*femur))
    P = math.sqrt(math.pow(maju,2)+math.pow((l+coxa),2)) #panjang diagonal setelah kaki maju
    P = P-coxa
    M = math.sqrt(math.pow(h,2)+math.pow(P,2)) #panjang garis miring antara femur tibia
    sudut_coxa_femur_1_tengah = math.degrees(math.acos((math.pow(femur,2)+math.pow(M,2)-math.pow(tibia,2))/(2*femur*M)))
    sudut_coxa_femur_2_tengah = math.degrees(math.acos((math.pow(M,2)+math.pow(h,2)-math.pow(P,2))/(2*h*M)))
    sudut_coxa_femur_total = sudut_coxa_femur_1_tengah + sudut_coxa_femur_2_tengah
    #print("Besar Sudut Coxa Femur Total : " + str(sudut_coxa_femur_total) + " derajat")
    return sudut_coxa_femur_total
flag = 0


# ================= LED =================
LED_PIN = 17 # GPIO017
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(17, GPIO.OUT)

# ================= THREAD CONTROL =================
stop_event = threading.Event()
current_thread = None
current_action = None

# ===========================================================
# Import your gait functions here
# ===========================================================

# from robot_gait import (
#     maju,
#     putar_kiri,
#     putar_kanan,
#     jalan_kiri_miring,
#     jalan_kanan_miring,
#     tetrapod_maju,
# )

# Temporary dummy functions
def maju():
    #loop_print("maju")
    while not stop_event.is_set():
        #femur 1 3 5 ngangkat
        kit1.servo[7].angle = 180 #femur1
        kit1.servo[1].angle = 180 #femur3
        kit2.servo[11].angle = 0 #femur5
        print("Femur 1 3 5 Ngangkat")
        sleep(waktu_sleep)

        #coxa 1 3 5 maju
        kit1.servo[8].angle = 120 #coxa1
        kit1.servo[2].angle = 120 #coxa3
        kit2.servo[10].angle = 60 #coxa5
        print("Coxa 1 3 5 Maju M")
        sleep(waktu_sleep)
        

        #femur 1 3 5 turun dan tibia turun sekalian adjust ngambil kaki
        for i in range (10, 50, 5):
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

        #coxa 2 4 6 maju
        kit1.servo[5].angle = 120 #coxa2
        kit2.servo[13].angle = 60 #coxa4
        kit2.servo[7].angle = 60 #coxa6
        print("Coxa 2 4 6 Maju M")
        sleep(waktu_sleep)

        #femur 2 4 6 turun dan tibia turun sekalian adjust ngambil kaki
        for i in range (10, 50, 5):
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
        
        time.sleep(0.25)
        print(f"stopped maju")
        break

def putar_kiri(): 
    #loop_print("muter kiri")
    while not stop_event.is_set():
        #femur 1 3 5 ngangkat
        kit1.servo[7].angle = 180 #femur1
        kit1.servo[1].angle = 180 #femur3
        kit2.servo[11].angle = 0 #femur5
        print("Femur 1 3 5 Ngangkat")
        sleep(waktu_sleep)

        #coxa 1 3 mundur 5 maju
        kit1.servo[8].angle = 60 #coxa1
        kit1.servo[2].angle = 60 #coxa3
        kit2.servo[10].angle = 60 #coxa5
        print("Coxa 1 3 Mundur 5 Maju PKR")
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
        print("Coxa 2 Mundur Coxa 4 6 Maju PKR")
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
        
        time.sleep(0.25)
        print(f"stopped putar kiri")
        break

def putar_kanan(): 
    #loop_print("muter kanan")
    while not stop_event.is_set():
        #femur 1 3 5 ngangkat
        kit1.servo[7].angle = 180 #femur1
        kit1.servo[1].angle = 180 #femur3
        kit2.servo[11].angle = 0 #femur5
        print("Femur 1 3 5 Ngangkat")
        sleep(waktu_sleep)

        #coxa 1 3 5 maju
        kit1.servo[8].angle = 120 #coxa1
        kit1.servo[2].angle = 120 #coxa3
        kit2.servo[10].angle = 120 #coxa5
        print("Coxa 1 3 Maju 5 Mundur")
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

        #coxa 2 4 6 maju
        kit1.servo[5].angle = 120 #coxa2
        kit2.servo[13].angle = 120 #coxa4
        kit2.servo[7].angle = 120 #coxa6
        print("Coxa 2 Maju Coxa 4 6 Mundur")
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
        
        time.sleep(0.25)
        print(f"stopped putar kanan")
        break


def jalan_kiri_miring(): 
    #loop_print("miring kiri")
    while not stop_event.is_set():
        for i in range (9):
            kit1.servo[i].set_pulse_width_range(320, 2320)
            kit2.servo[15-i].set_pulse_width_range(400, 2400)


        coxa = 2.644
        femur = 6.436
        tibia = 8.122
        l = 6.436
        maju = 3.8
        forward = maju
        gait = 2
        #0 tripod, 1 wave, 2 tetrapod
        geser = -4
        roll = -6
        mundur = 0

        delay = 0.4

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
            P = math.sqrt(math.pow(maju,2)+math.pow((l+coxa),2)-(2*maju*(l+coxa)*math.cos(math.radians(90-(yaw)-30)))) #panjang diagonal setelah kaki maju
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
            PB = math.sqrt(math.pow(maju,2)+math.pow((l+coxa),2)-(2*maju*(l+coxa)*math.cos(math.radians(90-30-mundur-45-(yaw)))))
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

        base_coxa_tengah_berdiri, coxa_femur_tengah_berdiri, femur_tibia_tengah_berdiri = IK_tengah(0, 0, 0, roll, 0, 0)
        base_coxa_depan_berdiri, coxa_femur_depan_berdiri, femur_tibia_depan_berdiri = IK_depan(0,0, panjang_depan_belakang/2, roll, 0)
        base_coxa_belakang_berdiri, coxa_femur_belakang_berdiri, femur_tibia_belakang_berdiri = IK_belakang(0,0, panjang_depan_belakang/2, roll, mundur, 0)

        base_coxa_tengah_kiri, coxa_femur_tengah_kiri, femur_tibia_tengah_kiri = IK_tengah(0, 0, 0, 0, geser,0)
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

        base_coxa_tengah_kanan, coxa_femur_tengah_kanan, femur_tibia_tengah_kanan = IK_tengah(0,0,0, 0, -geser, 0)
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


        data = [int(base_coxa_tengah_kiri), int(coxa_femur_tengah_kiri), int(femur_tibia_tengah_kiri), int(base_coxa_depan_kiri), int(coxa_femur_depan_kiri),int(femur_tibia_depan_kiri), int(base_coxa_belakang_kiri), int(coxa_femur_belakang_kiri), int(femur_tibia_belakang_kiri), int(base_coxa_tengah_kanan), int(coxa_femur_tengah_kanan), int(femur_tibia_tengah_kanan), int(base_coxa_depan_kanan), int(coxa_femur_depan_kanan), int(femur_tibia_depan_kanan), int(base_coxa_belakang_kanan), int(coxa_femur_belakang_kanan), int(femur_tibia_belakang_kanan), int(coxa_femur_tengah_berdiri+35), int(femur_tibia_tengah_berdiri-45), int(coxa_femur_depan_berdiri+35), int(femur_tibia_depan_berdiri-45), int(coxa_femur_belakang_berdiri+35), int(femur_tibia_belakang_berdiri-45), 0]

        #femur angkat
        kit1.servo[7].angle = max(0, min((data[11+9] + 30), 180)) #femur1
        kit1.servo[6].angle = max(0, min((180 - data[12+9] + 30), 180)) #tibia1
        kit1.servo[1].angle = max(0, min((data[13+9] + 30), 180)) #femur3
        kit1.servo[0].angle = max(0, min((180 - data[14+9] + 30), 180)) #tibia3
        kit2.servo[11].angle = max(0, min((180 - data[9+9] - 30), 180)) #femur5
#        kit2.servo[12].angle = max(0, min((data[10+9] - 30), 180)) #tibia5
        wait(delay)

        #femur 1 3 5 turun dan tibia turun sekalian adjust ngambil kaki
        kit1.servo[6].angle = max(0, min((180 - data[12+9] - data[5]), 180)) #tibia1
        kit1.servo[0].angle = max(0, min((180 - data[14+9] - data[8]), 180)) #tibia3
        kit2.servo[12].angle = 0 #max(0, min((data[10+9] + data[2+9] - 10), 180)) #tibia5
        wait(0.3)
        kit1.servo[7].angle = max(0, min((data[11+9] + data[4]), 180)) #femur1
        kit1.servo[1].angle = max(0, min((data[13+9] + data[7]), 180)) #femur3
        kit2.servo[11].angle = max(0, min((180 - data[9+9]- data[1+9]), 180)) #femur5

        wait(delay)

        # femur tibia 1 3 5 balik ke posisi awal
        kit1.servo[7].angle = data[11+9] #femur1
        kit1.servo[6].angle = 180 - data[12+9] #tibia1

        kit1.servo[1].angle = data[13+9] #femur3
        kit1.servo[0].angle = 180 - data[14+9] #tibia3

        kit2.servo[11].angle = 180 - data[9+9] #femur5
        kit2.servo[12].angle = data[10+9] #tibia5

        wait(0.02)

        kit1.servo[4].angle = max(0, min((data[9+9] + 30), 180)) #femur2
        kit1.servo[3].angle = max(0, min((180 - data[10+9] + 30), 180)) #tibia2
        kit2.servo[14].angle = max(0, min((180 - data[13+9] - 30), 180)) #femur4
#        kit2.servo[15].angle = max(0, min((data[14+9] - 30), 180)) #tibia4
        kit2.servo[8].angle = max(0, min((180 - data[11+9] - 30), 180)) #femur6
#        kit2.servo[9].angle =  max(0, min((data[12+9] - 30), 180)) #tibia6
        wait(delay)

        #femur 2 4 6 turun dan tibia turun sekalian adjust ngambil kaki
        kit1.servo[3].angle = max(0, min((180 - data[10+9] - data[2]), 180)) #tibia2
        kit2.servo[15].angle = max(0, min((data[14+9] + data[8+9] - 10), 180)) #tibia4
        kit2.servo[9].angle = max(0, min((data[12+9] + data[5+9] - 10), 180)) #tibia6
        wait(0.3)
        kit1.servo[4].angle = max(0, min((data[9+9] + data[1]), 180)) #femur2
        kit2.servo[14].angle = max(0, min((180 - data[13+9] - data[7+9]), 180)) #femur4
        kit2.servo[8].angle = max(0, min((180 - data[11+9] - data[4+9]), 180)) #femur6
        wait(delay)

        #femur tibia 2 4 6 balik ke poisi awal
        kit1.servo[4].angle = data[9+9] #femur2
        kit1.servo[3].angle = 180 -data[10+9] #tibia2

        kit2.servo[14].angle = 180 - data[13+9] #femur4
        kit2.servo[15].angle = data[14+9] #tibia4

        kit2.servo[8].angle = 180 - data[11+9] #femur6
        kit2.servo[9].angle = data[12+9] #tibia6
        time.sleep(0.25)
        print(f"stopped strafe kiri")
        break

# hati hati ini masih belum strafe kanan
def jalan_kanan_miring(): #PR perlu buat versi strafe kanan
    #loop_print("miring kanan")
    while not stop_event.is_set():
        for i in range (9):
            kit1.servo[i].set_pulse_width_range(320, 2320)
            kit2.servo[15-i].set_pulse_width_range(400, 2400)


        coxa = 2.644
        femur = 6.436
        tibia = 8.122
        l = 6.436
        maju = 3.8
        forward = maju
        gait = 2
        #0 tripod, 1 wave, 2 tetrapod
        geser = 4 # kalo ini positif jadi ke kanan katanya
        roll = -6
        mundur = 0

        delay = 0.4

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
            P = math.sqrt(math.pow(maju,2)+math.pow((l+coxa),2)-(2*maju*(l+coxa)*math.cos(math.radians(90-(yaw)-30)))) #panjang diagonal setelah kaki maju
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
            PB = math.sqrt(math.pow(maju,2)+math.pow((l+coxa),2)-(2*maju*(l+coxa)*math.cos(math.radians(90-30-mundur-45-(yaw)))))
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

        base_coxa_tengah_berdiri, coxa_femur_tengah_berdiri, femur_tibia_tengah_berdiri = IK_tengah(0, 0, 0, roll, 0, 0)
        base_coxa_depan_berdiri, coxa_femur_depan_berdiri, femur_tibia_depan_berdiri = IK_depan(0,0, panjang_depan_belakang/2, roll, 0)
        base_coxa_belakang_berdiri, coxa_femur_belakang_berdiri, femur_tibia_belakang_berdiri = IK_belakang(0,0, panjang_depan_belakang/2, roll, mundur, 0)

        base_coxa_tengah_kiri, coxa_femur_tengah_kiri, femur_tibia_tengah_kiri = IK_tengah(0, 0, 0, 0, geser,0)
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

        base_coxa_tengah_kanan, coxa_femur_tengah_kanan, femur_tibia_tengah_kanan = IK_tengah(0,0,0, 0, -geser, 0)
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


        data = [int(base_coxa_tengah_kiri), int(coxa_femur_tengah_kiri), int(femur_tibia_tengah_kiri), int(base_coxa_depan_kiri), int(coxa_femur_depan_kiri),int(femur_tibia_depan_kiri), int(base_coxa_belakang_kiri), int(coxa_femur_belakang_kiri), int(femur_tibia_belakang_kiri), int(base_coxa_tengah_kanan), int(coxa_femur_tengah_kanan), int(femur_tibia_tengah_kanan), int(base_coxa_depan_kanan), int(coxa_femur_depan_kanan), int(femur_tibia_depan_kanan), int(base_coxa_belakang_kanan), int(coxa_femur_belakang_kanan), int(femur_tibia_belakang_kanan), int(coxa_femur_tengah_berdiri+35), int(femur_tibia_tengah_berdiri-45), int(coxa_femur_depan_berdiri+35), int(femur_tibia_depan_berdiri-45), int(coxa_femur_belakang_berdiri+35), int(femur_tibia_belakang_berdiri-45), 0]

        #femur angkat
        # Leg 1
        kit1.servo[7].angle = max(0, min((data[11+9] + 30), 180)) #femur1
        kit1.servo[6].angle = max(0, min((180 - data[12+9] + 30), 180)) #tibia1
        kit1.servo[1].angle = max(0, min((data[13+9] + 30), 180)) #femur3
        kit1.servo[0].angle = max(0, min((180 - data[14+9] + 30), 180)) #tibia3
        kit2.servo[11].angle = max(0, min((180 - data[9+9] - 30), 180)) #femur5
#        kit2.servo[12].angle = max(0, min((data[10+9] - 30), 180)) #tibia5
        wait(delay)

        #femur 1 3 5 turun dan tibia turun sekalian adjust ngambil kaki
        # Leg 1
        kit1.servo[6].angle = 0  - data[5]
        kit1.servo[7].angle = data[11+9] + data[4]

        # Leg 3
        kit1.servo[0].angle = 0  - data[8]
        kit1.servo[1].angle = data[13+9] + data[7]

        # Leg 5
        kit2.servo[12].angle = 90
        kit2.servo[11].angle = 180 - data[9+9] - data[1+9]
        wait(delay)

        # femur tibia 1 3 5 balik ke posisi awal
        kit1.servo[7].angle = data[11+9] #femur1
        kit1.servo[6].angle = 180 - data[12+9] #tibia1

        kit1.servo[1].angle = data[13+9] #femur3
        kit1.servo[0].angle = 180 - data[14+9] #tibia3

        kit2.servo[11].angle = 180 - data[9+9] #femur5
        kit2.servo[12].angle = 90 - data[14+9] - data[8] #tibia5

        wait(0.02)

        kit1.servo[4].angle = max(0, min((data[9+9] + 30), 180)) #femur2
        kit1.servo[3].angle = max(0, min((180 - data[10+9] + 30), 180)) #tibia2
        kit2.servo[14].angle = max(0, min((180 - data[13+9] - 30), 180)) #femur4
#        kit2.servo[15].angle = max(0, min((data[14+9] - 30), 180)) #tibia4
        kit2.servo[8].angle = max(0, min((180 - data[11+9] - 30), 180)) #femur6
#        kit2.servo[9].angle =  max(0, min((data[12+9] - 30), 180)) #tibia6
        wait(delay)

        #femur 2 4 6 turun dan tibia turun sekalian adjust ngambil kaki
        #kit1.servo[3].angle = max(0, min((180 - data[10+9] - data[2]), 180)) #tibia2
        kit2.servo[15].angle = max(0, min((data[14+9] + data[8+9] - 10), 180)) #tibia4
        kit2.servo[9].angle = max(0, min((data[12+9] + data[5+9] - 10), 180)) #tibia6
        # Leg 2
        #kit1.servo[3].angle = 180 - data[10+9] + data[2]
        kit1.servo[3].angle = 180 - data[10+9] - data[2]
        
        
        wait(0.3)
        #kit1.servo[4].angle = max(0, min((data[9+9] + data[1]), 180)) #femur2
        kit2.servo[14].angle = max(0, min((180 - data[13+9] - data[7+9]), 180)) #femur4
        kit2.servo[8].angle = max(0, min((180 - data[11+9] - data[4+9]), 180)) #femur6
        #kit1.servo[4].angle = data[9+9] - data[1]
        kit1.servo[4].angle = data[9+9] + data[1]
        wait(delay)

        #femur tibia 2 4 6 balik ke poisi awal
        kit1.servo[4].angle = data[9+9] #femur2
        kit1.servo[3].angle = 180 -data[10+9] #tibia2

        kit2.servo[14].angle = 180 - data[13+9] #femur4
        kit2.servo[15].angle = data[14+9] #tibia4

        kit2.servo[8].angle = 180 - data[11+9] #femur6
        kit2.servo[9].angle = data[12+9] #tibia6
        time.sleep(0.25)
        print(f"stopped strafe kanan")
        break


def tetrapod_maju():
    print("Tetrapod Forward")

def langsungBerdiri():
    for i in range (10):
        kit1.servo[i].set_pulse_width_range(320, 2320)
        kit2.servo[15-i].set_pulse_width_range(400, 2400)

    coxa = 2.55
    femur = 6.508
    tibia = 7.964

    def lebar(l):
        maju = 0
        alpha1 = math.asin(l/femur)
        h = math.sqrt(math.pow(femur,2)+math.pow(tibia,2)-(2*femur*tibia*math.cos(alpha1))-(math.sin(alpha1)*math.sin(alpha1)*femur*femur))
        P = math.sqrt(math.pow(maju,2)+math.pow((l+coxa),2)) #panjang diagonal setelah kaki maju
        P = P-coxa
        M = math.sqrt(math.pow(h,2)+math.pow(P,2)) #panjang garis miring antara femur tibia
        sudut_coxa_femur_1_tengah = math.degrees(math.acos((math.pow(femur,2)+math.pow(M,2)-math.pow(tibia,2))/(2*femur*M)))
        sudut_coxa_femur_2_tengah = math.degrees(math.acos((math.pow(M,2)+math.pow(h,2)-math.pow(P,2))/(2*h*M)))
        sudut_coxa_femur_total = sudut_coxa_femur_1_tengah + sudut_coxa_femur_2_tengah
        #print("Besar Sudut Coxa Femur Total : " + str(sudut_coxa_femur_total) + " derajat")
        return sudut_coxa_femur_total
    flag = 0

    #ini perlu atur dulu kayak gimana selebhinya aman
    if flag == 0:
        sudut = lebar(6.508) #3.776
        flag = 1
    elif flag == 1:
        sudut = lebar(6.508) #6
        flag = 2
    elif flag == 2:
        sudut = lebar(6.508) #6.582
        flag = 0
    #sudut = lebar(4.66) # 3.776 - 4.66 - 6.582
    sudutt = sudut + 45
    if sudutt > 180:
        sudutt = 135
    else:
        sudutt = sudut

    suduttt = (180-sudut)-45
    if suduttt < 0:
        suduttt = 135
    else:
        suduttt = sudut

    print("Sudut Femur 1 2 3 : " + str(sudut + 35))
    print("Sudut Femur 4 5 6 : " + str((180-sudut) - 35))
    print("Sudut Tibia 1 2 3 : " + str(sudutt + 45))
    print("Sudut Tibia 4 5 6 : " + str((180-suduttt) - 45))

    kit1.servo[8].angle = 90 #coxa1
    kit2.servo[7].angle = 90 #coxa6
    kit1.servo[5].angle = 90 #coxa2
    kit2.servo[10].angle = 90 #coxa5
    kit1.servo[2].angle = 90 #coxa3
    kit2.servo[13].angle = 90 #coxa4

    kit1.servo[7].angle = sudut + 35 #femur1 125
    kit2.servo[8].angle = (180-sudut) - 35 #femur6 55
    kit1.servo[4].angle = sudut + 35 #femur2 125 
    kit2.servo[11].angle = (180-sudut) - 35 #femur5 55
    kit1.servo[1].angle = sudut + 35 #femur3 125 
    kit2.servo[14].angle = (180-sudut) - 35 #femur4 55

    kit1.servo[6].angle = (sudutt) + 45 #tibia1 135
    kit2.servo[9].angle = (180-suduttt) - 45 #tibia6 45
    kit1.servo[3].angle = (sudutt) + 45 #tibia2 135
    kit2.servo[12].angle = (180-suduttt) - 45 #tibia5 45
    kit1.servo[0].angle = (sudutt) + 45 #tibia3 135
    kit2.servo[15].angle = (180-suduttt) - 45 #tibia4 45
    sleep(0.2)


class MovementExecutor(Node):

    def __init__(self):

        super().__init__("movement_executor")

        self.busy = False
        self.tetrapod_mode = False

        self.create_subscription(
            Float32MultiArray,
            "/cmd_movement",
            self.cmd_callback,
            1
        )

        self.create_subscription(
            Bool,
            "/move_tetrapod",
            self.tetrapod_callback,
            1
        )

        self.pub_state = self.create_publisher(
            Bool,
            "/movement_state",
            1
        )

        self.get_logger().info("Movement Executor Started")

    def tetrapod_callback(self, msg):
        self.tetrapod_mode = msg.data

    def publish_state(self, moving):

        msg = Bool()
        msg.data = moving
        self.pub_state.publish(msg)

    def cmd_callback(self, msg):
        global movement_counter

        if self.busy:
            self.get_logger().warn("Robot is busy.")
            return

        if len(msg.data) < 3:
            return

        movement_counter = movement_counter + 1
        self.get_logger().info(f"New data in({movement_counter}) ")

        self.busy = True
        self.publish_state(True)

        forward = msg.data[0]
        strafe = msg.data[1]
        rotate = msg.data[2]

        try:

            # ==========================
            # Forward
            # ==========================

            if forward > 0:

                if self.tetrapod_mode:

                    self.get_logger().info("Tetrapod Forward")
                    tetrapod_maju()

                else:

                    self.get_logger().info("Forward")
                    maju()

            # ==========================
            # Turn Left
            # ==========================

            elif rotate > 0:

                self.get_logger().info("Turn Left")
                putar_kiri()

            # ==========================
            # Turn Right
            # ==========================

            elif rotate < 0:

                self.get_logger().info("Turn Right")
                putar_kanan()

            # ==========================
            # Strafe Left
            # ==========================

            elif strafe < 0:

                self.get_logger().info("Strafe Left")
                jalan_kiri_miring()

            # ==========================
            # Strafe Right
            # ==========================

            elif strafe > 0:

                self.get_logger().info("Strafe Right")
                jalan_kanan_miring()

            else:

                self.get_logger().info("Stop / No movement")
                langsungBerdiri()

            forward = 0.0
            strafe = 0.0
            rotate = 0.0
            langsungBerdiri()

        finally:

            self.publish_state(False)
            self.busy = False


def main(args=None):

    rclpy.init(args=args)

    node = MovementExecutor()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()