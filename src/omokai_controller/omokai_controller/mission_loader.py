import json
import os

from ament_index_python.packages import get_package_share_directory

from .mission_validator import validate_mission


def load_mission(filename):
    """Load and validate a mission JSON file."""
    with open(filename, 'r', encoding='utf-8') as file:
        mission = json.load(file)

    valid, message = validate_mission(mission)

    if not valid:
        raise ValueError(f'Invalid mission: {message}')

    return mission


def main():
    """Load the default inspection mission and display it."""
    package_share = get_package_share_directory(
        'omokai_controller'
    )

    filename = os.path.join(
        package_share,
        'missions',
        'inspection_loop.json'
    )

    mission = load_mission(filename)

    print('Mission loaded successfully')
    print(f"Mission: {mission['mission']}")
    print(f"Repeat: {mission['repeat']}")
    print('Waypoints:')

    for i, waypoint in enumerate(mission['waypoints'], 1):
        print(
            f'  {i}: '
            f"x={waypoint['x']}, "
            f"y={waypoint['y']}"
        )


if __name__ == '__main__':
    main()
