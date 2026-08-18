import json
import math
import os

from geometry_msgs.msg import Twist

from nav_msgs.msg import Odometry

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy

from std_msgs.msg import String

from std_srvs.srv import SetBool, Trigger

from ament_index_python.packages import get_package_share_directory

from .mission_validator import validate_mission


class WaypointController(Node):

    def __init__(self):
        super().__init__('waypoint_controller')

        self.cmd_pub = self.create_publisher(
            Twist,
            '/model/vehicle_blue/cmd_vel',
            10
        )

        self.progress_pub = self.create_publisher(
            String,
            '/mission/progress',
            10
        )
        status_qos = QoSProfile(
            depth=10,
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.TRANSIENT_LOCAL
        )
        self.status_pub = self.create_publisher(
            String,
            '/mission/status',
            status_qos
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

        default_mission = os.path.join(
            get_package_share_directory('omokai_controller'),
            'missions',
            'inspection_loop.json'
        )

        self.declare_parameter(
            'mission_file',
            default_mission
        )
        self.mission_file = self.get_parameter(
            'mission_file'
        ).value

        self.waypoints = self.load_mission(
            self.mission_file
        )

        self.current_waypoint = 0
        self.current_repeat = 0
        self.mission_completed = False
        self.mission_paused = False
        self.mission_cancelled = False
        self._last_status = None

        self.pause_service = self.create_service(
            SetBool,
            '/mission/pause',
            self.pause_callback
        )

        self.cancel_service = self.create_service(
            SetBool,
            '/mission/cancel',
            self.cancel_callback
        )

        self.status_service = self.create_service(
            Trigger,
            '/mission/get_status',
            self.status_callback
        )

        self.reset_service = self.create_service(
            Trigger,
            '/mission/reset',
            self.reset_callback
        )

        self.position_tolerance = 0.15
        self.linear_speed = 0.5
        self.angular_gain = 1.5

        self.get_logger().info('Waypoint controller started')

    def publish_status(self, status):
        if status == self._last_status:
            return

        msg = String()
        msg.data = status

        self.status_pub.publish(msg)

        self._last_status = status

    def load_mission(self, filename):
        with open(filename, 'r') as file:
            mission = json.load(file)

        valid, message = validate_mission(mission)

        if not valid:
            raise ValueError(
                f'Mission validation failed: {message}'
            )

        self.get_logger().info(
            f'Validated mission: {mission["mission"]}'
        )

        self.mission_name = mission['mission']
        self.mission_repeat = int(mission['repeat'])

        waypoints = []

        for waypoint in mission['waypoints']:
            waypoints.append(
                (
                    float(waypoint['x']),
                    float(waypoint['y'])
                )
            )

        return waypoints

    def pause_callback(self, request, response):

        self.mission_paused = request.data

        if self.mission_paused:
            response.success = True
            response.message = 'Mission paused'
            self.get_logger().info('Mission paused')
        else:
            response.success = True
            response.message = 'Mission resumed'
            self.get_logger().info('Mission resumed')

        return response

    def cancel_callback(self, request, response):

        if request.data:
            self.mission_cancelled = True
            self.cmd_pub.publish(Twist())

            response.success = True
            response.message = 'Mission cancelled'

            self.get_logger().info('Mission cancelled')

        else:
            response.success = False
            response.message = 'Cancel request must use true'

        return response

    def status_callback(self, request, response):

        if self.mission_cancelled:
            status = 'CANCELLED'
        elif self.mission_completed:
            status = 'COMPLETED'
        elif self.mission_paused:
            status = 'PAUSED'
        else:
            status = 'RUNNING'

        response.success = True
        response.message = status

        return response

    def reset_callback(self, request, response):

        self.cmd_pub.publish(Twist())

        self.current_waypoint = 0
        self.current_repeat = 0

        self.mission_completed = False
        self.mission_paused = False
        self.mission_cancelled = False

        self._last_status = None
        self._last_reported_waypoint = -1

        response.success = True
        response.message = 'Mission reset'

        self.get_logger().info('Mission reset')

        progress = String()
        progress.data = (
            f'Mission: {self.mission_name} | '
            f'Repeat: 1/{self.mission_repeat} | '
            f'Waypoint: 1/{len(self.waypoints)}'
        )
        self.progress_pub.publish(progress)

        self.publish_status('RUNNING')

        return response

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

        if self.mission_paused:
            self.publish_status('PAUSED')
            self.cmd_pub.publish(cmd)
            return

        if self.mission_cancelled:
            self.publish_status('CANCELLED')
            self.cmd_pub.publish(cmd)
            return

        if self.mission_completed:
            self.publish_status('COMPLETED')
            self.cmd_pub.publish(cmd)
            return

        if self.current_waypoint >= len(self.waypoints):

            self.current_repeat += 1

            if self.current_repeat >= self.mission_repeat:

                self.cmd_pub.publish(cmd)
                self.mission_completed = True

                self.get_logger().info(
                    'Mission completed'
                )

                progress = String()
                progress.data = (
                    f'Mission: {self.mission_name} | COMPLETED'
                )
                self.progress_pub.publish(progress)

                self.publish_status('COMPLETED')
                return

            self.get_logger().info(
                f'Repeating mission: '
                f'{self.current_repeat + 1}/{self.mission_repeat}'
            )

            self.current_waypoint = 0
            self.publish_status('RUNNING')
            return

        self.publish_status('RUNNING')

        target_x, target_y = self.waypoints[self.current_waypoint]

        if self.current_waypoint != getattr(
            self, '_last_reported_waypoint', -1
        ):

            progress = String()
            progress.data = (
                f'Mission: {self.mission_name} | '
                f'Repeat: {self.current_repeat + 1}/{self.mission_repeat} | '
                f'Waypoint: {self.current_waypoint + 1}/{len(self.waypoints)}'
            )

            self.progress_pub.publish(progress)

            self._last_reported_waypoint = self.current_waypoint

        dx = target_x - self.x
        dy = target_y - self.y

        distance = math.sqrt(
            dx * dx + dy * dy
        )

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

        # -------------------------------------------------
        # 1. Rotate in place if the heading error is large
        # -------------------------------------------------
        heading_threshold = 0.15

        if abs(angle_error) > heading_threshold:

            cmd.linear.x = 0.0

            cmd.angular.z = (
                self.angular_gain * angle_error
            )

            cmd.angular.z = max(
                -1.5,
                min(1.5, cmd.angular.z)
            )

            self.cmd_pub.publish(cmd)
            return

        # -------------------------------------------------
        # 2. Move toward waypoint once heading is aligned
        # -------------------------------------------------

        cmd.angular.z = (
            self.angular_gain * angle_error
        )

        cmd.angular.z = max(
            -1.0,
            min(1.0, cmd.angular.z)
        )

        # Slow down when approaching waypoint
        if distance < 0.5:
            cmd.linear.x = 0.2
        else:
            cmd.linear.x = self.linear_speed

        self.cmd_pub.publish(cmd)

def main(args=None):

    rclpy.init(args=args)

    node = WaypointController()

    try:
        while rclpy.ok() and not node.mission_completed:
            rclpy.spin_once(
                node,
                timeout_sec=0.1
            )

    except KeyboardInterrupt:
        pass

    finally:
        if rclpy.ok():
            node.cmd_pub.publish(Twist())

        node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
