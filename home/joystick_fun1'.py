import pygame
import time

pygame.init()
pygame.joystick.init()

if pygame.joystick.get_count() == 0:
    print("No joystick detected!")
    exit()

joystick = pygame.joystick.Joystick(0)
joystick.init()

print("Connected to:", joystick.get_name())
print("\nReading trigger & shoulder inputs...\n")

try:
    while True:
        pygame.event.pump()

        # Read buttons
        buttons = [joystick.get_button(i) for i in range(joystick.get_numbuttons())]

        # Read axes
        axes = [round(joystick.get_axis(i), 3) for i in range(joystick.get_numaxes())]

        # ===== BUTTONS =====
        if buttons[4] == 1:
            print("LB Pressed")

        if buttons[5] == 1:
            print("RB Pressed")

        if buttons[8] == 1:
            print("L3 Pressed")

        if buttons[9] == 1:
            print("R3 Pressed")

        # ===== TRIGGERS (AXES) =====
        # Adjust threshold to avoid noise
        if axes[2] > -0.9:   # LT
            print("LT Value:", axes[2])

        if axes[5] > -0.9:   # RT
            print("RT Value:", axes[5])

        time.sleep(0.1)

except KeyboardInterrupt:
    print("Stopped")
    pygame.quit()