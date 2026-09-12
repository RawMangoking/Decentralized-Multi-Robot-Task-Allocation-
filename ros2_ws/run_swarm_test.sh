#!/bin/bash
set -e

cleanup() {
    echo ""
    echo "=== Stopping everything ==="
    pkill -f "gz sim" 2>/dev/null || true
    pkill -f "task_publisher" 2>/dev/null || true
    pkill -f "agent_node" 2>/dev/null || true
    exit 0
}
trap cleanup SIGINT SIGTERM

echo "=== Killing any leftover processes from previous runs ==="
pkill -f "gz sim" 2>/dev/null || true
pkill -f "task_publisher" 2>/dev/null || true
pkill -f "agent_node" 2>/dev/null || true
sleep 1

echo "=== Sourcing ROS 2 ==="
source /opt/ros/jazzy/setup.bash

echo "=== Rebuilding swarm_agent ==="
cd /root/ros2_ws
colcon build --packages-select swarm_agent
source install/setup.bash

echo "=== Starting Gazebo ==="
rm -f /tmp/gz.log
gz sim -r empty.sdf > /tmp/gz.log 2>&1 &
sleep 5

echo "=== Spawning warehouse decor (floor, shelves, boxes) ==="
ros2 run swarm_agent spawn_decor

spawn_box() {
    local name=$1
    local x=$2
    local y=$3
    local req="sdf: \"<?xml version=\\\"1.0\\\"?><sdf version=\\\"1.7\\\"><model name=\\\"$name\\\"><pose>$x $y 0.5 0 0 0</pose><link name=\\\"link\\\"><visual name=\\\"visual\\\"><geometry><box><size>1 1 1</size></box></geometry></visual><collision name=\\\"collision\\\"><geometry><box><size>1 1 1</size></box></geometry></collision></link></model></sdf>\", name: \"$name\""
    gz service -s /world/empty/create --reqtype gz.msgs.EntityFactory --reptype gz.msgs.Boolean --timeout 2000 --req "$req" || true
}

echo "=== Spawning robot markers ==="
spawn_box robot_a 0 0
spawn_box robot_b 19 0
spawn_box robot_c 0 19
spawn_box robot_d 19 19
spawn_box robot_e 10 10

echo "=== Starting task_publisher ==="
rm -f /tmp/task_publisher.log
ros2 run swarm_agent task_publisher > /tmp/task_publisher.log 2>&1 &

echo "=== Starting 5 agent nodes ==="
rm -f /tmp/robot_a.log /tmp/robot_b.log /tmp/robot_c.log /tmp/robot_d.log /tmp/robot_e.log
ros2 run swarm_agent agent_node --ros-args -p robot_id:=robot_a -p start_x:=0.0 -p start_y:=0.0 > /tmp/robot_a.log 2>&1 &
ros2 run swarm_agent agent_node --ros-args -p robot_id:=robot_b -p start_x:=19.0 -p start_y:=0.0 > /tmp/robot_b.log 2>&1 &
ros2 run swarm_agent agent_node --ros-args -p robot_id:=robot_c -p start_x:=0.0 -p start_y:=19.0 > /tmp/robot_c.log 2>&1 &
ros2 run swarm_agent agent_node --ros-args -p robot_id:=robot_d -p start_x:=19.0 -p start_y:=19.0 > /tmp/robot_d.log 2>&1 &
ros2 run swarm_agent agent_node --ros-args -p robot_id:=robot_e -p start_x:=10.0 -p start_y:=10.0 > /tmp/robot_e.log 2>&1 &

echo ""
echo "=== Everything running. Watching logs (Ctrl+C stops everything cleanly) ==="
sleep 1
tail -f /tmp/task_publisher.log /tmp/robot_a.log /tmp/robot_b.log /tmp/robot_c.log /tmp/robot_d.log /tmp/robot_e.log
