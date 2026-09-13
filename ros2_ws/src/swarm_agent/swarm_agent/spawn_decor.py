from swarm_agent.layout import GRID_SIZE, CELL_SIZE, SHELVES, BOXES
from swarm_agent.sim_control import spawn_box  # move spawn_box here if not already shared

def main():
    center = GRID_SIZE * CELL_SIZE / 2
    spawn_box('floor', center, center, -0.05, GRID_SIZE, GRID_SIZE, 0.1, 0.59, 0.29, 0.0)
    for i, (gx, gy) in enumerate(SHELVES):
        spawn_box(f'shelf_{i}', gx, gy, 0.75, 0.8, 0.8, 1.5, 0.4, 0.25, 0.1)

    for name, pos in BOXES.items():
        spawn_box(name, pos['x'], pos['y'], 0.3, 0.4, 0.4, 0.4, 0.9, 0.6, 0.1)

if __name__ == '__main__':
    main()