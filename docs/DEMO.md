# Demo Guide — LLM-Controlled Ground Robot

## Purpose

The demonstration shows the complete pipeline:

```text
Natural-language prompt
        |
        v
Local LLM
        |
        v
Structured JSON
        |
        v
Mission validation
        |
        v
Deterministic ROS 2 executor
        |
        v
Gazebo ground robot
