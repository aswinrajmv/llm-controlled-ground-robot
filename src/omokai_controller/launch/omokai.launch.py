import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch_ros.actions import Node


def generate_launch_description():
    package_share = get_package_share_directory(
        'omokai_controller'
    )

    models_dir = os.path.join(
        package_share,
        'simulation',
        'models'
    )

    world_file = os.path.join(
        package_share,
        'simulation',
        'worlds',
        'ground_robot_world.sdf'
    )

    resource_path = os.environ.get('GZ_SIM_RESOURCE_PATH', '')

    if resource_path:
        resource_path = f'{models_dir}:{resource_path}'
    else:
        resource_path = models_dir

    gazebo_env = os.environ.copy()
    gazebo_env['GZ_SIM_RESOURCE_PATH'] = resource_path
    gazebo_env['LIBGL_ALWAYS_SOFTWARE'] = '1'

    return LaunchDescription([

        # Start Gazebo simulation.
        ExecuteProcess(
            cmd=[
                'gz',
                'sim',
                '-r',
                world_file,
            ],
            additional_env=gazebo_env,
            output='screen'
        ),

        # Gazebo <-> ROS bridges.
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
