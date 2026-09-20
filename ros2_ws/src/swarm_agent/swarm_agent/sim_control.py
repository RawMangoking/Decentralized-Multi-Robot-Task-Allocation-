import subprocess
import os

SIM_ENABLED = os.environ.get('ENABLE_SIM', 'true').lower() == 'true'
def spawn_box(name, x, y, z, sx, sy, sz, r, g, b):
    sdf = (
        f"<?xml version='1.0'?><sdf version='1.7'><model name='{name}'>"
        f"<pose>{x} {y} {z} 0 0 0</pose><link name='link'>"
        f"<visual name='visual'><geometry><box><size>{sx} {sy} {sz}</size></box></geometry>"
        f"<material><ambient>{r} {g} {b} 1</ambient><diffuse>{r} {g} {b} 1</diffuse></material></visual>"
        f"<collision name='collision'><geometry><box><size>{sx} {sy} {sz}</size></box></geometry></collision>"
        f"</link></model></sdf>"
    )
    subprocess.run([
        'gz', 'service', '-s', '/world/empty/create',
        '--reqtype', 'gz.msgs.EntityFactory',
        '--reptype', 'gz.msgs.Boolean',
        '--timeout', '2000',
        '--req', f"sdf: \"{sdf}\", name: \"{name}\""
    ])

class SimController:
    def __init__(self, node, robot_id, on_complete=None):
        self.node = node
        self.robot_id = robot_id
        self.on_complete = on_complete
        self.path = []
        self.path_index = 0
        self.timer = None
        self.carried_entity = None
        self.active_on_complete = None
    def move_along_path(self, path, on_complete=None, carried_entity=None):
        if self.timer is not None:
            self.timer.cancel()
            self.node.destroy_timer(self.timer)
            self.timer = None

        if not path:
            self.node.get_logger().warning('No path to execute')
            return

        self.path = path
        self.path_index = 0
        self.carried_entity = carried_entity
        self.active_on_complete = on_complete or self.on_complete

        self.move_next()
        if len(self.path) > 1:
            self.timer = self.node.create_timer(0.3, self.move_next)

    def move_next(self):
        if self.path_index >= len(self.path):
            self.stop()
            return
        x, y = self.path[self.path_index]
        self.set_pose(self.robot_id, x, y)
        if self.carried_entity is not None:
            self.set_pose(self.carried_entity, x, y)
        self.path_index += 1
        if self.path_index >= len(self.path):
            self.stop()

    def set_pose(self, entity_name, x, y):
        if not SIM_ENABLED:
            return
        try:
            subprocess.run([
                'gz', 'service', '-s', '/world/empty/set_pose',
                '--reqtype', 'gz.msgs.Pose', '--reptype', 'gz.msgs.Boolean',
                '--timeout', '1000',
                '--req', f'name: "{entity_name}", position: {{x: {x}, y: {y}, z: 0.5}}'
            ])
        except FileNotFoundError:
            pass

    def stop(self):
        if self.timer is not None:
            self.timer.cancel()
            self.node.destroy_timer(self.timer)
            self.timer = None
        callback = self.active_on_complete
        self.active_on_complete = None
        if callback is not None:
            callback()
