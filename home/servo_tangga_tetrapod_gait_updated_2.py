import sys
import time
import math
import numpy as np
from adafruit_servokit import ServoKit
from DFRobot_BMX160 import BMX160
from ahrs.filters import Madgwick
from scipy.spatial.transform import Rotation as R

# ---------------------------------------------------------
# 1. HARDWARE & SERVO INITIALIZATION
# ---------------------------------------------------------
kit1 = ServoKit(channels=16, address=0x41, reference_clock_speed=24723456)
kit2 = ServoKit(channels=16, address=0x40, reference_clock_speed=24985600)

for i in range(9):
    kit1.servo[i].set_pulse_width_range(320, 2320)
    kit2.servo[15-i].set_pulse_width_range(400, 2400)

bmx = BMX160(1)
while not bmx.begin():
    print("Waiting for BMX160 IMU...")
    time.sleep(2)

# Leg physical dimensions (cm)
coxa = 2.644
femur = 6.436
tibia = 8.122

panjang_depan_belakang = 23.3
mundur = -10
forward = 4
mepet = 0
yaw = 0
delay = 0.3

# ---------------------------------------------------------
# 2. IMU CALIBRATION & HELPER FUNCTIONS
# ---------------------------------------------------------
def calculate_IMU_error():
    c = 0
    AccelErrorX = AccelErrorY = AccelErrorZ = 0
    GyroErrorX = GyroErrorY = GyroErrorZ = 0
    while c < 200:
        data = bmx.get_all_data()
        GyroErrorX += data[3]
        GyroErrorY += data[4]
        GyroErrorZ += data[5]
        AccelErrorX += data[6]
        AccelErrorY += data[7]
        AccelErrorZ += data[8]
        c += 1
        time.sleep(0.005)
    return (GyroErrorX/200, GyroErrorY/200, GyroErrorZ/200, 
            AccelErrorX/200, AccelErrorY/200, AccelErrorZ/200)

def read_imu_roll(q, madgwick, last_time, IMUX, IMUY, IMUZ, IMUAX, IMUAY, IMUAZ):
    """Reads IMU, updates Madgwick filter, and returns Roll clamped between [0, -27]."""
    data = bmx.get_all_data()
    acc = np.array([data[6] - IMUAX, data[7] - IMUAY, 9.8066501 + data[8] - IMUAZ])
    gyr = np.radians(np.array([data[3] - IMUX, data[4] - IMUY, data[5] - IMUZ]))
    
    current_time = time.perf_counter()
    dt = max(current_time - last_time, 0.001)
    
    q_updated = madgwick.updateIMU(q=q, acc=acc, gyr=gyr, dt=dt)
    
    if q_updated is not None:
        q = q_updated
        
    r = R.from_quat([q[1], q[2], q[3], q[0]])
    roll_deg, pitch_deg, yaw_deg = r.as_euler('xyz', degrees=True)
    
    # Map and clamp slope Roll (Flat: 0 deg, Slope: -27 deg)
    clamped_roll = max(-27.0, min(0.0, roll_deg))
    return clamped_roll, q, current_time

# ---------------------------------------------------------
# 3. INVERSE KINEMATICS (IK) FUNCTIONS
# ---------------------------------------------------------
def nilai_h(panjang, derajat, maju, geser):
    h = tibia + (math.tan(math.radians(derajat)) * panjang)
    alpha1 = math.acos(((femur * tibia) - (math.sqrt((math.pow(femur, 2) * math.pow(tibia, 2)) + (math.pow(femur, 2) * (math.pow(h, 2) - math.pow(tibia, 2)))))) / math.pow(femur, 2))
    l = math.sin(alpha1) * femur - geser
    return h, l

def IK_tengah(maju, yaw, panjang, roll, geser):
    h, l = nilai_h(panjang, abs(roll), maju, geser)
    P = math.sqrt(math.pow(maju, 2) + math.pow((l + coxa), 2) - (2 * maju * (l + coxa) * math.cos(math.radians(90 - yaw))))
    P = P - coxa
    M = math.sqrt(math.pow(h, 2) + math.pow(P, 2))

    sudut_base_coxa = math.degrees(math.acos((math.pow((l + coxa), 2) + math.pow(P + coxa, 2) - math.pow(maju, 2)) / (2 * (l + coxa) * (P + coxa))))
    sudut_coxa_femur_1 = math.degrees(math.acos((math.pow(femur, 2) + math.pow(M, 2) - math.pow(tibia, 2)) / (2 * femur * M)))
    sudut_coxa_femur_2 = math.degrees(math.acos((math.pow(M, 2) + math.pow(h, 2) - math.pow(P, 2)) / (2 * h * M)))
    
    return (sudut_base_coxa, sudut_coxa_femur_1 + sudut_coxa_femur_2, math.degrees(math.acos((math.pow(femur, 2) + math.pow(tibia, 2) - math.pow(M, 2)) / (2 * tibia * femur))))

