import pygame
import time
import sys

pygame.init()
pygame.joystick.init()

if pygame.joystick.get_count() == 0:
    print("No joystick detected!")
    exit()

joystick = pygame.joystick.Joystick(0)
joystick.init()

print("Connected to:", joystick.get_name())
print("\nLive Controller Monitor (Ctrl+C to stop)\n")

try:
    while True:
        pygame.event.pump()

        # ---- AXES ----
        axes = [round(joystick.get_axis(i), 2) for i in range(joystick.get_numaxes())]

        # ---- BUTTONS ----
        buttons = [joystick.get_button(i) for i in range(joystick.get_numbuttons())]

        # ---- HATS ----
        hats = joystick.get_hat(0) if joystick.get_numhats() > 0 else (0, 0)

        # ---- SAFE INDEXING ----
        LB  = buttons[4] if len(buttons) > 4 else 0
        RB  = buttons[5] if len(buttons) > 5 else 0
        L3  = buttons[8] if len(buttons) > 8 else 0
        R3  = buttons[9] if len(buttons) > 9 else 0

        LT = (axes[2] + 1) / 2 if len(axes) > 2 else 0
        RT = (axes[5] + 1) / 2 if len(axes) > 5 else 0

        # ---- SINGLE LINE OUTPUT ----
        output = (
            f"Axes: {axes} | "
            f"Buttons: {buttons} | "
            f"D-pad: {hats} | "
            f"LB:{LB} RB:{RB} L3:{L3} R3:{R3} | "
            f"LT:{LT:.2f} RT:{RT:.2f}"
        )

        sys.stdout.write("\r" + output)
        sys.stdout.flush()

        time.sleep(0.05)

except KeyboardInterrupt:
    print("\nStopped")
    pygame.quit()