#!/usr/bin/env python3
import sys, select, termios, tty, rclpy
from std_msgs.msg import Float32MultiArray


settings = termios.tcgetattr(sys.stdin)


def getKey():
    tty.setraw(sys.stdin.fileno())
    select.select([sys.stdin], [], [], 0)
    key = sys.stdin.read(1)
    if key == '\x1b':
        key += sys.stdin.read(2)
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key


def status(distance):
	return "currently:\tforward distance %s\t strafe distance %s" % (distance[0], distance[1])

msg = """
Reading from the keyboard  and Publishing!
---------------------------
Moving dan strafing
   q    w    e
   a    s    d
   z    x    c
Moving dan strafing

w : forward
s : stop
x : backward

a : turn left 30 degree
d : turn right 30 degree
q : turn left 10 degree
e : turn right 10 degree

z : strafe left
c : strafe right

^/v (arrow key) : increase/decrease forward steps distance by 0.1
>/< (arrow key) : increase/decrease strafe steps distance by 0.1

minimum and maximum distance = 0 & 6 cm

CTRL-C to quit
"""

moveBindings = {
		'w':(1.0, 0.0, 0.0),
        'x':(-1.0, 0.0, 0.0),
		'a':(0.0, 0.0, 30.0),
		'd':(0.0, 0.0, -30.0),
        'q':(0.0, 0.0, 10.0),
        'e':(0.0, 0.0, -10.0),
		's':(0.0, 0.0, 0.0),
		'z':(0.0, -1.0, 0.0),
		'c':(0.0, 1.0, 0.0)
	       }

distanceBindings={
		'\x1b[A':(0.1, 0.0), #up arrow
		'\x1b[B':(-0.1, 0.0), #down arrow
		'\x1b[C':(0.0, 0.1), #right arrow
		'\x1b[D':(0.0, -0.1) #left arrow
	      }

def main(args=None):
    rclpy.init(args=args)
    node = rclpy.create_node('hectarus_teleop_key')
    publish_key = node.create_publisher(Float32MultiArray, '/cmd_movement', 1)

    distance = [6.0, 5.0] #forward, strafe
    try:
        print(msg)
        print(status(distance))
        while(1):
            key= getKey()
            if key in moveBindings.keys():
                message = Float32MultiArray()
                message.data = [moveBindings[key][0]*distance[0], moveBindings[key][1]*distance[1], moveBindings[key][2]]
                publish_key.publish(message)
            elif key in distanceBindings.keys():
                distance = [round(min(max(distance[0] + distanceBindings[key][0],0.0),6.0),1), round(min(max(distance[1] + distanceBindings[key][1],0.0),5.0),1)] 
                print(status(distance))
            else:
                if (key == '\x03'):
                    print("Exit Hectarus Teleop Key")
                    break

    except Exception as e:
        print

    finally:
        message = Float32MultiArray()
        message.data = [0.0, 0.0, 0.0]
        publish_key.publish(message)
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)

if __name__ == '__main__':
     main()

# batas