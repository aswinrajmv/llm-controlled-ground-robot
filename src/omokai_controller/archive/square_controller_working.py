import math

import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry


class WaypointController(Node):

    def __init__(self):
        super().__init__('waypoint_controller')

        self.cmd_pub = self.create_publisher(
            Twist,
            '/model/vehicle_blue/cmd_vel',
            10
        )

        self.odom_sub = self.create_subscription(
            Odometry,
            '/model/vehicle_blue/odometry',
            self.odom_callback,
            10
        )

        self.timer = self.create_timer(0.05, self.control_loop)

        self.x = 0.0
        self.y = 0.0
        self.yaw = 0.0

        self.waypoints = [
            (2.0, 0.0),
            (2.0, 2.0),
            (0.0, 2.0),
            (0.0, 0.0),
        ]

        self.current_waypoint = 0

        self.position_tolerance = 0.15
        self.linear_speed = 0.5
        self.angular_gain = 1.5

        self.get_logger().info('Waypoint controller started')

    def odom_callback(self, msg):

        self.x = msg.pose.pose.position.x
        self.y = msg.pose.pose.position.y

        q = msg.pose.pose.orientation

        # Quaternion -> yaw
        sin_yaw = 2.0 * (q.w * q.z + q.x * q.y)
        cos_yaw = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)

        self.yaw = math.atan2(sin_yaw, cos_yaw)

    def normalize_angle(self, angle):

        while angle > math.pi:
            angle -= 2.0 * math.pi

        while angle < -math.pi:
            angle += 2.0 * math.pi

        return angle

    def control_loop(self):

        cmd = Twist()

        if self.current_waypoint >= len(self.waypoints):

            self.cmd_pub.publish(cmd)
            return

        target_x, target_y = self.waypoints[self.current_waypoint]

        dx = target_x - self.x
        dy = target_y - self.y

        distance = math.sqrt(dx * dx + dy * dy)

        if distance < self.position_tolerance:

            self.get_logger().info(
                f'Reached waypoint {self.current_waypoint + 1}: '
                f'({target_x}, {target_y})'
            )

            self.current_waypoint += 1

            return

        target_angle = math.atan2(dy, dx)

        angle_error = self.normalize_angle(
            target_angle - self.yaw
        )

        cmd.linear.x = self.linear_speed

        cmd.angular.z = self.angular_gain * angle_error

        # Limit angular velocity
        cmd.angular.z = max(
            -1.5,
            min(1.5, cmd.angular.z)
        )

        self.cmd_pub.publish(cmd)


def main(args=None):

    rclpy.init(args=args)

    node = WaypointController()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    finally:

        node.cmd_pub.publish(Twist())

        node.destroy_node()

        rclpy.shutdown()


if __name__ == '__main__':
    main()
