# Technical Write-up — LLM-Controlled Ground Robot

## 1. Project Overview

This project implements a natural-language mission interface for a simulated differential-drive ground robot.

The operator provides a command such as:

"Drive the inspection route three times"

A locally hosted Qwen 2.5 3B model, served through Ollama, interprets the command and returns a constrained structured response.

The application converts that response into an executable mission, validates it, and passes the validated mission to a deterministic ROS 2 waypoint controller.

The system separates high-level language interpretation from low-level robot execution.

## 2. Architecture

```text
Operator
   |
   v
Natural-language prompt
   |
   v
Local Qwen 2.5 3B / Ollama
   |
   v
Structured JSON mission
   |
   v
Mission validator
   |
   v
Deterministic ROS 2 executor
   |
   v
ros_gz_bridge
   |
   v
Gazebo ground robot
   ^
   |
Odometry

## 3. Role of the LLM

The LLM is deliberately restricted to high-level operator-intent interpretation.

The current prompt tells the model that the robot supports only an inspection-loop mission and asks for a constrained JSON response.

Example:

{"supported":true,"repeat":3}

The model does not directly generate velocity commands.

## 4. Mission Generation

The application converts the LLM response into the supported mission representation:

{
  "version": "1.0",
  "mission": "inspection_loop",
  "repeat": 3,
  "waypoints": [
    {"x": 2.0, "y": 0.0},
    {"x": 2.0, "y": 2.0},
    {"x": 0.0, "y": 2.0},
    {"x": 0.0, "y": 0.0}
  ]
}

The mission is stored temporarily and passed to the deterministic executor.

## 5. Validation and Guardrail

Before execution, the mission validator checks:

- Mission object structure.
- Required fields.
- Mission type.
- Repeat count.
- Waypoint list.
- Waypoint object structure.
- Numeric X/Y coordinates.

Only the currently supported inspection-loop mission is accepted.

The repeat count is constrained to the supported range.

The architectural principle is:

LLM proposal
     |
     v
Mission validation
     |
  +--+--+
  |     |
reject  accept
         |
         v
    Robot executor

This prevents the language model from directly entering the low-level control loop.

## 6. Deterministic Robot Execution

The deterministic waypoint controller is responsible for robot motion.

It:

1. Loads the validated mission.
2. Reads robot odometry.
3. Tracks current X/Y position and yaw.
4. Calculates the direction to the current waypoint.
5. Generates velocity commands.
6. Detects when a waypoint is reached.
7. Advances to the next waypoint.
8. Repeats the mission when requested.
9. Reports mission completion.

## 7. ROS 2 Interfaces

Command:

/model/vehicle_blue/cmd_vel

Message:

geometry_msgs/msg/Twist

Odometry:

/model/vehicle_blue/odometry

Message:

nav_msgs/msg/Odometry

The ROS-Gazebo bridge translates between ROS 2 messages and Gazebo transport messages.

## 8. Mission Control

The controller exposes:

/mission/pause
/mission/cancel
/mission/get_status
/mission/reset

These controls were tested during development.

## 9. Automatic Simulation Startup

The user-facing Python interface automatically starts the simulation launch system before running the mission.

The launcher:

- Locates installed package resources.
- Configures the Gazebo model resource path.
- Starts Gazebo.
- Starts the ROS-Gazebo bridges.

The mission runner waits for the odometry publisher before continuing.

This avoids requiring the operator to manually start Gazebo, the bridge, and the controller in separate terminals.

## 10. Challenges and Solutions

### Gazebo model discovery

The simulation required explicit model-resource configuration so that the vehicle model could be resolved from the SDF world.

The solution was to determine the installed package share directory and add the package's simulation model directory to GZ_SIM_RESOURCE_PATH.

### ROS/Gazebo communication

The simulated robot required a ROS-Gazebo bridge.

The working system bridges command velocity and odometry.

### Simulation readiness

Starting Gazebo does not guarantee that robot odometry is immediately available.

The mission runner waits for the odometry publisher before starting mission execution.

### LLM output validation

A language model can produce malformed or unsupported output.

The application constrains the expected response format and validates the resulting mission before execution.

### Automatic startup

The final mission interface starts the simulation and bridge automatically rather than requiring multiple manually managed terminals.

### Portability

Hard-coded simulation paths were removed from the main launch path. ROS package-share lookup is now used to locate installed simulation resources.

## 11. Verified Demonstration

The final demonstration command is:

./scripts/run_demo.sh "Drive the inspection route three times"

A successful run produces:

LLM OUTPUT:
{"supported":true,"repeat":3}

VALIDATION:
Mission is valid

Reached waypoint 1
Reached waypoint 2
Reached waypoint 3
Reached waypoint 4

Repeating mission: 2/3
Repeating mission: 3/3

Mission completed

## 12. Scaling to Harder Real-World Problems

A larger system could expand the mission representation into a typed task graph:

Natural Language
       |
       v
LLM Task Planner
       |
       v
Typed Task Graph
       |
       v
Safety / Constraint Validation
       |
       v
Task Execution Layer
       |
       +---- Navigation
       |
       +---- Perception
       |
       +---- Manipulation
       |
       v
Robot Hardware

The same architectural principles should remain:

- LLM for high-level semantic interpretation/planning.
- Explicit machine-readable task representation.
- Validation and safety constraints.
- Deterministic or bounded low-level execution.
- Sensor feedback.
- Explicit recovery and cancellation mechanisms.

For real hardware, additional capabilities would be required for localization, mapping, dynamic obstacle avoidance, watchdogs, emergency-stop handling, and fault recovery.

## 13. Limitations

Current limitations include:

- One supported mission type.
- Fixed waypoint route.
- Simulation-only robot.
- No physical hardware validation.
- No autonomous obstacle avoidance.
- No SLAM or dynamic navigation.
- No long-horizon task planning.

These limitations are deliberate for the current demonstration scope.

## 14. Code Ownership and AI Assistance

AI coding assistants were used during development.

The project author is responsible for the submitted implementation and can explain and modify the LLM integration, mission generation, mission validation, ROS 2 interfaces, deterministic waypoint control, mission-management services, Gazebo integration, and simulation startup.

Third-party software remains under its original license.
