import pygame
import time
import sys
import threading
import RPi.GPIO as GPIO

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


def maju(): loop_print("maju")
def mundur(): loop_print("mundur")
def jalan_kiri_miring(): loop_print("miring kiri")
def jalan_kanan_miring(): loop_print("miring kanan")
def berdiri(): loop_print("berdiri")
def stop(): print("stop")
def tambah_speed(): loop_print("tambah speed")
def kurang_speed(): loop_print("kurang speed")
def muter_kiri(): loop_print("muter kiri")
def muter_kanan(): loop_print("muter kanan")


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
        if len(buttons) > 0 and buttons[1] == 1:
            start_action(berdiri, "berdiri")

        elif len(buttons) > 1 and buttons[2] == 1:
            start_action(stop, "stop")

        # ---- D-PAD ----
        elif hats[1] == 1:
            start_action(maju, "maju")

        elif hats[1] == -1:
            start_action(mundur, "mundur")

        elif hats[0] == -1:
            start_action(jalan_kiri_miring, "kiri")

        elif hats[0] == 1:
            start_action(jalan_kanan_miring, "kanan")

        # ---- BUTTON ACTIONS ----
        elif len(buttons) > 2 and buttons[0] == 1:
            start_action(tambah_speed, "tambah")

        elif len(buttons) > 3 and buttons[3] == 1:
            start_action(kurang_speed, "kurang")

        elif len(buttons) > 4 and buttons[4] == 1:
            start_action(muter_kiri, "muter_kiri")

        elif len(buttons) > 5 and buttons[5] == 1:
            start_action(muter_kanan, "muter_kanan")
        
        elif buttons[8] == 1:
            GPIO.output(17, GPIO.HIGH)
        
        elif buttons[9] == 1:
            GPIO.output(17, GPIO.LOW)
        
        elif buttons[10] == 1:
            break

        elif buttons[11] == 1:
            break

        time.sleep(0.05)
        #GPIO.cleanup()

except KeyboardInterrupt:
    stop_event.set()
    if current_thread:
        current_thread.join()
    print("\nStopped")
    pygame.quit()