import json
import subprocess
import sys
import tempfile

import requests

from mission_validator import validate_mission


OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2.5:3b"


def generate_mission(prompt):
    """
    Use the local Qwen LLM through Ollama to convert
    a natural-language command into a structured mission.
    """

    llm_prompt = f"""
You are a robot mission planner.

Convert the operator command into a mission JSON.

The robot can ONLY perform an "inspection_loop" mission.

The mission MUST use exactly these waypoints:

[
  {{"x": 2.0, "y": 0.0}},
  {{"x": 2.0, "y": 2.0}},
  {{"x": 0.0, "y": 2.0}},
  {{"x": 0.0, "y": 0.0}}
]

Return ONLY valid JSON.

The JSON format MUST be:

{{
  "version": "1.0",
  "mission": "inspection_loop",
  "repeat": NUMBER,
  "waypoints": [
    {{"x": NUMBER, "y": NUMBER}},
    {{"x": NUMBER, "y": NUMBER}},
    {{"x": NUMBER, "y": NUMBER}},
    {{"x": NUMBER, "y": NUMBER}}
  ]
}}

Operator command:
{prompt}
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": llm_prompt,
            "stream": False,
            "format": "json"
        },
        timeout=180
    )

    response.raise_for_status()

    data = response.json()

    llm_output = data["response"]

    print("LLM OUTPUT:")
    print(llm_output)
    print()

    try:
        mission = json.loads(llm_output)
    except json.JSONDecodeError as error:
        raise ValueError(
            f"LLM returned invalid JSON: {error}"
        )

    return mission


def main():

    if len(sys.argv) < 2:
        print("Usage:")
        print(
            'python3 run_mission.py '
            '"Drive the inspection route three times"'
        )
        sys.exit(1)

    prompt = " ".join(sys.argv[1:])

    print()
    print("PROMPT:")
    print(prompt)
    print()

    print("Calling local LLM...")
    print()

    try:
        mission = generate_mission(prompt)
    except Exception as error:
        print(f"LLM ERROR: {error}")
        sys.exit(1)

    print("GENERATED MISSION:")
    print(json.dumps(mission, indent=2))
    print()

    valid, message = validate_mission(mission)

    print("VALIDATION:")
    print(message)
    print()

    if not valid:
        print("Mission rejected.")
        sys.exit(1)

    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".json",
        delete=False
    ) as file:

        json.dump(mission, file, indent=2)
        mission_file = file.name

    print(f"Validated mission saved to: {mission_file}")
    print()
    print("Starting deterministic executor...")
    print()

    subprocess.run([
        "ros2",
        "run",
        "omokai_controller",
        "square_controller",
        "--ros-args",
        "-p",
        f"mission_file:={mission_file}"
    ])


if __name__ == "__main__":
    main()
