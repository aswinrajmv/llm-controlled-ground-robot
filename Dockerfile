FROM ros:lyrical

SHELL ["/bin/bash", "-c"]

ENV DEBIAN_FRONTEND=noninteractive
ENV ROS_DISTRO=lyrical

RUN apt-get update && \
    apt-get install -y \
        ros-lyrical-ros-gz \
        ros-lyrical-ros-gz-sim \
        python3-requests \
        python3-pip \
        git \
        bash \
        && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

COPY src ./src
COPY scripts ./scripts
COPY setup.sh .
COPY LICENSE .
COPY README.md .
COPY SOURCES.md .
COPY RESULTS.md .
COPY docs ./docs

RUN source /opt/ros/lyrical/setup.bash && \
    colcon build

RUN chmod +x \
    /workspace/setup.sh \
    /workspace/scripts/run_demo.sh

CMD ["/bin/bash"]
