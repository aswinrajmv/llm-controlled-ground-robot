import json
import os
import signal
import subprocess
import sys
import tempfile
import time

import requests

from mission_validator import validate_mission


OLLAMA_URL = 'http://localhost:11434/api/generate'
MODEL = 'qwen2.5:3b'

WAYPOINTS = [
    {'x': 2.0, 'y': 0.0},
    {'x': 2.0, 'y': 2.0},
    {'x': 0.0, 'y': 2.0},
    {'x': 0.0, 'y': 0.0}
]

from ament_index_python.packages import get_package_share_directory
PACKAGE_SHARE = get_package_share_directory('omokai_controller')

LAUNCH_FILE = os.path.join(
    PACKAGE_SHARE,
    'launch',
    'omokai.launch.py'
)
launch_process = None


def generate_mission(prompt):
    """Use the LLM only to interpret operator intent."""

    llm_prompt = (
        'You are a robot mission planner. '
        'The robot only supports an inspection_loop mission. '
        'Determine whether the operator command can be performed. '
        'If it can, determine the number of repetitions. '
        'Return ONLY JSON in this exact format: '
        '{"supported":true,"repeat":3} '
        'or, if unsupported: '
        '{"supported":false} '
        'Operator command: '
        + prompt
    )

    print('Calling local LLM...')

    response = requests.post(
        OLLAMA_URL,
        json={
            'model': MODEL,
            'prompt': llm_prompt,
            'stream': False,
            'format': 'json',
            'options': {
                'temperature': 0,
                'num_predict': 10
            }
        },
        timeout=120
    )

    response.raise_for_status()

    data = response.json()
    llm_output = data['response']

    print('LLM OUTPUT:')
    print(llm_output)
    print()

    result = json.loads(llm_output)

    if not result.get('supported', False):
        raise ValueError(
            'Operator command is not supported by the robot.'
        )

    repeat = int(result['repeat'])

    mission = {
        'version': '1.0',
        'mission': 'inspection_loop',
        'repeat': repeat,
        'waypoints': WAYPOINTS
    }

    return mission


def start_simulation():
    """Start Gazebo and the ROS-Gazebo bridges."""

    global launch_process

    print('Starting Omokai simulation...')
    print()

    launch_process = subprocess.Popen([
        'ros2',
        'launch',
        'omokai_controller',
        'omokai.launch.py'
    ])

    print('Waiting for simulation...')
    
    for _ in range(30):
        try:
            result = subprocess.run(
                [
                    'ros2',
                    'topic',
                    'info',
                    '/model/vehicle_blue/odometry'
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
                timeout=3
            )

            if 'Publisher count: 1' in result.stdout:
                print('Simulation is ready.')
                print()
                return

        except subprocess.TimeoutExpired:
            pass

        time.sleep(1)

    raise RuntimeError(
        'Simulation did not become ready within 30 seconds.'
    )


def stop_simulation():
    """Stop the automatically started simulation."""

    global launch_process

    if launch_process is not None:
        print()
        print('Stopping Omokai simulation...')

        try:
            launch_process.send_signal(signal.SIGINT)
            launch_process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            launch_process.terminate()

        launch_process = None


def main():

    if len(sys.argv) < 2:
        print('Usage:')
        print(
            'python3 run_mission.py '
            '"Drive the inspection route three times"'
        )
        sys.exit(1)

    prompt = ' '.join(sys.argv[1:])

    print()
    print('PROMPT:')
    print(prompt)
    print()

    try:

        # Start simulation automatically.
        start_simulation()

        # Ask the local LLM to interpret the command.
        mission = generate_mission(prompt)

        print('GENERATED MISSION:')
        print(json.dumps(mission, indent=2))
        print()

        # Validate before execution.
        valid, message = validate_mission(mission)

        print('VALIDATION:')
        print(message)
        print()

        if not valid:
            print('Mission rejected.')
            stop_simulation()
            sys.exit(1)

        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.json',
            delete=False
        ) as file:

            json.dump(mission, file, indent=2)
            mission_file = file.name

        print(f'Validated mission saved to: {mission_file}')
        print()
        print('Starting deterministic executor...')
        print()

        result = subprocess.run([
            'ros2',
            'run',
            'omokai_controller',
            'square_controller',
            '--ros-args',
            '-p',
            f'mission_file:={mission_file}'
        ])

        print()
        print('Mission executor finished.')

        stop_simulation()

        sys.exit(result.returncode)

    except KeyboardInterrupt:
        print()
        print('Mission interrupted by operator.')
        stop_simulation()
        sys.exit(1)

    except Exception as error:
        print()
        print(f'ERROR: {error}')
        stop_simulation()
        sys.exit(1)


if __name__ == '__main__':
    main()
