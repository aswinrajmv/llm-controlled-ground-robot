import json
import subprocess
import sys
import tempfile

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
        mission = generate_mission(prompt)

    except Exception as error:
        print()
        print(f'LLM ERROR: {error}')
        sys.exit(1)

    print('GENERATED MISSION:')
    print(json.dumps(mission, indent=2))
    print()

    valid, message = validate_mission(mission)

    print('VALIDATION:')
    print(message)
    print()

    if not valid:
        print('Mission rejected.')
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

    subprocess.run([
        'ros2',
        'run',
        'omokai_controller',
        'square_controller',
        '--ros-args',
        '-p',
        f'mission_file:={mission_file}'
    ])


if __name__ == '__main__':
    main()
