import json
import sys


def generate_mission(prompt):
    """
    Convert a natural-language prompt into a structured mission.

    This is a deterministic placeholder for the future LLM.
    The LLM will eventually replace this function.
    """

    prompt = prompt.lower()

    if 'inspection' in prompt and 'three' in prompt:
        repeat = 3
    elif 'inspection' in prompt and 'twice' in prompt:
        repeat = 2
    elif 'inspection' in prompt:
        repeat = 1
    else:
        raise ValueError(
            'Unable to understand the requested mission'
        )

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
        print(
            'Usage: python3 mission_generator.py '
            '"natural language command"'
        )
        sys.exit(1)

    prompt = ' '.join(sys.argv[1:])

    try:
        mission = generate_mission(prompt)
    except ValueError as error:
        print(f'ERROR: {error}')
        sys.exit(1)

    print(json.dumps(mission, indent=2))


if __name__ == '__main__':
    main()

