#!/usr/bin/env bash

set -e

WORKSPACE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "=============================================="
echo "       LLM-CONTROLLED GROUND ROBOT"
echo "=============================================="
echo

cd "$WORKSPACE"

if [ ! -f /opt/ros/lyrical/setup.bash ]; then
    echo "ERROR: ROS 2 Lyrical was not found."
    exit 1
fi

source /opt/ros/lyrical/setup.bash

if [ ! -f "$WORKSPACE/install/setup.bash" ]; then
    echo "ERROR: Workspace has not been built."
    echo "Run:"
    echo "  colcon build"
    exit 1
fi

source "$WORKSPACE/install/setup.bash"

if ! command -v ollama >/dev/null 2>&1; then
    echo "ERROR: Ollama is not installed."
    exit 1
fi

if ! ollama list | grep -q '^qwen2.5:3b'; then
    echo "ERROR: qwen2.5:3b is not installed."
    echo "Run:"
    echo "  ollama pull qwen2.5:3b"
    exit 1
fi

if [ "$#" -eq 0 ]; then
    PROMPT="Drive the inspection route three times"
else
    PROMPT="$*"
fi

echo "Operator command:"
echo "  $PROMPT"
echo

python3 \
    "$WORKSPACE/src/omokai_controller/omokai_controller/run_mission.py" \
    "$PROMPT"
