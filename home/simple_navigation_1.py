#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from std_msgs.msg import String
from std_msgs.msg import Float32MultiArray, Int32MultiArray, String
from std_msgs.msg import Bool

import time
SAFE_DISTANCE = 0.10

movement_counter = 0


class NavigationController(Node):

    def __init__(self):
        super().__init__("navigation_controller")
        self.deviation_yaw = 0.0 # untuk menemrima data callback Yaw
        self.deviation_roll = 0.0 # untuk menerima data callback Roll
        self.deviation_pitch = 0.0 # untuk menerima data callback Pitch
        self.deviation_left_dist = 0.0 # utnuk menerima data callback left_dist
        self.deviation_right_dist = 0.0 # untuk menerima data callback right_dist

        self.yaw_dev_value = 0.0 # untuk menyimpan data error Yaw sebagai referensi
        self.leftdist_dev_value = 0.0
        self.rightdist_dev_value = 0.0
        self.location_state_val = 0.0 # untuk menyimpan data state lokasi robot
        self.tetrapod_gait = False

        self.correcting_state = False
        self.correcting_state_strafe = False
        self.quadrant_compensation_val = 0.0 # for the positive side
        self.quadrant_compensation_val_2 = 0.0 # for the negative side
        self.strafe_correction_debug = False
        self.movement_state = False

        self.msg = Float32MultiArray()
        self.current_state = 0.0

        self.correcting_counter = 0.0
        self.timeout_active = False
        self.recovery_attempts = 0
        self.timeout_active = False
        self.previous_timeout = False

        self.timeout_recovery_counter = 0

        self.deviation_front_dist = 0.0
        self.deviation_back_dist = 0.0
        self.left_front = 0.0
        self.left = 0.0
        self.left_rear = 0.0

        self.back = 0.0

        self.right_front = 0.0
        self.right = 0.0

        self.front = 0.0

        self.pub = self.create_publisher(
            Float32MultiArray,
            "/cmd_movement",
            1
        )

        self.sub = self.create_subscription(
            Float32MultiArray,
            "/location_state",
            #self.location_callback,
            self.location_state_callback,
            1
        )

        self.sub_rpy = self.create_subscription(
            Float32MultiArray,
            "/rpy",
            self.rpy_callback,
            1
        )

        self.sub_left_dist = self.create_subscription(
            Float32MultiArray,
            "/left_dist",
            self.left_dist_callback,
            1
        )

        self.sub_right_dist = self.create_subscription(
            Float32MultiArray,
            "/right_dist",
            self.right_dist_callback,
            1
        )
        self.sub_front_dist = self.create_subscription(
            Float32MultiArray,
            "/front_dist",
            self.front_dist_callback,
            1
        )

        self.sub_back_dist = self.create_subscription(
            Float32MultiArray,
            "/back_dist",
            self.back_dist_callback,
            1
        )
        self.create_subscription(
            Int32MultiArray,
            "/ultrasonic",
            self.ultrasonic_cb,
            1
        )

        self.pub_tetrapod_gait = self.create_publisher(
            Bool,
            "/move_tetrapod",
            1
        )

        self.pub_correction_move = self.create_publisher(
            String,
            "/correction_detect",
            1
        )

        # ini subsciber buat debugging aja
        self.sub_debug_strafe = self.create_subscription(
            Bool,
            "/debug_strafe",
            self.strafe_debug_callback,
            1
        )

        self.sub_movement_state = self.create_subscription(
            Bool,
            "/movement_state",
            #"/motion_complete", # awalnya /movement_state yaitu dari gazebo joint pblisher, tapi kita ganti biar bisa pasti sama acceleration value
            self.movement_state_callback,
            1
        )
        self.sub_timeout = self.create_subscription(
            Bool,
            "/navigation_timeout",
            self.timeout_callback,
            1
        )

        self.current_state = Float32MultiArray()
        

        self.get_logger().info("Navigation Controller Started")
        self.create_timer(2.0, self.location_callback) # location_callback jadi function jalan

    def publish_correction(self, type, value):
        self.msg = String()
        self.msg.data = type + str(value)
        self.pub_correction_move.publish(self.msg)
    
    def rpy_callback(self, msg):
        if self.movement_state == False:
            if len(msg.data)>=3:
                self.deviation_roll, self.deviation_pitch, self.deviation_yaw = msg.data[:3]
        else:
            self.get_logger().info("Robot is moving, not getting any info (rpy)")
    
    def movement_state_callback(self, msg):
        self.movement_state = msg.data # kita atur not karna /motion_complete itu kebalikan datanya untuk /movement_state saat memberikan informasi yang sama
        #self.movement_state = False # uncomment untuk mode debug
    
    def left_dist_callback(self, msg):
        if self.movement_state == False: 
            if msg.data:self.deviation_left_dist = msg.data[0]
        else:
            self.get_logger().info("Robot is moving, not getting any info (uls)")
    
    def right_dist_callback(self, msg):
        if self.movement_state == False:
            if msg.data:self.deviation_right_dist = msg.data[0]
        else:
            self.get_logger().info("Robot is moving, not getting any info (right)")
    
    def front_dist_callback(self,msg):
        if not self.movement_state:
            if msg.data:
                self.deviation_front_dist = msg.data[0]

    def back_dist_callback(self,msg):
        if not self.movement_state:
            if msg.data:
                self.deviation_back_dist = msg.data[0]
    def ultrasonic_cb(self, msg):
    
        if len(msg.data) < 7:
            return

        self.left_front = float(msg.data[0])
        self.left       = float(msg.data[1])
        self.left_rear  = float(msg.data[2])
        self.back       = float(msg.data[3])
        self.right_front= float(msg.data[4])
        self.right      = float(msg.data[5])
        self.front      = float(msg.data[6])


    def strafe_debug_callback(self, msg):
        self.strafe_correction_debug = msg.data[0]
    
    def timeout_callback(self,msg):

        self.timeout_active = msg.data

        # timeout finished
        if self.previous_timeout and not self.timeout_active:

            self.get_logger().info(
                "Recovery successful. Resetting timeout counter."
            )

            self.timeout_recovery_counter = 0

        self.previous_timeout = self.timeout_active
    
    def location_state_callback(self, msg):
        if self.movement_state == False:
            if msg.data == self.current_state:
                return
            self.location_state_val = msg.data[0]
        else:
            self.get_logger().info("Robot is moving, not getting any info (loca)")

    def location_callback(self):
        step = String
        rep = int
        unknown_state = False
        if self.movement_state == False:

            # Ignore repeated states
            #if msg.data == self.current_state:
            #    return

            #self.current_state = msg.data[0]
            self.current_state = self.location_state_val # location_state_val unnecessary banget

            self.get_logger().info(f"New State: {self.current_state}")

            if self.current_state == 1.0 or self.current_state == 2.0:
                self.quadrant_compensation_val = 0.0
                self.quadrant_compensation_val_2 = 0.0
            elif self.current_state == 4.0 or self.current_state == 5.0:
                self.quadrant_compensation_val = 90.0
                self.quadrant_compensation_val_2 = 270.0
            elif self.current_state == 7.0:
                self.quadrant_compensation_val = 180.0
                self.quadrant_compensation_val_2 = 180.0

            if self.current_state == 1.0 or ( # 1.0 = A (q1)
                self.current_state == 2.0 or # 2.0 = B_beta (q1)
                self.current_state == 4.0 or # 4.0 = B_next (q2)
                self.current_state == 5.0 or # 5.0 = C (q2)
                self.current_state == 7.0 # 7.0 = D_next (q3)
            ): # A
                #self.walk_forward(1)
                # dibawah adalah koreksi untuk pergerakan yaw yang bisa digunaakn untuk kondisi saat "maju" apapun

                #dibawah ini fix untuk robot
                self.deviation_left_dist = self.left
                self.deviation_right_dist = self.right

                # untuk sementara ini smeua pergerakan koreksi ditutup dulu sampai sudah optimal

                #quadrant 1
                step = "forward"
                if self.quadrant_compensation_val == 0.0 and self.deviation_yaw <= 180.0 and self.deviation_yaw > 9.0:
                    self.yaw_dev_value = self.deviation_yaw
                    self.correcting_state = True
                    self.publish_correction("Leaning Left(q1) ", self.deviation_yaw)
                    self.get_logger().info("Leaning Left(q1)")
                elif self.quadrant_compensation_val == 0.0 and self.deviation_yaw > 180 and self.deviation_yaw < 360.0 - 9.0:
                    self.yaw_dev_value = self.deviation_yaw
                    self.correcting_state = True
                    self.publish_correction("Leaning Right(q1) ", self.deviation_yaw)
                    self.get_logger().info("Leaning Right(q1)")
                
                # quadrant 2
                if self.quadrant_compensation_val == 90.0 and self.deviation_yaw <= 270 and self.deviation_yaw > 90.0 + 9.0:
                    self.yaw_dev_value = self.deviation_yaw
                    self.correcting_state = True
                    self.publish_correction("Leaning Left(q2) ", self.deviation_yaw)
                    self.get_logger().info("Leaning Left(q2)")
                elif self.quadrant_compensation_val == 90.0 and (self.deviation_yaw > 270.0 or self.deviation_yaw < 90.0 - 9.0):
                    self.yaw_dev_value = self.deviation_yaw
                    self.correcting_state = True
                    self.publish_correction("Leaning Right(q2) ", self.deviation_yaw)
                    self.get_logger().info("Leaning Right(q2)")

                # quadrant 3
                if self.quadrant_compensation_val == 180.0 and self.deviation_yaw <= 360.0 and self.deviation_yaw > 180.0 + 9.0:
                    self.yaw_dev_value = self.deviation_yaw
                    self.correcting_state = True
                    self.publish_correction("Leaning Left(q3) ", self.deviation_yaw)
                    self.get_logger().info("Leaning Left(q3)")
                elif self.quadrant_compensation_val == 180.0 and self.deviation_yaw > 0.0 and self.deviation_yaw < 180.0 - 9.0:
                    self.yaw_dev_value = self.deviation_yaw
                    self.correcting_state = True
                    self.publish_correction("Leaning Right(q3) ", self.deviation_yaw)
                    self.get_logger().info("Leaning Right(q3)")
                
                elif self.deviation_right_dist < 8 and self.deviation_right_dist > 1:
                    self.rightdist_dev_value = self.deviation_right_dist
                    self.correcting_state_strafe = True
                    self.publish_correction("Close to right wall ", self.deviation_right_dist)
                    self.get_logger().info("Close to right wall")
                
                elif self.deviation_left_dist < 8 and self.deviation_left_dist > 1:
                    self.leftdist_dev_value = self.deviation_left_dist
                    self.correcting_state_strafe = True
                    self.publish_correction("Close to left wall ", self.deviation_left_dist)
                    self.get_logger().info("Close to left wall")
                
                #fix bidang miring
                #if self.current_state == 1.0 and (self.deviation_back_dist <= 0.0 or self.deviation_back_dist >= 1.3):
                #    step = "forward_tetrapod"  
                if self.current_state == 2.0 and self.deviation_pitch > 1.0:
                    #step = "forward_tetrapod" # buka ini kalau sudah ada pergerakan tetrapod
                    step = "forward"
                elif self.current_state == 2.0 and self.deviation_pitch < 1.0:
                    step = "forward"

            elif self.current_state == 3.0 or ( # 3.0 = B
                self.current_state == 6.0 # 6.0 = D
            ): # B
                #self.turn_left(1)
                step = "left"

            elif self.current_state == 7.0: # E
                #self.stop()
                step = "stop"
                self.get_logger().info("STOP - endpoint")

            else:
                self.get_logger().warn(f"Unknown state: {self.current_state}")
                unknown_state = True

            #q1
            if self.correcting_state == True:
                if self.quadrant_compensation_val == 0.0 and self.yaw_dev_value > 0.0  and self.yaw_dev_value <=180.0:
                    if self.deviation_yaw >8.0:
                        step = "right" # counter move
                        self.correcting_counter = self.correcting_counter + 1.0
                    else:
                        self.correcting_state = False
                        step = "stop"
                        self.get_logger().info("STOP - done right correction(q1)")
                        self.yaw_dev_value = self.deviation_yaw
                    #if self.correcting_counter >= 2.0:
                    #    self.correcting_state = False # jadi kita cuman 2 kali aja
                elif self.quadrant_compensation_val == 0.0 and self.yaw_dev_value < 360.0 and self.yaw_dev_value > 180:
                    # also correct the yaw orientation
                    if self.deviation_yaw <360.0 -8.0:
                        step = "left"
                        self.correcting_counter = self.correcting_counter + 1.0
                    else:
                        self.correcting_state = False
                        step = "stop"
                        self.get_logger().info("STOP - done left correction(q1)")
                        self.yaw_dev_value = self.deviation_yaw
            #q2
            if self.correcting_state == True:
                if self.quadrant_compensation_val == 90.0 and self.yaw_dev_value > 90.0  and self.yaw_dev_value <=270.0:
                    if self.deviation_yaw >98.0:
                        step = "right" # counter move
                        self.correcting_counter = self.correcting_counter + 1.0
                    else:
                        self.correcting_state = False
                        step = "stop"
                        self.get_logger().info("STOP - done right correction(q2)")
                        self.yaw_dev_value = self.deviation_yaw
                    #if self.correcting_counter >= 2.0:
                    #    self.correcting_state = False # jadi kita cuman 2 kali aja
                elif self.quadrant_compensation_val == 90.0 and (self.yaw_dev_value < 90.0 or self.yaw_dev_value > 270.0):
                    # also correct the yaw orientation
                    if self.deviation_yaw <90.0 -8.0:
                        step = "left"
                        self.correcting_counter = self.correcting_counter + 1.0
                    else:
                        self.correcting_state = False
                        step = "stop"
                        self.get_logger().info("STOP - done left correction(q2)")
                        self.yaw_dev_value = self.deviation_yaw

            #q3
            if self.correcting_state == True:
                if self.quadrant_compensation_val == 180.0 and self.yaw_dev_value > 180.0  and self.yaw_dev_value <=360.0:
                    if self.deviation_yaw >188.0:
                        step = "right" # counter move
                        self.correcting_counter = self.correcting_counter + 1.0
                    else:
                        self.correcting_state = False
                        step = "stop"
                        self.get_logger().info("STOP - done right correction(q3)")
                        self.yaw_dev_value = self.deviation_yaw
                    #if self.correcting_counter >= 2.0:
                    #    self.correcting_state = False # jadi kita cuman 2 kali aja
                elif self.quadrant_compensation_val == 180.0 and self.yaw_dev_value < 180.0 and self.yaw_dev_value > 0.0:
                    # also correct the yaw orientation
                    if self.deviation_yaw <180.0 -8.0:
                        step = "left"
                        self.correcting_counter = self.correcting_counter + 1.0
                    else:
                        self.correcting_state = False
                        step = "stop"
                        self.get_logger().info("STOP - done left correction(q3)")
                        self.yaw_dev_value = self.deviation_yaw
            
            if self.correcting_state_strafe == True:
                if self.rightdist_dev_value < 12:
                    if self.deviation_right_dist < 12:
                        step = "strafe_left"
                        self.correcting_counter = self.correcting_counter + 1.0
                    else:
                        self.correcting_state_strafe = False
                        step = "stop"
                        self.get_logger().info("STOP - done strafe_left")
                        self.rightdist_dev_value = self.deviation_right_dist
                        self.get_logger().info(f"{self.rightdist_dev_value}")
                elif self.leftdist_dev_value < 12:
                    if self.deviation_left_dist < 12:
                        step = "strafe_right"
                        self.correcting_counter = self.correcting_counter + 1.0
                    else:
                        self.correcting_state_strafe = False
                        step = "stop"
                        self.get_logger().info("STOP - done strafe_right")
                        self.leftdist_dev_value = self.deviation_left_dist
        

                if self.correcting_counter >= 1.0:
                    self.correcting_state = False # jadi cuman 2 step aja
                    self.correcting_counter = 0.0
            
            rep = 1
            if not unknown_state:
                self.execute_step(step, rep) # antara maju/left dan 1 
                #self.movement_state = True
        else:
            self.get_logger().info("Robot is moving, not generating output")

        # --------------------------
        # Timeout Recovery
        # --------------------------

        if self.timeout_active:

            self.timeout_recovery()

            return
    
    def timeout_recovery(self):

        self.timeout_recovery_counter += 1

        self.get_logger().warn(
            f"Timeout Recovery Attempt {self.timeout_recovery_counter}"
        )

        # Too many attempts
        if self.timeout_recovery_counter >= 5:

            self.get_logger().error(
                "Recovery failed. Robot stopped."
            )

            self.stop()

            return

        front = self.deviation_front_dist
        left = self.deviation_left_dist
        right = self.deviation_right_dist
        back = self.deviation_back_dist

        distances = {
            "forward": front,
            "backward": back,
            "left": left,
            "right": right
        }
        if max(distances.values()) < SAFE_DISTANCE:
            self.get_logger().warn(
                "No safe recovery direction. Stopping robot."
            )
            self.stop()
            return

        direction = max(distances, key=distances.get)

        self.get_logger().info(
            f"Recovery Direction : {direction}"
        )

        if direction == "forward":

            self.walk_forward(1)

        elif direction == "backward":

            self.walk_backward(1)

        elif direction == "left":

            self.turn_left(1)

            self.walk_forward(1)

        elif direction == "right":

            self.turn_right(1)

            self.walk_forward(1)
            
    def execute_step(self, step, rep):
        #self.movement_state = True # kita set true setiap sebelum menjalankan servo, agar dapat di set False setelah joint publisher selesai gerak
        if step == "forward":
            self.walk_forward(rep) # umumnya 1
        elif step == "left":
            self.turn_left(rep)
        elif step == "right":
            self.turn_right(rep)
        elif step == "strafe_left":
            self.strafe_left(rep)
        elif step == "strafe_right":
            self.strafe_right(rep)
        elif step == "forward_tetrapod":
            self.tetrapod_forward(rep)
        elif step == "stop":
            self.stop()

    def publish_movement(self, data, message):
        global movement_counter
        self.movement_state = True
        movement_counter = movement_counter + 1
        self.get_logger().info(f"Perintah ke({movement_counter}) ")
        self.msg = Bool()
        self.msg.data = False
        self.pub_tetrapod_gait.publish(self.msg)
        self.msg = Float32MultiArray()
        self.msg.data = data
        self.pub.publish(self.msg)
        self.get_logger().info(message)

    def stop(self):
        self.msg = Bool()
        self.msg.data = False
        self.pub_tetrapod_gait.publish(self.msg)
        self.msg = Float32MultiArray()
        self.msg.data = [0.0, 0.0, 0.0]
        #self.pub.publish(self.msg)
        #self.get_logger().info("STOP aja")
        self.publish_movement(self.msg.data, "STOP aja")

    def walk_forward(self, steps):
        self.msg = Bool()
        self.msg.data = False # atur jadi true kalau mau movement tetrapod aja
        self.pub_tetrapod_gait.publish(self.msg)
        self.msg = Float32MultiArray()
        for _ in range(steps):
            self.msg.data = [6.0, 0.0, 0.0]
            #self.pub.publish(self.msg)
            #self.get_logger().info("FORWARD")
            self.publish_movement(self.msg.data, "FORWARD")
            time.sleep(0.1) # kalau sudah pakai /movement_state ini hilang aja

        #self.stop()


    def turn_left(self, steps):
        self.msg = Bool()
        self.msg.data = False
        self.pub_tetrapod_gait.publish(self.msg)
        self.msg = Float32MultiArray()
        for _ in range(steps):
            self.msg.data = [0.0, 0.0, 30.0]
            #self.pub.publish(self.msg)
            #self.get_logger().info("TURN LEFT")
            self.publish_movement(self.msg.data, "TURN LEFT")
            time.sleep(0.1)

        #self.stop()

    def turn_right(self, steps):
        self.msg = Bool()
        self.msg.data = False
        self.pub_tetrapod_gait.publish(self.msg)
        self.msg = Float32MultiArray()
        for _ in range(steps):
            self.msg.data = [0.0, 0.0, -30.0]
            #self.pub.publish(self.msg)
            #self.get_logger().info("TURN RIGHT")
            self.publish_movement(self.msg.data, "TURN RIGHT")
            time.sleep(0.1)
    
    def walk_backward(self,steps):

        self.msg = Bool()

        self.msg.data = False

        self.pub_tetrapod_gait.publish(self.msg)

        self.msg = Float32MultiArray()

        for _ in range(steps):

            self.msg.data = [-6.0,0.0,0.0]

            #self.pub.publish(self.msg)

            #self.get_logger().info("BACKWARD")
            self.publish_movement(self.msg.data, "BACKWARD")

            time.sleep(0.1)
        
    def strafe_left(self, steps):
        self.msg = Bool()
        self.msg.data = False
        self.pub_tetrapod_gait.publish(self.msg)
        self.msg = Float32MultiArray()
        for _ in range(steps):
            self.msg.data = [0.0, -5.0, 0.0]
            #self.pub.publish(self.msg)
            #self.get_logger().info("STRAFE LEFT")
            self.publish_movement(self.msg.data, "STRAFE LEFT")
            time.sleep(0.1)
    
    def strafe_right(self, steps):
        self.msg = Bool()
        self.msg.data = False
        self.pub_tetrapod_gait.publish(self.msg)
        self.msg = Float32MultiArray()
        for _ in range(steps):
            self.msg.data = [0.0, 5.0, 0.0]
            #self.pub.publish(self.msg)
            #self.get_logger().info("STRAFE RIGHT")
            self.publish_movement(self.msg.data, "STRAFE RIGHT")
            time.sleep(0.1)

        self.stop()
    
    def tetrapod_forward(self, steps):
        self.msg = Bool()
        self.msg.data = True # dia true sendiri karena dia tetrapod
        self.pub_tetrapod_gait.publish(self.msg)
        self.msg = Float32MultiArray()
        for _ in range(steps):
            self.msg.data = [6.0, 0.0, 0.0]
            #self.pub.publish(self.msg)
            #self.get_logger().info("TERAPOD FORWARD")
            self.publish_movement(self.msg.data, "TETRAPOD FORWARD")
            time.sleep(0.1)


def main(args=None):

    rclpy.init(args=args)

    node = NavigationController()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()