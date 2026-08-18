def test_mission_initial_state():

    mission_completed = False
    mission_paused = False
    mission_cancelled = False

    assert mission_completed is False
    assert mission_paused is False
    assert mission_cancelled is False


def test_pause_state():

    mission_paused = False

    mission_paused = True

    assert mission_paused is True

    mission_paused = False

    assert mission_paused is False


def test_cancel_state():

    mission_cancelled = False

    mission_cancelled = True

    assert mission_cancelled is True


def test_reset_state():

    current_waypoint = 3
    current_repeat = 2

    mission_completed = True
    mission_paused = True
    mission_cancelled = True

    current_waypoint = 0
    current_repeat = 0

    mission_completed = False
    mission_paused = False
    mission_cancelled = False

    assert current_waypoint == 0
    assert current_repeat == 0
    assert mission_completed is False
    assert mission_paused is False
    assert mission_cancelled is False


def test_mission_completion():

    current_waypoint = 4
    total_waypoints = 4

    current_repeat = 2
    total_repeats = 3

    assert current_waypoint >= total_waypoints
    assert current_repeat < total_repeats


def test_final_repeat_completion():

    current_waypoint = 4
    total_waypoints = 4

    current_repeat = 3
    total_repeats = 3

    assert current_waypoint >= total_waypoints
    assert current_repeat >= total_repeats
