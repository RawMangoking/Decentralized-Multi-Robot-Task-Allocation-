FROM osrf/ros:jazzy-simulation

RUN apt-get update && apt-get install -y --no-install-recommends \
      python3-colcon-common-extensions \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /root/ros2_ws
COPY src/swarm_agent src/swarm_agent

RUN /bin/bash -c "source /opt/ros/jazzy/setup.bash && \
      colcon build --packages-select swarm_agent --symlink-install"

COPY src/swarm_agent/docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
