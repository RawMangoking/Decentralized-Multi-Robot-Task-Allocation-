import sys
import random
import json

from pysyncobj import SyncObj
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

from swarm_agent.layout import BOXES, DELIVERY_POINTS


class FleetManagerCore(SyncObj):
    def __init__(self, self_address, partner_addrs):
        super().__init__(self_address, partner_addrs)


class FleetManagerNode(Node):
    def __init__(self, raft_core):
        super().__init__('fleet_manager')
        self.raft = raft_core
        self.announce_pub = self.create_publisher(String, '/tasks/new', 10)
        self.task_index = 0
        self.create_timer(10.0, self.tick)
        self._was_leader = None

    def tick(self):
        is_leader = self.raft._isLeader()

        if is_leader != self._was_leader:
            self.get_logger().info(f'Leadership status: {"LEADER" if is_leader else "follower"}')
            self._was_leader = is_leader

        if not is_leader:
            return

        box_name = random.choice(list(BOXES.keys()))
        box = BOXES[box_name]
        delivery_name = random.choice(list(DELIVERY_POINTS.keys()))
        delivery = DELIVERY_POINTS[delivery_name]

        task = {
            'task_id': self.task_index,
            'box': box_name,
            'start_x': box['x'],
            'start_y': box['y'],
            'delivery': delivery_name,
            'x': delivery['x'],
            'y': delivery['y'],
        }
        self.announce_pub.publish(String(data=json.dumps(task)))
        self.get_logger().info(f'Announced task {self.task_index}: {box_name} -> {delivery_name}')
        self.task_index = self.task_index + 1


def main():
    self_addr = sys.argv[1]
    partner_addrs = sys.argv[2].split(',')

    raft = FleetManagerCore(self_addr, partner_addrs)

    rclpy.init()
    node = FleetManagerNode(raft)
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