def IK_depan(maju, yaw, panjang, roll, geser):
    h, l = nilai_h(panjang, max(-15, roll), maju, geser)
    PD = math.sqrt(math.pow(maju, 2) + math.pow((l + coxa), 2) - (2 * maju * (l + coxa) * math.cos(math.radians(135 - yaw))))
    PD = PD - coxa
    MD = math.sqrt(math.pow(h, 2) + math.pow(PD, 2))

    sudut_base_coxa = math.degrees(math.acos((math.pow((l + coxa), 2) + math.pow(PD + coxa, 2) - math.pow(maju, 2)) / (2 * (l + coxa) * (PD + coxa))))
    sudut_coxa_femur_1 = math.degrees(math.acos((math.pow(femur, 2) + math.pow(MD, 2) - math.pow(tibia, 2)) / (2 * femur * MD)))
    sudut_coxa_femur_2 = math.degrees(math.acos((math.pow(MD, 2) + math.pow(h, 2) - math.pow(PD, 2)) / (2 * h * MD)))

    return (sudut_base_coxa, sudut_coxa_femur_1 + sudut_coxa_femur_2, math.degrees(math.acos((math.pow(femur, 2) + math.pow(tibia, 2) - math.pow(MD, 2)) / (2 * tibia * femur))))

def IK_belakang(maju, yaw, panjang, roll, mundur, geser):
    h, l = nilai_h(panjang, -min(roll, 15), maju, geser)
    PB = math.sqrt(math.pow(maju, 2) + math.pow((l + coxa), 2) - (2 * maju * (l + coxa) * math.cos(math.radians(90 - mundur - 45 - yaw))))
    PB = PB - coxa
    MB = math.sqrt(math.pow(h, 2) + math.pow(PB, 2))

    sudut_base_coxa = math.degrees(math.acos((math.pow((l + coxa), 2) + math.pow(PB + coxa, 2) - math.pow(maju, 2)) / (2 * (l + coxa) * (PB + coxa))))
    sudut_coxa_femur_1 = math.degrees(math.acos((math.pow(femur, 2) + math.pow(MB, 2) - math.pow(tibia, 2)) / (2 * femur * MB)))
    sudut_coxa_femur_2 = math.degrees(math.acos((math.pow(MB, 2) + math.pow(h, 2) - math.pow(PB, 2)) / (2 * h * MB)))

    return (sudut_base_coxa, sudut_coxa_femur_1 + sudut_coxa_femur_2, math.degrees(math.acos((math.pow(femur, 2) + math.pow(tibia, 2) - math.pow(MB, 2)) / (2 * tibia * femur))))

def wait(waktu):
    myTime = time.time()
    while time.time() - myTime < waktu:
        pass

# ---------------------------------------------------------
# 4. MAIN GAIT LOOP WITH GYRO FEEDBACK
# ---------------------------------------------------------
IMUX, IMUY, IMUZ, IMUAX, IMUAY, IMUAZ = calculate_IMU_error()
q = np.array([1.0, 0.0, 0.0, 0.0])
madgwick = Madgwick()
previous_time = time.perf_counter()

