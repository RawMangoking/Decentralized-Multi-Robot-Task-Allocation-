FROM osrf/ros:jazzy-desktop-full

ENV ENABLE_SIM=false

WORKDIR /root/ros2_ws
RUN sed -i 's|http://archive.ubuntu.com|https://archive.ubuntu.com|g; s|http://security.ubuntu.com|https://security.ubuntu.com|g' /etc/apt/sources.list 2>/dev/null; \
    sed -i 's|http://archive.ubuntu.com|https://archive.ubuntu.com|g; s|http://security.ubuntu.com|https://security.ubuntu.com|g' /etc/apt/sources.list.d/ubuntu.sources 2>/dev/null; \
    true
RUN apt-get update && apt-get install -y ros-jazzy-rmw-zenoh-cpp
COPY ros2_ws/src/swarm_agent src/swarm_agent

RUN /bin/bash -c "source /opt/ros/jazzy/setup.bash && colcon build --packages-select swarm_agent"

COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
