import json
import subprocess
import sys
import tempfile

from mission_validator import validate_mission


def generate_mission(prompt):
    """
    Generate a structured mission from a natural-language prompt.

    This is the deterministic placeholder for the LLM.
    Later, this function will be replaced by an actual LLM call.
    """

    prompt_lower = prompt.lower()

    if 'three times' in prompt_lower or '3 times' in prompt_lower:
        repeat = 3
    elif 'twice' in prompt_lower or '2 times' in prompt_lower:
        repeat = 2
    else:
        repeat = 1

    mission = {
        'version': '1.0',
        'mission': 'inspection_loop',
        'repeat': repeat,
        'waypoints': [
            {'x': 2.0, 'y': 0.0},
            {'x': 2.0, 'y': 2.0},
            {'x': 0.0, 'y': 2.0},
            {'x': 0.0, 'y': 0.0}
        ]
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

    mission = generate_mission(prompt)

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
