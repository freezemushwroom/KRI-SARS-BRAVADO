import pygame
import time
import sys
import threading
import RPi.GPIO as GPIO
from time import sleep
from adafruit_servokit import ServoKit
import math

waktu_sleep = 0.2


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


# ================= ACTION FUNCTIONS =================
def loop_print(text):
    print(f"{text} started")
    while not stop_event.is_set():
        print(text)
        time.sleep(0.25)
    print(f"{text} stopped")


def maju(): 
    #loop_print("maju")
    while not stop_event.is_set():
        #coxa 1 3 5 maju
        kit1.servo[8].angle = 120 #coxa1
        kit1.servo[2].angle = 120 #coxa3
        kit2.servo[10].angle = 60 #coxa5
        print("Coxa 1 3 5 Maju")
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
        print("Coxa 2 4 6 Maju")
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
        #femur 1 3 5 ngangkat
        kit1.servo[7].angle = 180 #femur1
        kit1.servo[1].angle = 180 #femur3
        kit2.servo[11].angle = 0 #femur5
        print("Femur 1 3 5 Ngangkat")
        sleep(waktu_sleep)
        time.sleep(0.25)
        print(f"stopped")

def mundur(): 
    #loop_print("mundur")
    while not stop_event.is_set():
        #print(text)
        time.sleep(0.25)
        print(f"stopped")

def jalan_kiri_miring(): 
    #loop_print("miring kiri")
    while not stop_event.is_set():
        #print(text)
        time.sleep(0.25)
        print(f"stopped")

def jalan_kanan_miring(): 
    #loop_print("miring kanan")
    while not stop_event.is_set():
        #print(text)
        time.sleep(0.25)
        print(f"stopped")

def berdiri(): 
    #loop_print("berdiri")
    while not stop_event.is_set():
        langsungBerdiri()   
        time.sleep(0.25)
        print(f"stopped")

def stop(): 
    langsungBerdiri()
    print("stop")

def tambah_speed(): 
    waktu_sleep = waktu_sleep - 0.1
    loop_print("tambah speed")

def kurang_speed(): 
    waktu_sleep = waktu_sleep + 0.1
    loop_print("kurang speed")

def muter_kiri(): 
    #loop_print("muter kiri")
    while not stop_event.is_set():
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
        time.sleep(0.25)
        print(f"stopped")

def muter_kanan(): 
    #loop_print("muter kanan")
    while not stop_event.is_set():
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
        #femur 1 3 5 ngangkat
        kit1.servo[7].angle = 180 #femur1
        kit1.servo[1].angle = 180 #femur3
        kit2.servo[11].angle = 0 #femur5
        print("Femur 1 3 5 Ngangkat")
        sleep(waktu_sleep)
        time.sleep(0.25)
        print(f"stopped")

def langsungBerdiri():
    ''' #ini perlu atur dulu kayak gimana selebhinya aman
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
'''
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
    sleep(3)

# ================= START / STOP HANDLER =================
def start_action(func, name):
    global current_thread, current_action

    # If same action already running → ignore
    if current_action == name:
        return

    # Stop previous thread
    stop_event.set()
    if current_thread is not None:
        current_thread.join()

    # Reset event
    stop_event.clear()

    # Start new thread
    current_action = name
    current_thread = threading.Thread(target=func)
    current_thread.start()


# ================= PYGAME INIT =================
pygame.init()
pygame.joystick.init()

if pygame.joystick.get_count() == 0:
    print("No joystick detected!")
    exit()

joystick = pygame.joystick.Joystick(0)
joystick.init()

print("Connected to:", joystick.get_name())
print("\nLive Controller Monitor (Ctrl+C to stop)\n")

# ================= MAIN LOOP =================
try:
    while True:
        pygame.event.pump()

        # ---- AXES ----
        axes = [round(joystick.get_axis(i), 2) for i in range(joystick.get_numaxes())]

        # ---- BUTTONS ----
        buttons = [joystick.get_button(i) for i in range(joystick.get_numbuttons())]

        # ---- HATS ----
        hats = joystick.get_hat(0) if joystick.get_numhats() > 0 else (0, 0)

        # ---- LIVE MONITOR ----
        output = (
            f"Axes: {axes} | "
            f"Buttons: {buttons} | "
            f"D-pad: {hats}"
        )
        #sys.stdout.write("\r" + output)
        #sys.std
        # ================= CONTROL LOGIC =================

        # ---- PRIORITY OVERRIDE ----
        if len(buttons) > 0 and buttons[1] == 1: #A
            start_action(berdiri, "berdiri")

        elif len(buttons) > 1 and buttons[2] == 1: #B
            start_action(stop, "stop")

        # ---- D-PAD ----
        elif hats[1] == 1: #panah atas
            start_action(maju, "maju")

        elif hats[1] == -1: #panah bawah
            start_action(mundur, "mundur")

        elif hats[0] == -1: #panah kiri
            start_action(jalan_kiri_miring, "kiri")

        elif hats[0] == 1: #panah kanan
            start_action(jalan_kanan_miring, "kanan")

        # ---- BUTTON ACTIONS ----
        elif len(buttons) > 2 and buttons[0] == 1: #X
            start_action(tambah_speed, "tambah")

        elif len(buttons) > 3 and buttons[3] == 1: #Y
            start_action(kurang_speed, "kurang")

        elif len(buttons) > 4 and buttons[4] == 1: #Lb
            start_action(muter_kiri, "muter_kiri")

        elif len(buttons) > 5 and buttons[5] == 1: #Rb
            start_action(muter_kanan, "muter_kanan")
        
        elif buttons[8] == 1: #back
            GPIO.output(17, GPIO.HIGH)
            print("LED On")
        
        elif buttons[9] == 1: #start
            GPIO.output(17, GPIO.LOW)
            print("LED Off")

        
        elif buttons[10] == 1:
            break #R3 kiri
        elif buttons[11] == 1:
            break #R3 kanan

        time.sleep(0.05)
        #GPIO.cleanup()

except KeyboardInterrupt:
    stop_event.set()
    if current_thread:
        current_thread.join()
    print("\nStopped")
    pygame.quit()