try:
    while True:
        # Read roll dynamically from IMU
        current_roll, q, previous_time = read_imu_roll(
            q, madgwick, previous_time, IMUX, IMUY, IMUZ, IMUAX, IMUAY, IMUAZ
        )
        print(f"Current Gyro Slope Roll: {current_roll:.2f} deg")

        # Dynamically scale Phase 4 recovery lift angles based on roll magnitude (0 deg to -27 deg)
        # Flat (0 deg) -> Femur Lift: +35 deg, Tibia Lift: +60 deg
        # Slope (-27 deg) -> Femur Lift: +55 deg, Tibia Lift: +92 deg
        slope_factor = abs(current_roll) / 27.0
        femur_lift = 35 + (20 * slope_factor)
        tibia_lift = 60 + (32 * slope_factor)

        # Re-calculate standing angles using current dynamic roll
        _, coxa_femur_tengah_berdiri, femur_tibia_tengah_berdiri = IK_tengah(0, 0, 0, current_roll, 0)
        base_coxa_depan_berdiri, coxa_femur_depan_berdiri, femur_tibia_depan_berdiri = IK_depan(0, 0, panjang_depan_belakang/2, current_roll, 0)
        base_coxa_belakang_berdiri, coxa_femur_belakang_berdiri, femur_tibia_belakang_berdiri = IK_belakang(0, 0, panjang_depan_belakang/2, current_roll, mundur, 0)

        # Solve swing vectors
        base_coxa_tengah_kiri, coxa_femur_tengah_kiri, femur_tibia_tengah_kiri = IK_tengah(forward, yaw, 0, current_roll, mepet)
        base_coxa_depan_kiri, coxa_femur_depan_kiri, femur_tibia_depan_kiri = IK_depan(forward, yaw, panjang_depan_belakang/2, current_roll, mepet)
        base_coxa_belakang_kiri, coxa_femur_belakang_kiri, femur_tibia_belakang_kiri = IK_belakang(-forward, yaw, panjang_depan_belakang/2, current_roll, mundur, mepet)

        base_coxa_tengah_kanan, coxa_femur_tengah_kanan, femur_tibia_tengah_kanan = IK_tengah(forward, -yaw, 0, current_roll, -mepet)
        base_coxa_depan_kanan, coxa_femur_depan_kanan, femur_tibia_depan_kanan = IK_depan(forward, -yaw, panjang_depan_belakang/2, current_roll, -mepet)
        base_coxa_belakang_kanan, coxa_femur_belakang_kanan, femur_tibia_belakang_kanan = IK_belakang(-forward, -yaw, panjang_depan_belakang/2, current_roll, mundur, -mepet)

        # Normalize relative deltas
        coxa_femur_belakang_kiri -= coxa_femur_belakang_berdiri
        femur_tibia_belakang_kiri -= femur_tibia_belakang_berdiri
        base_coxa_belakang_kiri = (180 - base_coxa_belakang_kiri) - (180 - base_coxa_belakang_berdiri)

        coxa_femur_belakang_kanan -= coxa_femur_belakang_berdiri
        femur_tibia_belakang_kanan -= femur_tibia_belakang_berdiri
        base_coxa_belakang_kanan = (180 - base_coxa_belakang_kanan) - (180 - base_coxa_belakang_berdiri)

        # -----------------------------------------------------
        # PHASE 1: MIDDLE LEGS
        # -----------------------------------------------------
        kit1.servo[4].angle = max(0, min(((coxa_femur_tengah_berdiri + 35) + 30), 180))
        kit1.servo[3].angle = max(0, min((180 - (femur_tibia_tengah_berdiri - 45) + 30), 180))
        kit2.servo[11].angle = max(0, min((180 - (coxa_femur_tengah_berdiri + 35) - 30), 180))
        kit2.servo[12].angle = max(0, min(((femur_tibia_tengah_berdiri - 45) - 30), 180))
        wait(delay)

        kit1.servo[5].angle = max(0, min((90 + (base_coxa_tengah_kiri - base_coxa_tengah_berdiri)), 180))
        kit2.servo[10].angle = max(0, min((90 - (base_coxa_tengah_kanan - base_coxa_tengah_berdiri)), 180))
        wait(delay)

        kit1.servo[3].angle = max(0, min((180 - (femur_tibia_tengah_berdiri - 45) - (femur_tibia_tengah_kiri - femur_tibia_tengah_berdiri)), 180))
        kit2.servo[12].angle = max(0, min(((femur_tibia_tengah_berdiri - 45) + (femur_tibia_tengah_kanan - femur_tibia_tengah_berdiri)), 180))
        wait(0.05)
        kit1.servo[4].angle = max(0, min(((coxa_femur_tengah_berdiri + 35) + (coxa_femur_tengah_kiri - coxa_femur_tengah_berdiri)), 180))
        kit2.servo[11].angle = max(0, min((180 - (coxa_femur_tengah_berdiri + 35) - (coxa_femur_tengah_kanan - coxa_femur_tengah_berdiri)), 180))
        wait(delay)

        # -----------------------------------------------------
        # PHASE 2: FRONT LEGS
        # -----------------------------------------------------
        kit1.servo[7].angle = max(0, min(((coxa_femur_depan_berdiri + 35) + 60), 180))
        kit1.servo[6].angle = max(0, min((180 - (femur_tibia_depan_berdiri - 45) + 60), 180))
        kit2.servo[8].angle = max(0, min((180 - (coxa_femur_depan_berdiri + 35) - 60), 180))
        kit2.servo[9].angle = max(0, min(((femur_tibia_depan_berdiri - 45) - 60), 180))

        kit1.servo[8].angle = max(0, min((90 - 20), 180))
        kit2.servo[7].angle = max(0, min((90 + 20), 180))
        kit1.servo[6].angle = max(0, min((180 - (femur_tibia_depan_berdiri - 45) - 30), 180))
        kit2.servo[9].angle = max(0, min(((femur_tibia_depan_berdiri - 45) + 30), 180))
        wait(0.3)

        kit1.servo[8].angle = max(0, min((90 + (base_coxa_depan_kiri - base_coxa_depan_berdiri)), 180))
        kit2.servo[7].angle = max(0, min((90 - (base_coxa_depan_kanan - base_coxa_depan_berdiri)), 180))
        wait(delay)

        kit1.servo[6].angle = max(0, min((180 - (femur_tibia_depan_berdiri - 45) - (femur_tibia_depan_kiri - femur_tibia_depan_berdiri)), 180))
        kit2.servo[9].angle = max(0, min(((femur_tibia_depan_berdiri - 45) + (femur_tibia_depan_kanan - femur_tibia_depan_berdiri)), 180))
        wait(0.1)
        kit1.servo[7].angle = max(0, min(((coxa_femur_depan_berdiri + 35) + (coxa_femur_depan_kiri - coxa_femur_depan_berdiri)), 180))
        kit2.servo[8].angle = max(0, min((180 - (coxa_femur_depan_berdiri + 35) - (coxa_femur_depan_kanan - coxa_femur_depan_berdiri)), 180))
        wait(delay)

        # -----------------------------------------------------
        # PHASE 3: BODY STANCE PUSH
        # -----------------------------------------------------
        kit1.servo[8].angle = 90
        kit1.servo[7].angle = (coxa_femur_depan_berdiri + 35)
        kit1.servo[6].angle = 180 - (femur_tibia_depan_berdiri - 45)

        kit1.servo[5].angle = 90
        kit1.servo[4].angle = (coxa_femur_tengah_berdiri + 35)
        kit1.servo[3].angle = 180 - (femur_tibia_tengah_berdiri - 45)

        kit2.servo[10].angle = 90
        kit2.servo[11].angle = 180 - (coxa_femur_tengah_berdiri + 35)
        kit2.servo[12].angle = (femur_tibia_tengah_berdiri - 45)

        kit2.servo[7].angle = 90
        kit2.servo[8].angle = 180 - (coxa_femur_depan_berdiri + 35)
        kit2.servo[9].angle = (femur_tibia_depan_berdiri - 45)

        kit1.servo[2].angle = max(0, min((90 - mundur + base_coxa_belakang_kiri), 180))
        kit1.servo[1].angle = max(0, min(((coxa_femur_belakang_berdiri + 35) + coxa_femur_belakang_kiri), 180))
        kit1.servo[0].angle = max(0, min((180 - (femur_tibia_belakang_berdiri - 45) - femur_tibia_belakang_kiri), 180))

        kit2.servo[13].angle = max(0, min((90 + mundur - base_coxa_belakang_kanan), 180))
        kit2.servo[14].angle = max(0, min((180 - (coxa_femur_belakang_berdiri + 35) - coxa_femur_belakang_kanan), 180))
        kit2.servo[15].angle = max(0, min(((femur_tibia_belakang_berdiri - 45) + femur_tibia_belakang_kanan), 180))

        wait(delay)

        # -----------------------------------------------------
        # PHASE 4: REAR LEG RECOVERY (GYRO-SCALED LIFT)
        # -----------------------------------------------------
        # Leg 3 (Left Rear) Lift
        kit1.servo[1].angle = max(0, min(((coxa_femur_belakang_berdiri + 35) + femur_lift), 180))
        kit1.servo[0].angle = max(0, min((180 - (femur_tibia_belakang_berdiri - 45) + tibia_lift), 180))
        wait(0.5)

        # Leg 3 Reset
        kit1.servo[2].angle = 90 - mundur
        kit1.servo[1].angle = (coxa_femur_belakang_berdiri + 35)
        kit1.servo[0].angle = 180 - (femur_tibia_belakang_berdiri - 45)
        wait(delay)

        # Leg 4 (Right Rear) Lift
        kit2.servo[14].angle = max(0, min((180 - (coxa_femur_belakang_berdiri + 35) - femur_lift), 180))
        kit2.servo[15].angle = max(0, min(((femur_tibia_belakang_berdiri - 45) - tibia_lift), 180))
        wait(0.5)

        # Leg 4 Reset
        kit2.servo[13].angle = 90 + mundur
        kit2.servo[14].angle = 180 - (coxa_femur_belakang_berdiri + 35)
        kit2.servo[15].angle = (femur_tibia_belakang_berdiri - 45)

        wait(delay)

except KeyboardInterrupt:
    print("Program stopped by user.")