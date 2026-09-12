import json
import random

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

from .layout import BOXES, DELIVERY_POINTS



class TaskPublisher(Node):
    def __init__(self):
        super().__init__('task_publisher')
        self.announce_pub = self.create_publisher(String, '/tasks/new', 10)
        self.task_index = 0
        self.create_timer(10.0, self.tick)

    def tick(self):
        box_name = random.choice(list(BOXES.keys()))
        box = BOXES[box_name]
        delivery_name = random.choice(
            list(DELIVERY_POINTS.keys())
        )

        delivery = DELIVERY_POINTS[delivery_name]
        task = {'task_id': self.task_index,'box': box_name,'start_x': box['x'],'start_y': box['y'],'delivery': delivery_name,'x': delivery['x'],'y': delivery['y']}
        self.announce_pub.publish(String(data=json.dumps(task)))        
        self.task_index =  self.task_index + 1


def main():
    rclpy.init()
    node = TaskPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
