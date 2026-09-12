import json
import heapq
from .sim_control import SimController
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import subprocess
from .bfs import findpath

class Agent(Node):

    def __init__(self):
        super().__init__('agentnode')
        self.declare_parameter('robot_id', 'robot1')
        self.declare_parameter('start_x', 0.0)
        self.declare_parameter('start_y', 0.0)
        self.id = self.get_parameter('robot_id').value
        self.x = self.get_parameter('start_x').value
        self.y = self.get_parameter('start_y').value
        self.declare_parameter('exec_seconds', 10.0)
        self.exec_seconds = self.get_parameter('exec_seconds').value
        self.occupied = False
        self.execution_timer = None
        self.current = None
        self.jobs = {}
        self.robot = {}
        self.heap = []
        self.bids = {}
        self.participants = set()
        self.acks = set()
        self.task_id = None
        self.my_bid = None
        self.claimed_winner = None
        self.state = 'IDLE'
        self.task_x = None
        self.task_y = None
        self.sim_controller = SimController(
            self,
            self.id,
            on_complete=self.task_finished
        )
        self.pickup_x = None
        self.pickup_y = None

        self.current_path = []

        self.discovery_pub = self.create_publisher(String,'/robots/discover',10)

        self.discovery_sub = self.create_subscription(String,'/robots/discover',self.discover,10)

        self.discovery_timer = self.create_timer(30.0,self.broadcast)

        self.timeout_timer = self.create_timer(10.0,self.check_robot_timeout)


        self.task_sub = self.create_subscription(String,'/tasks/new',self.posted,10)

        self.bid_pub = self.create_publisher(String,'/tasks/bids',10)

        self.bid_sub = self.create_subscription(String,'/tasks/bids',self.receive_bid,10)

        self.claim_pub = self.create_publisher(String,'/tasks/claims',10)

        self.claim_sub = self.create_subscription(String,'/tasks/claims',self.receive_claim,10)

        self.ack_pub = self.create_publisher(String,'/tasks/acks',10)

        self.ack_sub = self.create_subscription(String,'/tasks/acks',self.receive_ack,10)

        self.winner_pub = self.create_publisher(String,'/tasks/winner',10)

        self.winner_sub = self.create_subscription(String,'/tasks/winner',self.receive_winner,10)

        self.bid_timer = None

        self.broadcast()


    def broadcast(self):
        msg = String()
        data = {'id': self.id,'status': int(self.occupied)}
        msg.data = json.dumps(data)
        self.discovery_pub.publish(msg)


    def discover(self, msg):
        try:
            data = json.loads(msg.data)
            received_id = data['id']
            status = int(data['status'])

        except (json.JSONDecodeError, KeyError, ValueError):
            self.get_logger().warning(
                'Invalid discovery message'
            )
            return

        if received_id == self.id:
            return

        now = self.get_clock().now()

        if received_id not in self.robot:
            self.get_logger().info(f'Robot joined: {received_id}')
        self.robot[received_id] = {'status': status,'last_seen': now}

    def check_robot_timeout(self):
        now = self.get_clock().now()
        timeout_ns = 60 * 1_000_000_000
        dead_robots = []
        for robot_id, info in self.robot.items():
            elapsed = (now - info['last_seen']).nanoseconds
            if elapsed > timeout_ns:
                dead_robots.append(robot_id)
        for robot_id in dead_robots:
            del self.robot[robot_id]


    def posted(self, msg):
        try:
            task = json.loads(msg.data)
        except json.JSONDecodeError:
            self.get_logger().warning(
                'Invalid task message'
            )
            return
        task_id = task['task_id']
        self.jobs[task_id] = task
        self.get_logger().info(
            f'Received task {task_id}'
        )
        if self.occupied:
            self.get_logger().info(f'{self.id} is busy')
            return
        if self.state != 'IDLE':
            self.get_logger().info(f'{self.id} is not available for {task_id}')

            return
        self.start_bidding(task)

    def start_bidding(self, task):
        self.task_id = task['task_id']

        self.pickup_x = task['start_x']
        self.pickup_y = task['start_y']

        self.task_x = task['x']
        self.task_y = task['y']

        self.state = 'BIDDING'

        self.bids = {}
        self.heap = []
        self.acks = set()
        self.claimed_winner = None
        self.participants = set()

        self.participants.add(self.id)

        for robot_id, info in self.robot.items():
            if info['status'] == 0:
                self.participants.add(robot_id)

        self.path_to_pickup, self.path_to_delivery, distance = findpath(
            self.x, self.y, self.pickup_x, self.pickup_y, self.task_x, self.task_y
        )

        if distance == -1:
            self.get_logger().warning(f'{self.id} cannot reach task {self.task_id}')
            self.state = 'IDLE'
            return

        self.my_bid = distance
        self.bids[self.id] = distance
        heapq.heappush(self.heap, (distance, self.id))

        bid = {
            'type': 'BID',
            'task_id': self.task_id,
            'robot_id': self.id,
            'bid': distance
        }
        self.bid_pub.publish(String(data=json.dumps(bid)))
        self.get_logger().info(f'{self.id} bid {distance:.2f} on {self.task_id}')

        self.bid_timer = self.create_timer(5.0, self.finish_bidding)
    def receive_bid(self, msg):
        try:
            data = json.loads(msg.data)

            task_id = data['task_id']
            robot_id = data['robot_id']
            bid = float(data['bid'])

        except (json.JSONDecodeError, KeyError, ValueError):
            self.get_logger().warning(
                'Invalid bid message'
            )
            return
        if task_id != self.task_id:
            return
        if robot_id == self.id:
            return
        if robot_id in self.robot:

            if self.robot[robot_id]['status'] == 1:
                return
        self.bids[robot_id] = bid
        heapq.heappush(
            self.heap,
            (bid, robot_id)
        )
        self.get_logger().info(
            f'Received bid from {robot_id}'
        )

    def finish_bidding(self):
        if self.bid_timer is not None:

            self.bid_timer.cancel()
            self.destroy_timer(self.bid_timer)

            self.bid_timer = None

        if self.state != 'BIDDING':
            return

        self.state = 'WAITING_CONFIRMATION'
        if not self.heap:
            self.get_logger().warning(
                'No bids received'
            )
            self.state = 'IDLE'
            return

        best_bid, best_robot = self.heap[0]

        self.claimed_winner = best_robot

        self.get_logger().info(
            f'Best bid for {self.task_id}: '
            f'{best_robot} = {best_bid:.2f}'
        )
        if best_robot == self.id:

            self.send_claim(best_bid)
    def send_claim(self, bid):
        claim = {
            'type': 'CLAIM',
            'task_id': self.task_id,
            'robot_id': self.id,
            'bid': bid
        }
        self.claim_pub.publish(
            String(data=json.dumps(claim))
        )
        self.acks.add(self.id)

        self.get_logger().info(
            f'{self.id} claims {self.task_id} '
            f'with bid {bid:.2f}'
        )
        self.check_majority()

    def receive_claim(self, msg):

        try:
            data = json.loads(msg.data)

            task_id = data['task_id']
            claiming_robot = data['robot_id']
            claim_bid = float(data['bid'])

        except (json.JSONDecodeError, KeyError, ValueError):
            return

        if task_id != self.task_id:
            return

        if claiming_robot == self.id:
            return

        if self.my_bid is None:
            return

        candidate = (claim_bid, claiming_robot)

        current = (self.my_bid, self.id)
        if candidate < current:

            self.get_logger().info(
                f'{claiming_robot} has better bid '
                f'{claim_bid:.2f}'
            )

            ack = {
                'type': 'ACK',
                'task_id': task_id,
                'from': self.id,
                'for_robot': claiming_robot
            }

            self.ack_pub.publish(
                String(data=json.dumps(ack))
            )

        else:

            self.get_logger().info(
                f'{self.id} has better option '
                f'than {claiming_robot}'
            )
    def receive_ack(self, msg):

        try:
            data = json.loads(msg.data)

            task_id = data['task_id']
            from_robot = data['from']
            for_robot = data['for_robot']

        except (json.JSONDecodeError, KeyError):
            return

        if task_id != self.task_id:
            return

        # ACK must be for us
        if for_robot != self.id:
            return

        self.acks.add(from_robot)

        self.get_logger().info(
            f'ACK from {from_robot} '
            f'({len(self.acks)} votes)'
        )

        self.check_majority()

    def check_majority(self):

        total = len(self.participants)

        majority = total // 2 + 1

        if len(self.acks) >= majority:

            self.get_logger().info(
                f'{self.id} has MAJORITY '
                f'({len(self.acks)}/{total})'
            )

            self.announce_winner()
    def announce_winner(self):

        if self.state == 'EXECUTING':
            return

        self.state = 'EXECUTING'

        self.occupied = True

        winner = {'type': 'WINNER','task_id': self.task_id,'robot_id': self.id,'bid': self.my_bid}
        self.winner_pub.publish(
            String(data=json.dumps(winner))
        )

        self.get_logger().info(
            f'{self.id} WON {self.task_id}'
        )
        self.broadcast()
        self.execute_task()
    def receive_winner(self, msg):
        try:
            data = json.loads(msg.data)

            task_id = data['task_id']
            winner = data['robot_id']
            bid = float(data['bid'])

        except (json.JSONDecodeError, KeyError, ValueError):
            return

        if task_id != self.task_id:
            return

        if self.my_bid is not None:

            if (self.my_bid, self.id) < (bid, winner):
                self.get_logger().warning(f'{self.id} better bid ')
                return
        self.claimed_winner = winner
        if winner != self.id:
            self.get_logger().info(
                f'{winner} won {task_id}'
            )
            self.state = 'IDLE'
    def execute_task(self):
        self.sim_controller.move_along_path(
            self.path_to_pickup,
            on_complete=self.arrived_at_pickup
        )

    def arrived_at_pickup(self):
        self.sim_controller.move_along_path(
            self.path_to_delivery,
            on_complete=self.task_finished,
            carried_entity=self.jobs[self.task_id]['box']
        )
    def task_finished(self):

        self.get_logger().info(
            f'{self.id} completed task {self.task_id}'
        )

        # Robot is already at the delivery point
        self.x = self.task_x
        self.y = self.task_y

        self.occupied = False
        self.current = None

        self.task_id = None
        self.my_bid = None

        self.task_x = None
        self.task_y = None

        self.pickup_x = None
        self.pickup_y = None

        self.current_path = []

        self.bids = {}
        self.heap = []
        self.participants = set()
        self.acks = set()
        self.claimed_winner = None

        self.state = 'IDLE'

        self.broadcast()
def main():
    rclpy.init()
    node = Agent()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()