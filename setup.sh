#!/bin/bash

# Get the directory where this script is located
SCRIPT_DIR=$(dirname "$(realpath "$0")")

# Path to the virtual environment's Python interpreter
VENV_PYTHON="$SCRIPT_DIR/.venv/bin/python3"

# Check if the virtual environment's Python exists
if [ ! -f "$VENV_PYTHON" ]; then
    echo "Virtual environment not found at $VENV_PYTHON."
    echo "Ensure the virtual environment is set up correctly in $SCRIPT_DIR/.venv."
    exit 1
fi

# Ensure the script is run with sufficient permissions
if [ "$(id -u)" -ne 0 ]; then
    echo "This script must be run as root (e.g., using sudo) to place 'simferm' in /usr/local/bin."
    exit 1
fi

# Create the wrapper script in /usr/local/bin
WRAPPER_PATH="/usr/local/bin/simferm"
echo "#!/bin/bash" > "$WRAPPER_PATH"
echo "\"$VENV_PYTHON\" \"$SCRIPT_DIR/simferm.py\" \"\$@\"" >> "$WRAPPER_PATH"

# Ensure the wrapper script and the original script are executable
chmod +x "$WRAPPER_PATH"
chmod +x "$SCRIPT_DIR/simferm.py"

echo "Setup complete. You can now run 'simferm' from anywhere. The log file will be co-located where simferm.py was installed."

