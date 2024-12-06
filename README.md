
# Simferm

Simferm is a Python script designed to simulate the fermentation process by generating
temperature and gravity data. It is specifically designed to work with
[Tilt-Sim](https://github.com/spouliot/tilt-sim), a tool that can simulate multiple (16) Tilt / Tilt Pro devices.
Simferm can be used to test and develop brewing software.

## Features

- Simulates temperature and gravity changes during a fermentation process.
- Integrates seamlessly with Tilt-Sim to send simulated data.
- Configurable via command-line arguments or a YAML configuration file.
- Logs all simulated data to a log file for easy monitoring.

## Installation

### Step 1: Clone the Repository

First, clone the repository to your local machine:

``` git clone https://github.com/ChuckGl/simferm.git cd simferm ```

### Step 2: Set Up a Virtual Environment

Create a Python virtual environment in the directory where `simferm.py` is located:

``` python3 -m venv .venv ```

Activate the virtual environment:

- On Linux/macOS: ``` source .venv/bin/activate ```
- On Windows: ``` .venv\Scripts\activate ```

### Step 3: Install Required Dependencies

With the virtual environment activated, install the required Python packages using pip:

``` pip install -r requirements.txt ```

## Setup Script

### setup.sh

The `setup.sh` script is designed to create a symbolic link in `~/.local/bin` that allows
you to run `simferm` from anywhere on your system.

#### How to Use the Setup Script

1. Make the `setup.sh` script executable:

   ``` chmod +x setup.sh ```

2. Run the `setup.sh` script:

   ``` ./setup.sh ```

This will create a symbolic link in `~/.local/bin`, allowing you to run `simferm` from any
directory by simply typing `simferm`.

## Running Simferm

Simferm can be run in three ways: with a configuration file, using default settings, or
with command-line arguments.

### 1. Running with a Configuration File

You can create a YAML configuration file (`config.yaml`) to specify the settings for the
simulation. Here's an example configuration:

```
ip: '192.168.254.62' # IP address of the Tilt-Sim device
color: 'yellow*hd' # Tilt color from Tilt-Sim device
starttemp: 101.3 # Starting temperature (°F)
finaltemp: 55.3 # Final temperature (°F)
og: 1.0615  # Original Gravity (OG)
fg: 1.015  # Final Gravity (FG)
time: 60  # Total simulation time (minutes)
```

To run `simferm` with a configuration file:

``` simferm --config config.yaml ```

### 2. Running Without a Configuration File (Using Defaults)

If you run `simferm` without specifying a configuration file, it will use the default
values provided in the script:

``` simferm ```

### 3. Running with Command-Line Arguments

You can override the defaults or configuration file settings by specifying command-line
arguments. Only the settings you provide a command-line argument will be overridden:

``` simferm --ip 192.168.254.62 --starttemp 104.5 --finaltemp 58.5 --time 120 --color blue --og 1.062 --fg 1.015 ```

### Command-Line Arguments

- `-h, --help`: Show this help message and exit
- `--config`: Path to the YAML configuration file
- `--ip`: IP address of the Tilt-Sim device
- `--color`: Tilt color from the Tilt-Sim device
- `--starttemp`: Starting temperature (°F)
- `--finaltemp`: Final temperature (°F)
- `--og`: Original Gravity (OG)
- `--fg`: Final Gravity (FG)
- `--time`: Total simulation time (minutes)

## Log File

All simulation data is logged to `simferm.log`, which is located in the same directory as
`simferm.py`. You can monitor this log file to track the progress of the simulated
fermentation:

``` tail -f simferm.log ```

## Tilt-Sim

For more information about Tilt-Sim, visit the [Tilt-Sim GitHub repository](https://github.com/spouliot/tilt-sim).

