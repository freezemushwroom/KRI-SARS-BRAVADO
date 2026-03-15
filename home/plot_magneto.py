import sys
sys.path.append('../../')
import time
from DFRobot_BMX160 import BMX160
import math
import numpy as np
import matplotlib.pyplot as plt
from numpy.linalg import inv

bmx = BMX160(1)

while not bmx.begin():
    time.sleep(2)
mag_data = []

print("Rotate sensor in all directions (figure-8). Collecting data...")

while True: #for _ in range(1000):
    try:
        user input = input("Colecting Data, Enter to stop")
        if user_input == "":
            print("Stop Collecting Data")
            break
        data = bmx.get_all_data()
        mag = [data[0], data[1], data[2]]  # Should return a list or tuple of 3 values
        mag_data.append(mag)
    except Exception as e:
        print(f"Error reading magnetometer: {e}")
    time.sleep(0.01)  # Adjust sample rate (100 Hz)

mag_data = np.array(mag_data)  # Use your collected magnetometer data

# Design matrix D (ellipsoid form)
x, y, z = mag_data[:, 0], mag_data[:, 1], mag_data[:, 2]
D = np.vstack([x*x, y*y, z*z, 2*x*y, 2*x*z, 2*y*z, 2*x, 2*y, 2*z, np.ones(len(x))]).T

# Solve normal system of equations
S = np.dot(D.T, D)
_, v = np.linalg.eig(S)
v = v[:, np.argmin(np.abs(np.sum(v, axis=0)))]  # smallest eigenvalue

# Coefficients of ellipsoid equation
A = np.array([
    [v[0], v[3], v[4], v[6]],
    [v[3], v[1], v[5], v[7]],
    [v[4], v[5], v[2], v[8]],
    [v[6], v[7], v[8], v[9]]
])

# Find center of ellipsoid
A3 = A[0:3, 0:3]
bv = -v[6:9]
center = np.dot(inv(A3), bv)

# Shift data
shifted = mag_data - center

# Compute soft iron correction
evals, evecs = np.linalg.eig(np.dot(shifted.T, shifted) / shifted.shape[0])
scale = np.sqrt(1.0 / evals)
transform = np.dot(evecs, np.diag(scale)).dot(evecs.T)

# Apply calibration
calibrated = (shifted).dot(transform.T)

# ------------- Plot Before and After -------------
fig = plt.figure(figsize=(12, 5))

print(center)
print(transform)
print(calibrated)

# Raw
ax1 = fig.add_subplot(121, projection='3d')
ax1.scatter(mag_data[:, 0], mag_data[:, 1], mag_data[:, 2], s=1)
ax1.set_title('Raw Magnetometer Data')
sdasdax1.set_xlabel('X'); ax1.set_ylabel('Y'); ax1.set_zlabel('Z')

# Calibrated
ax2 = fig.add_subplot(122, projection='3d')
ax2.scatter(calibrated[:, 0], calibrated[:, 1], calibrated[:, 2], s=1)
ax2.set_title('Calibrated Magnetometer Data')
ax2.set_xlabel('X'); ax2.set_ylabel('Y'); ax2.set_zlabel('Z')

plt.tight_layout()
plt.show()
