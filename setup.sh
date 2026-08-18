#!/usr/bin/env bash

set -e

WORKSPACE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=============================================="
echo "     LLM-CONTROLLED GROUND ROBOT SETUP"
echo "=============================================="
echo

echo "[1/6] Checking ROS 2..."

if [ ! -f /opt/ros/lyrical/setup.bash ]; then
    echo "ERROR: ROS 2 Lyrical was not found at:"
    echo "  /opt/ros/lyrical/setup.bash"
    exit 1
fi

source /opt/ros/lyrical/setup.bash

echo "ROS_DISTRO=$ROS_DISTRO"

if [ "$ROS_DISTRO" != "lyrical" ]; then
    echo "WARNING: Expected ROS 2 Lyrical."
    echo "Detected: $ROS_DISTRO"
fi

echo
echo "[2/6] Checking Gazebo..."

if ! command -v gz >/dev/null 2>&1; then
    echo "ERROR: Gazebo command 'gz' was not found."
    exit 1
fi

echo "Gazebo:"
gz sim --version

echo
echo "[3/6] Checking Python..."

if ! command -v python3 >/dev/null 2>&1; then
    echo "ERROR: python3 was not found."
    exit 1
fi

python3 --version

echo
echo "[4/6] Checking Python dependencies..."

python3 -c "import requests" 2>/dev/null || {
    echo "requests is missing. Installing with pip..."
    python3 -m pip install --user requests
}

echo "requests: OK"

echo
echo "[5/6] Checking Ollama..."

if ! command -v ollama >/dev/null 2>&1; then
    echo "ERROR: Ollama is not installed."
    echo
    echo "Install Ollama from:"
    echo "https://ollama.com/"
    exit 1
fi

ollama --version

echo
echo "Checking qwen2.5:3b..."

if ! ollama list | grep -q '^qwen2.5:3b'; then
    echo "Model qwen2.5:3b is not installed."
    echo "Pulling model..."
    ollama pull qwen2.5:3b
else
    echo "qwen2.5:3b: OK"
fi

echo
echo "[6/6] Building ROS 2 workspace..."

cd "$WORKSPACE"

colcon build

source "$WORKSPACE/install/setup.bash"

echo
echo "=============================================="
echo "             SETUP COMPLETE"
echo "=============================================="
echo
echo "Run the demonstration with:"
echo
echo '  ./scripts/run_demo.sh "Drive the inspection route three times"'
echo
