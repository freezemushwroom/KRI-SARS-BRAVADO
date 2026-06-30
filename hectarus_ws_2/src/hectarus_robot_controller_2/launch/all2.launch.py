from launch import LaunchDescription
import launch_ros.actions


def generate_launch_description():
    return LaunchDescription([
        launch_ros.actions.Node(
            package = 'hectarus_robot_controller_2', executable= 'process_node'),
        launch_ros.actions.Node(
            package = 'hectarus_robot_controller_2', executable = 'strafe_gait_node'),
        launch_ros.actions.Node(
            package = 'hectarus_robot_controller_2', executable = 'tripod_gait_node'),
        launch_ros.actions.Node(
            package = 'hectarus_robot_controller_2', executable = 'gait_node'),
#        launch_ros.actions.Node(
#            package = 'hectarus_robot_controller_2', executable = 'wave_gait_node'),
#        launch_ros.actions.Node(
#            package = 'hectarus_robot_controller_2', executable = 'tetrapod_gait_node'),
        launch_ros.actions.Node(
            package = 'hectarus_robot_controller_2', executable = 'turn_gait_node'),
#        launch_ros.actions.Node(
#            package = 'hectarus_robot_controller_2', executable = 'tetrapod_gait_tangga_node'),
        launch_ros.actions.Node(
            package = 'hectarus_robot_controller_2', executable = 'count_time_node'),
        launch_ros.actions.Node(
            package = 'hectarus_robot_controller_2', executable = 'stop_gait_node'),
        launch_ros.actions.Node(
            package = 'hectarus_robot_controller_2', executable = 'gyro_node')
        ])
