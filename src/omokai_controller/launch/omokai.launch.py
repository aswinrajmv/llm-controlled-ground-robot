from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([

        # Start Gazebo simulation
        ExecuteProcess(
            cmd=[
                'bash',
                '-c',
                (
                    'cd ~/omokai_ws && '
                    'source /opt/ros/lyrical/setup.bash && '
                    'source ~/omokai_ws/install/setup.bash && '
                    'export GZ_SIM_RESOURCE_PATH='
                    '$GZ_SIM_RESOURCE_PATH:'
                    '$HOME/omokai_ws/src/omokai_controller/simulation/models && '
                    'LIBGL_ALWAYS_SOFTWARE=1 '
                    'gz sim -r '
                    '~/omokai_ws/src/omokai_controller/'
                    'simulation/worlds/omokai_world.sdf'
                )
            ],
            output='screen'
        ),

        # Gazebo <-> ROS bridges
        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            arguments=[
                '/model/vehicle_blue/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist',
                '/model/vehicle_blue/odometry@nav_msgs/msg/Odometry@gz.msgs.Odometry',
            ],
            output='screen'
        ),
    ])
