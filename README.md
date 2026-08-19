# LLM-Controlled Ground Robot

A ROS 2 and Gazebo-based ground robot system that accepts natural-language mission commands, uses a locally hosted Qwen 2.5 3B model through Ollama to interpret operator intent, validates the resulting mission, and executes it through a deterministic ROS 2 controller.

## Quick Start

```bash
source /opt/ros/lyrical/setup.bash
colcon build
source install/setup.bash
./scripts/run_demo.sh "Drive the inspection route three times"
```

## Architecture

```text
Natural-language command
        |
        v
Local LLM (Qwen 2.5 3B / Ollama)
        |
        v
Structured mission JSON
        |
        v
Mission validator
        |
        v
Deterministic ROS 2 waypoint executor
        |
        v
ROS-Gazebo bridge
        |
        v
Gazebo ground robot
        ^
        |
     Odometry
```

The LLM is used for high-level intent interpretation. It does not directly control the robot velocity loop.

## Current Mission

The current implementation supports the `inspection_loop` mission.

Waypoints:

```text
(2.0, 0.0)
(2.0, 2.0)
(0.0, 2.0)
(0.0, 0.0)
```

Example command:

```text
Drive the inspection route three times
```

Expected LLM response:

```json
{"supported":true,"repeat":3}
```

The application then constructs and validates the executable mission before execution.

## Verified Environment

- ROS 2: Lyrical
- Gazebo Sim: 10.4.0
- Python: 3.14.4
- Ollama: 0.32.14
- Model: qwen2.5:3b

## Build

```bash
source /opt/ros/lyrical/setup.bash
colcon build
source install/setup.bash
```

## Run the Demo

```bash
./scripts/run_demo.sh "Drive the inspection route three times"
```

A successful run ends with:

```text
Mission completed
```

## Mission Validation

The validator checks the mission structure, supported mission type, repeat count, and waypoint structure before execution.

## Mission Control

Available ROS 2 services:

```text
/mission/pause
/mission/cancel
/mission/get_status
/mission/reset
```

## License

Original project code is released under the MIT License. Third-party software and model assets remain under their respective licenses; see SOURCES.md.

## Project Name

The project is presented externally as LLM-Controlled Ground Robot. The internal ROS 2 package remains `omokai_controller` for compatibility with the implemented package and launch interfaces.

## Docker

Docker support is provided as an additional reproducible deployment path.

The container includes:

- ROS 2 Lyrical
- Gazebo Sim 10.4.0
- `ros_gz_bridge`
- `ros_gz_sim`
- Python runtime and project dependencies
- The complete ground-robot project

Ollama and the `qwen2.5:3b` model remain on the host and are accessed by the container through the host network.

### Prerequisites

Install Docker Engine and Docker Compose, and ensure Ollama is running with the required model:

```bash
ollama list
