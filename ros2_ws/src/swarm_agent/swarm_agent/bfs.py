import swarm_agent.layout as l
from collections import deque


def bfs(x1, y1, x2, y2):

    gridsize = l.GRID_SIZE

    start = (x1, y1)
    goal = (x2, y2)

    blocked = l.SHELVES

    if start in blocked or goal in blocked:
        return [], -1

    queue = deque([start])

    visited = {start}

    parent = {
        start: None
    }

    directions = [
        (1, 0),
        (-1, 0),
        (0, 1),
        (0, -1)
    ]

    while queue:

        current = queue.popleft()

        if current == goal:
            break

        x, y = current

        for dx, dy in directions:

            next_pos = (x + dx, y + dy)

            # Check grid boundaries
            if not (
                0 <= next_pos[0] < gridsize
                and
                0 <= next_pos[1] < gridsize
            ):
                continue

            # Check shelves
            if next_pos in blocked:
                continue

            # Already visited
            if next_pos in visited:
                continue

            visited.add(next_pos)

            parent[next_pos] = current

            queue.append(next_pos)

    # No path
    if goal not in parent:
        return [], -1

    # ------------------------------------------
    # Reconstruct path
    # ------------------------------------------

    path = []

    current = goal

    while current is not None:

        path.append(current)

        current = parent[current]

    path.reverse()

    # Number of movements
    distance = len(path) - 1

    return path, distance

def findpath(robot_x, robot_y, pick_x, pick_y, deli_x, deli_y):
    path1, distance1 = bfs(robot_x, robot_y, pick_x, pick_y)
    path2, distance2 = bfs(pick_x, pick_y, deli_x, deli_y)

    if distance1 == -1 or distance2 == -1:
        return None, None, -1

    return path1, path2, distance1 + distance2