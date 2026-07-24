import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray

import time
from std_msgs.msg import Bool
from std_msgs.msg import Float32MultiArray, Int32MultiArray


class LocationStateChecker(Node):

    def __init__(self):
        super().__init__('location_state_checker')

        self.roll=0.0
        self.pitch=0.0
        self.yaw=0.0

        self.left_front = 0.0
        self.left = 0.0
        self.left_rear = 0.0

        self.back = 0.0

        self.right_front = 0.0
        self.right = 0.0

        self.front = 0.0

        # 1=A,2=B_beta,3=B,4=C,5=D,6=E,7=F
        self.state=1
        self.state_str = "A"
        self.cv_location_state = 0.0 # location state dari computer vision

        # ---------- Timeout Variables ----------

        self.motion_complete = False

        self.cv_progress = 0.0
        self.prev_cv_state = None
        self.max_progress = 0.0

        self.progress_timeout = 60.0      # seconds
        self.progress_threshold = 0.01

        self.last_progress_time = time.time()

        self.pub_timeout = self.create_publisher(
            Bool,
            "/navigation_timeout",
            10
        )

        self.create_subscription(
            Bool,
            "/motion_complete",
            self.motion_complete_callback,
            10
        )

        self.pub=self.create_publisher(Float32MultiArray,'/location_state',1)

        self.create_subscription(Float32MultiArray,'/rpy',self.rpy_cb,1)
        self.create_subscription(
            Int32MultiArray,
            "/ultrasonic",
            self.ultrasonic_cb,
            1
        )
        self.create_subscription(Float32MultiArray,'/cv_location_state',self.cv_location_state_callback,1)

        self.create_timer(0.05,self.check_state)
        #self.create_timer(
        #    0.2,
        #    self.timeout_monitor
        #)
        self.publish_state(self.state,"A")


    # ---------- Callbacks ----------

    def cv_location_state_callback(self, msg):

        if len(msg.data) >= 2:

            self.cv_location_state = msg.data[0]
            self.cv_progress = msg.data[1]
    
    def motion_complete_callback(self, msg):

        self.motion_complete = msg.data

    def rpy_cb(self,msg):
        if len(msg.data)>=3:
            self.roll,self.pitch,self.yaw=msg.data[:3]

    def ultrasonic_cb(self, msg):

        if len(msg.data) < 7:
            return

        self.left_front = float(msg.data[0]) #original LF = 0
        self.left       = float(msg.data[5]) #original L = 1
        self.left_rear  = float(msg.data[3]) #original LR = 2
        self.back       = float(msg.data[6]) #original B = 3
        self.right_front= float(msg.data[4]) #original RF = 4
        self.right      = float(msg.data[1]) #original R = 5
        self.front      = float(msg.data[2]) #original F = 6

    # ---------- Helper ----------

    def ready(self):
        return None not in (
            self.left_front,
            self.left,
            self.left_rear,
            self.back,
            self.right_front,
            self.right,
            self.front
        )

    def yaw0(self):
        return 0.0<=self.yaw<=10.0 or 360 > self.yaw >= 350

    def yaw90(self):
        return 80<=self.yaw<=100

    def yaw180(self):
        return self.yaw>=170 or self.yaw<=-170

    def publish_state(self,state,name):
        msg=Float32MultiArray()
        msg.data=[float(state),0.0]
        self.pub.publish(msg)

        self.get_logger().info(
            f"Try(joystick)=({1})"
            f"State={name} | "
            f"Yaw={self.yaw:.1f} Pitch={self.pitch:.1f} | "
            f"LF={self.left_front:.1f}"
            f"L={self.left:.1f}"
            f"LR={self.left_rear:.1f}"
            f"B={self.back:.1f}"
            f"RF={self.right_front:.1f}"
            f"R={self.right:.1f}"
            f"F={self.front:.1f}"
        )
    def publish_state_2(self):
        msg=Float32MultiArray()
        msg.data=[float(self.state),0.0]
        self.pub.publish(msg)

        self.get_logger().info(
            f"Try(teleop)=({1})"
            f"State={self.state_str} | "
            f"Yaw={self.yaw:.1f} Pitch={self.pitch:.1f} | "
            f"LF={self.left_front:.1f}"
            f"L={self.left:.1f}"
            f"LR={self.left_rear:.1f}"
            f"B={self.back:.1f}"
            f"RF={self.right_front:.1f}"
            f"R={self.right:.1f}"
            f"F={self.front:.1f}"
        )

    def change_state(self,new_state,name):
        self.state = new_state
        self.state_str = name 
        #self.publish_state(new_state,name)
        self.publish_state_2()

    def timeout_monitor(self):

        # Robot still moving
        if not self.motion_complete:

            self.last_progress_time = time.time()
            return

        # First CV sample
        if self.prev_cv_state is None:

            self.prev_cv_state = self.cv_location_state
            self.max_progress = self.cv_progress
            self.last_progress_time = time.time()
            return

        # Robot entered another CV section
        if self.cv_location_state != self.prev_cv_state:

            self.prev_cv_state = self.cv_location_state
            self.max_progress = self.cv_progress
            self.last_progress_time = time.time()

            self.publish_timeout(False)

            return

        # Progress increased
        if self.cv_progress > self.max_progress + self.progress_threshold:

            self.max_progress = self.cv_progress
            self.last_progress_time = time.time()

            self.publish_timeout(False)

            return

        # Timeout
        elapsed = time.time() - self.last_progress_time

        if elapsed >= self.progress_timeout:

            self.publish_timeout(True)

        else:

            self.publish_timeout(False)
    
    def publish_timeout(self, value):

        msg = Bool()

        msg.data = value

        self.pub_timeout.publish(msg)

    # ---------- FSM ----------

    def check_state(self):

        if not self.ready():
            self.get_logger().info("Waiting for ultrasonic readings...")
            return

        front=self.front
        left=self.left
        right=self.right
        back=self.back

        # Ignore invalid ultrasonic readings
        if front<0 or left<0 or right<0 or back<0:
            self.get_logger().info("Invalid ultrasonic readings, ignoring...")
            return

        #==========================
        # A -> B_beta
        #==========================
        if self.state==1:

            if self.yaw0() and back<85 and (20<=front<80):
                if self.pitch>13.0:
                    self.change_state(2, "B_beta") # kita make ini buat tetrapod di kemiringan
                return
                
            #self.publish_state(1,"A") # maju

            else:
                self.change_state(1,"A")


        #==========================
        # B_beta -> B
        #==========================
        elif self.state==2:

            if -1<=self.pitch<=1 and front <= 7:
                self.change_state(3,"B") # putar kiri

        #==========================
        # B -> B_next
        # Rotate until facing 90°
        #==========================
        elif self.state==3:

            if self.yaw90():
                self.change_state(4,"B_next") # maju

        #==========================
        # B_next -> C
        # Check side/back distances
        #==========================
        elif self.state==4:

            if back>55 and (left<28 or right<28):
                self.change_state(5,"C") # maju

        #==========================
        # C -> D
        #==========================
        elif self.state==5:

            if self.yaw90() and back>75 and front<12:
                self.change_state(6,"D") # putar kiri

        #==========================
        # D -> D_next
        # Rotate until facing 180°
        #==========================
        elif self.state==6:

            if self.yaw180():
                self.change_state(7,"D_next") # maju

        #==========================
        # D_next -> E
        #==========================
        elif self.state==7:

            if back>55 and front<15 and right<15:
                self.change_state(8,"E") # stop

        #==========================
        # E -> F
        #==========================
        elif self.state==8:

            if back>60 and front<12 and right<20:
                self.change_state(9,"F") # stop

        #==========================
        # Finished
        #==========================
        elif self.state==9:
            pass

        self.publish_state_2()


def main(args=None):
    rclpy.init(args=args)
    node=LocationStateChecker()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__=="__main__":
    main()