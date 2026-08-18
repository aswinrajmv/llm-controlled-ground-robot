# Sources and Licenses

This document separates the original project code from third-party software and model assets used by the LLM-Controlled Ground Robot project.

## 1. ROS 2

Source:
https://docs.ros.org/

License:
ROS 2 packages are distributed under their respective package licenses; the ROS 2 ecosystem commonly includes Apache-2.0 licensed components.

Use in this project:
- ROS 2 middleware
- `rclpy`
- ROS 2 nodes, publishers, subscribers, services, parameters, and package infrastructure

Project-specific code was written for this project; ROS 2 itself is not included as original project code.

## 2. Gazebo Sim

Source:
https://gazebosim.org/

License:
Apache License 2.0

Use in this project:
- Ground-robot simulation
- Physics simulation
- SDF world
- Simulated differential-drive robot

## 3. ros_gz

Repository:
https://github.com/gazebosim/ros_gz

License:
Apache License 2.0

Use in this project:
- `ros_gz_bridge`
- ROS 2 <-> Gazebo transport bridge
- `/model/vehicle_blue/cmd_vel`
- `/model/vehicle_blue/odometry`

The repository's ROS 2 launch examples and bridge infrastructure were used as external software/components rather than copied as project source.

## 4. Ollama

Repository:
https://github.com/ollama/ollama

License:
MIT

Use in this project:
- Local model serving
- Ollama HTTP API at `http://localhost:11434`
- Serving the Qwen model locally

The project communicates with Ollama through its HTTP API; Ollama itself is third-party software.

## 5. Qwen2.5-3B

Model:
https://huggingface.co/Qwen/Qwen2.5-3B

License:
Qwen Research License Agreement (`qwen-research`)

Use in this project:
- Local natural-language mission interpretation
- Determining whether the operator command is supported
- Determining the requested inspection-loop repetition count

Important:
The model license is separate from this project's MIT license. This repository does not relicense the Qwen model or its weights.

## 6. Original project code

The following project-specific components were developed for this project:

- Natural-language mission interface
- Ollama HTTP integration
- Mission construction
- Mission validation logic
- Deterministic waypoint controller
- Pause/resume/cancel/reset/status mission services
- ROS 2 integration
- Ground-robot simulation integration
- Gazebo launch and resource-path handling
- Demo launcher
- Project documentation

These project-specific source files are released under the MIT License included in this repository.

## 7. Important licensing boundary

The MIT license in this repository applies to the project's original code only.

It does not replace, modify, or relicense:
- ROS 2
- Gazebo
- ros_gz
- Ollama
- Qwen2.5-3B
- other third-party dependencies

Third-party components remain subject to their own licenses and terms.

## 8. AI-assisted development

AI coding assistants were used during development.

The submitted codebase was reviewed, tested, debugged, and integrated by the project author. The author is responsible for understanding the implementation and being able to modify and explain it.

