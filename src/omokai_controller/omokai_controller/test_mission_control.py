import time

import rclpy
from rclpy.node import Node

from std_srvs.srv import SetBool, Trigger


class MissionControlTester(Node):

    def __init__(self):
        super().__init__('mission_control_tester')

        self.pause_client = self.create_client(
            SetBool,
            '/mission/pause'
        )

        self.cancel_client = self.create_client(
            SetBool,
            '/mission/cancel'
        )

        self.reset_client = self.create_client(
            Trigger,
            '/mission/reset'
        )

        self.status_client = self.create_client(
            Trigger,
            '/mission/get_status'
        )

    def call_status(self):

        if not self.status_client.wait_for_service(timeout_sec=3.0):
            return None

        future = self.status_client.call_async(
            Trigger.Request()
        )

        rclpy.spin_until_future_complete(
            self,
            future,
            timeout_sec=3.0
        )

        if future.result() is None:
            return None

        return future.result().message

    def call_pause(self, value):

        if not self.pause_client.wait_for_service(timeout_sec=3.0):
            return None

        request = SetBool.Request()
        request.data = value

        future = self.pause_client.call_async(request)

        rclpy.spin_until_future_complete(
            self,
            future,
            timeout_sec=3.0
        )

        if future.result() is None:
            return None

        return future.result().message

    def call_cancel(self):

        if not self.cancel_client.wait_for_service(timeout_sec=3.0):
            return None

        request = SetBool.Request()
        request.data = True

        future = self.cancel_client.call_async(request)

        rclpy.spin_until_future_complete(
            self,
            future,
            timeout_sec=3.0
        )

        if future.result() is None:
            return None

        return future.result().message

    def call_reset(self):

        if not self.reset_client.wait_for_service(timeout_sec=3.0):
            return None

        future = self.reset_client.call_async(
            Trigger.Request()
        )

        rclpy.spin_until_future_complete(
            self,
            future,
            timeout_sec=3.0
        )

        if future.result() is None:
            return None

        return future.result().message


def check(name, actual, expected):

    if actual == expected:
        print(f'[PASS] {name}: {actual}')
        return True

    print(
        f'[FAIL] {name}: '
        f'expected={expected}, actual={actual}'
    )

    return False


def main():

    rclpy.init()

    node = MissionControlTester()

    results = []

    print()
    print('=== Mission Control Test ===')
    print()

    time.sleep(1.0)

    status = node.call_status()
    results.append(
        check(
            'Initial status',
            status,
            'RUNNING'
        )
    )

    node.call_pause(True)

    time.sleep(0.2)

    status = node.call_status()

    results.append(
        check(
            'Pause',
            status,
            'PAUSED'
        )
    )

    node.call_pause(False)

    time.sleep(0.2)

    status = node.call_status()

    results.append(
        check(
            'Resume',
            status,
            'RUNNING'
        )
    )

    node.call_cancel()

    time.sleep(0.2)

    status = node.call_status()

    results.append(
        check(
            'Cancel',
            status,
            'CANCELLED'
        )
    )

    node.call_reset()

    time.sleep(0.2)

    status = node.call_status()

    results.append(
        check(
            'Reset',
            status,
            'RUNNING'
        )
    )

    passed = sum(results)
    total = len(results)

    print()
    print(f'{passed}/{total} TESTS PASSED')

    if passed == total:
        print('MISSION CONTROL: PASS')
    else:
        print('MISSION CONTROL: FAIL')

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
