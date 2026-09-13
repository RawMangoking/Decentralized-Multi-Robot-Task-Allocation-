#!/bin/bash
set -e
source /opt/ros/jazzy/setup.bash
source /root/ros2_ws/install/setup.bash

export GZ_PARTITION=swarm-fleet

exec ros2 run swarm_agent agent_node --ros-args \
  -p robot_id:="${ROBOT_ID:?ROBOT_ID env var required}" \
  -p start_x:="${START_X:-0.0}" \
  -p start_y:="${START_Y:-0.0}"
