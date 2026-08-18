import json
import sys


def validate_mission(mission):
    if not isinstance(mission, dict):
        return False, 'Mission must be a JSON object'

    required = ['version', 'mission', 'repeat', 'waypoints']

    for field in required:
        if field not in mission:
            return False, f'Missing field: {field}'

    if not isinstance(mission['version'], str):
        return False, 'version must be a string'

    if not isinstance(mission['mission'], str):
        return False, 'mission must be a string'

    if not isinstance(mission['repeat'], int):
        return False, 'repeat must be an integer'

    if mission['repeat'] < 1 or mission['repeat'] > 10:
        return False, 'repeat must be between 1 and 10'

    waypoints = mission['waypoints']

    if not isinstance(waypoints, list):
        return False, 'waypoints must be a list'

    if len(waypoints) < 2:
        return False, 'At least two waypoints are required'

    for i, waypoint in enumerate(waypoints):

        if not isinstance(waypoint, dict):
            return False, f'Waypoint {i} must be an object'

        if 'x' not in waypoint or 'y' not in waypoint:
            return False, f'Waypoint {i} requires x and y'

        if not isinstance(waypoint['x'], (int, float)):
            return False, f'Waypoint {i} x must be numeric'

        if not isinstance(waypoint['y'], (int, float)):
            return False, f'Waypoint {i} y must be numeric'

    return True, 'Mission is valid'


def main():

    if len(sys.argv) != 2:
        print('Usage: python3 mission_validator.py <mission.json>')
        sys.exit(1)

    filename = sys.argv[1]

    try:
        with open(filename, 'r') as file:
            mission = json.load(file)
    except (OSError, json.JSONDecodeError) as error:
        print(f'Invalid JSON: {error}')
        sys.exit(1)

    valid, message = validate_mission(mission)

    if valid:
        print(f'PASS: {message}')
        sys.exit(0)
    else:
        print(f'FAIL: {message}')
        sys.exit(1)


if __name__ == '__main__':
    main()
