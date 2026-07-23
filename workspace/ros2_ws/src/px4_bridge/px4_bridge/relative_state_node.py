#!/usr/bin/env python3

import math

import rclpy
from rclpy.node import Node

from px4_msgs.msg import VehicleLocalPosition
from px4_msgs.msg import VehicleAttitude

from interfaces.msg import UAVState, PlatformState, RLObservation

from rclpy.qos import QoSProfile
from rclpy.qos import ReliabilityPolicy
from rclpy.qos import HistoryPolicy
from rclpy.qos import DurabilityPolicy

class RelativeStateNode(Node):

    def __init__(self):

        super().__init__("relative_state_node")

        self.position = None
        self.attitude = None

        self.get_logger().info("Relative State Node Started")

        px4_qos = QoSProfile(
           reliability=ReliabilityPolicy.BEST_EFFORT,
           durability=DurabilityPolicy.VOLATILE,
           history=HistoryPolicy.KEEP_LAST,
           depth=1
           )

        self.create_subscription(
            VehicleLocalPosition,
            "/fmu/out/vehicle_local_position_v1",
            self.position_callback,
            px4_qos
        )

        self.create_subscription(
            VehicleAttitude,
            "/fmu/out/vehicle_attitude",
            self.attitude_callback,
            px4_qos
        )

        self.publisher = self.create_publisher(
            UAVState,
            "/uav/state",
            10,
        )

        self.timer = self.create_timer(
            0.05,
            self.publish_state,
        )



    def position_callback(self, msg):
        self.position = msg


    def attitude_callback(self, msg):
        self.attitude = msg


    def quaternion_to_euler(self, q):

        w = q[0]
        x = q[1]
        y = q[2]
        z = q[3]

        t0 = +2.0 * (w*x + y*z)
        t1 = +1.0 - 2.0*(x*x + y*y)
        roll = math.atan2(t0, t1)

        t2 = +2.0*(w*y - z*x)
        t2 = max(min(t2, 1.0), -1.0)
        pitch = math.asin(t2)

        t3 = +2.0*(w*z + x*y)
        t4 = +1.0 - 2.0*(y*y + z*z)
        yaw = math.atan2(t3, t4)

        return roll, pitch, yaw


    def publish_state(self):

        if self.position is None:
            return

        if self.attitude is None:
            return

        msg = UAVState()

        msg.x = float(self.position.x)
        msg.y = float(self.position.y)
        msg.z = float(self.position.z)

        msg.vx = float(self.position.vx)
        msg.vy = float(self.position.vy)
        msg.vz = float(self.position.vz)

        roll, pitch, yaw = self.quaternion_to_euler(self.attitude.q)

        msg.roll = roll
        msg.pitch = pitch
        msg.yaw = yaw

        self.publisher.publish(msg)


def main():

    rclpy.init()

    node = RelativeStateNode()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == "__main__":
    main()
