#!/bin/bash

# Get the directory where this script is located
SCRIPT_DIR=$(dirname "$(realpath "$0")")

# Path to the virtual environment's Python interpreter
VENV_PYTHON="$SCRIPT_DIR/bin/python3"

# Check if the virtual environment's Python exists or if $VIRTUAL_ENV is set
if [ ! -f "$VENV_PYTHON" ] && [ -z "$VIRTUAL_ENV" ]; then
    echo "Virtual environment not found in $SCRIPT_DIR, and no active virtual environment detected."
    exit 1
fi

# Create the ~/.local/bin directory if it doesn't exist
mkdir -p ~/.local/bin

# Create a wrapper script in ~/.local/bin that uses the virtual environment's Python
echo "#!/bin/bash" > ~/.local/bin/simferm

# If $VIRTUAL_ENV is set, use it; otherwise, use $VENV_PYTHON
if [ -n "$VIRTUAL_ENV" ]; then
    echo "\"$VIRTUAL_ENV/bin/python3\" \"$SCRIPT_DIR/simferm.py\" \"\$@\"" >> ~/.local/bin/simferm
else
    echo "\"$VENV_PYTHON\" \"$SCRIPT_DIR/simferm.py\" \"\$@\"" >> ~/.local/bin/simferm
fi

# Ensure the simferm script is executable
chmod +x ~/.local/bin/simferm
chmod +x "$SCRIPT_DIR/simferm.py"

echo "Setup complete. You can now run 'simferm' from anywhere. The log file will be co-located where simferm.py was installed."

