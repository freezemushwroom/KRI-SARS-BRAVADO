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

for _ in range(10000): #while True: #for _ in range(1000):
    try:
        if _ == 1999:
            print("Change Direction")
        if _ == 4999:
            print("Change Direction")
        if _ == 6999:
            print("Change Direction")
        if _ == 8999:
            print("Change Direction")
        #user_input = input("Colecting Data, Enter to stop")
        #if user_input == "":
        #    print("Stop Collecting Data")
        #    break
        data = bmx.get_all_data()
        mag = [data[0], data[1], data[2]]  # Should return a list or tuple of 3 values
        mag_data.append(mag)
    except Exception as e:
        print(f"Error reading magnetometer: {e}")
    time.sleep(0.01)  # Adjust sample rate (100 Hz)

mag_data = np.array(mag_data)  # Use your collected magnetometer data
data = mag_data
x, y, z = data[:,0], data[:,1], data[:,2]
D = np.array([x*x,
              y*y,
              z*z,
              2*y*z,
              2*x*z,
              2*x*y,
              2*x,
              2*y,
              2*z,
              np.ones(len(x))]).T
d2 = x*x + y*y + z*z
u, s, vh = np.linalg.svd(D, full_matrices=False)
v = vh.T
p = v[:,-1]

A = np.array([[p[0], p[5], p[4], p[6]],
              [p[5], p[1], p[3], p[7]],
              [p[4], p[3], p[2], p[8]],
              [p[6], p[7], p[8], p[9]]])
 # Center of the ellipsoid
A3 = A[0:3, 0:3]
b = -np.linalg.solve(A3, p[6:9])
T = np.eye(4)
T[3, :3] = b

R = T @ A @ T.T
R3 = R[0:3, 0:3]
evals, evecs = np.linalg.eig(R3 / -R[3, 3])

radii = np.sqrt(1.0 / np.abs(evals))
offset = b

# Soft iron correction matrix
soft_iron_matrix = evecs @ np.diag(1.0 / radii) @ evecs.T

calibrated = (data - offset) @ soft_iron_matrix

print(offset)
print(soft_iron_matrix)

# ------------- Plot Before and After -------------
fig = plt.figure(figsize=(12, 5))

# Raw
ax1 = fig.add_subplot(121, projection='3d')
ax1.scatter(mag_data[:, 0], mag_data[:, 1], mag_data[:, 2], s=1)
ax1.set_title('Raw Magnetometer Data')
ax1.set_xlabel('X'); ax1.set_ylabel('Y'); ax1.set_zlabel('Z')

# Calibrated
ax2 = fig.add_subplot(122, projection='3d')
ax2.scatter(calibrated[:, 0], calibrated[:, 1], calibrated[:, 2], s=1)
ax2.set_title('Calibrated Magnetometer Data')
ax2.set_xlabel('X'); ax2.set_ylabel('Y'); ax2.set_zlabel('Z')

plt.tight_layout()
plt.show()
