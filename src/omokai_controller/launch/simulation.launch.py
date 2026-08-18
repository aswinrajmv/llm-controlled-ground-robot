from launch import LaunchDescription
from launch.actions import ExecuteProcess


def generate_launch_description():
    return LaunchDescription([
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
        )
    ])
