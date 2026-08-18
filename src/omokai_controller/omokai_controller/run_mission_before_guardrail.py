import json
import subprocess
import sys
import tempfile

import requests

from mission_validator import validate_mission


WAYPOINTS = [
    {'x': 2.0, 'y': 0.0},
    {'x': 2.0, 'y': 2.0},
    {'x': 0.0, 'y': 2.0},
    {'x': 0.0, 'y': 0.0}
]


def generate_mission(prompt):
    """Use the local Qwen LLM to determine the mission repeat count."""

    llm_prompt = f"""
You are a robot mission planner.

The robot can only perform an inspection_loop mission.

Determine how many times the inspection loop should be repeated
from the operator command.

Return ONLY valid JSON in exactly this format:

{{"repeat": NUMBER}}

Operator command:
{prompt}
"""

    print('Calling local LLM...')

    response = requests.post(
        'http://localhost:11434/api/generate',
        json={
            'model': 'qwen2.5:3b',
            'prompt': llm_prompt,
            'stream': False,
            'format': 'json',
            'options': {
                'temperature': 0,
                'num_predict': 20
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
