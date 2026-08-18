import json

from mission_validator import validate_mission


def load_mission(filename):

    with open(filename, 'r') as file:
        mission = json.load(file)

    valid, message = validate_mission(mission)

    if not valid:
        raise ValueError(f'Invalid mission: {message}')

    return mission


def main():

    filename = (
        '/home/aswin/omokai_ws/src/'
        'omokai_controller/missions/inspection_loop.json'
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
