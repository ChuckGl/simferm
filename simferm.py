#!/usr/bin/env python3

import os
import sys
import argparse
import random
import subprocess
import time
from datetime import datetime
import yaml

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

# ========================
# Default Configuration
# ========================
DEFAULTS = {
    'ip': '192.168.254.62',  # IP of Tilt-Sim
    'color': 'yellow*hd',  # Name of Tilt on Tilt-Sim
    'starttemp': 101.3,  # Starting temperature in Fahrenheit
    'finaltemp': 55.3,  # Final target temperature in Fahrenheit
    'time': 60,  # Total simulation time in minutes
    'og': 1.0615,  # Original Gravity (OG)
    'fg': 1.015,  # Final Gravity (FG)
}

# ========================
# Script Version
# ========================
script_version = 39

# ========================
# Function Definitions
# ========================

def generate_random_temp_increment():
    """Generates a small random temperature increment."""
    return random.uniform(0.000, 0.099)

def update_log(log_file, timestamp, script_version, current_temp_fahrenheit, color, gravity, start_temp_fahrenheit, og, is_start=False, is_end=False):
    """Logs the simulation progress to the log file."""
    try:
        if is_start:
            log_entry = (f"{timestamp.strftime('%Y-%m-%d, %H:%M:%S')}, Simulation Starting. "
                         f"Tilt Color: {color}, "
                         f"Starting Gravity: {gravity:.4f}, "
                         f"Starting Temperature: {current_temp_fahrenheit:.1f} °F, "
                         f"Run Time: {DEFAULTS['time']} minutes, "
                         f"Final Gravity: {DEFAULTS['fg']:.4f}, "
                         f"Final Temperature: {DEFAULTS['finaltemp']:.1f} °F\n")
        elif is_end:
            log_entry = (f"{timestamp.strftime('%Y-%m-%d, %H:%M:%S')}, Version {script_version}, Simulation at Start. "
                         f"Starting Temperature: {start_temp_fahrenheit:.1f} °F, Starting Gravity: {og:.4f}, Tilt Color: {color}\n")
            log_file.write(log_entry)
            log_entry = (f"{timestamp.strftime('%Y-%m-%d, %H:%M:%S')}: Version {script_version}: Simulation Complete. "
                         f"Final Temperature: {current_temp_fahrenheit:.1f} °F, "
                         f"Final Gravity: {gravity:.4f}, Tilt Color: {color}\n")
        else:
            log_entry = (f"{timestamp.strftime('%Y-%m-%d, %H:%M:%S')}: Current Temperature: {current_temp_fahrenheit:.1f} °F, "
                         f"Current Gravity: {gravity:.4f}, Tilt Color: {color}\n")
        
        log_file.write(log_entry)
        log_file.flush()
    except Exception as e:
        print(f"Error updating log file: {e}")

def execute_curl_command(ip_addr, color, current_temp_fahrenheit, gravity):
    """Executes a curl command to update the target server with simulated values."""
    try:
        curl_command = (f'curl "http://{ip_addr}/setTilt?name={color}&active=on&sg={gravity:.4f}&temp={current_temp_fahrenheit:.1f}"')
        subprocess.run(curl_command, shell=True)
    except Exception as e:
        print(f"Error executing curl command: {e}")

def read_config_file(file_path):
    """Reads the configuration file if it exists."""
    try:
        with open(file_path, 'r') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        return None  # Silently return None if the file is not found
    except yaml.YAMLError as e:
        print(f"Error parsing config file {file_path}: {e}")
        return None

def determine_direction(start_temp, end_temp):
    """Determines the direction of the temperature change."""
    return "down" if start_temp > end_temp else "up"

# ========================
# Main Function
# ========================

def main():
    parser = argparse.ArgumentParser(
        description="Simulate a fermentation using Tilt-Sim (https://github.com/spouliot/tilt-sim)",
        formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=30)
    )

    # Arguments
    parser.add_argument('--config', type=str, help='Path to the YAML configuration file.')
    parser.add_argument('--ip', type=str, help='IP address of the Tilt-Sim device')
    parser.add_argument('--color', type=str, help='Tilt color from Tilt-Sim device')
    parser.add_argument('--starttemp', type=float, help='Starting temperature (°F)')
    parser.add_argument('--finaltemp', type=float, help='Final temperature (°F)')
    parser.add_argument('--og', type=float, help='Original Gravity (OG)')
    parser.add_argument('--fg', type=float, help='Final Gravity (FG)')
    parser.add_argument('--time', type=int, help='Total simulation time (minutes)')

    args = parser.parse_args()

    # Load configuration from file if provided
    if args.config:
        config_data = read_config_file(args.config)
        if config_data:
            DEFAULTS.update(config_data)

    # Override defaults with command-line arguments if provided
    for key, value in vars(args).items():
        if value is not None:
            DEFAULTS[key] = value

    # Convert temperatures to milli-degrees Celsius
    start_temp = int((DEFAULTS['starttemp'] - 32) * 5/9 * 1000)
    end_temp = int((DEFAULTS['finaltemp'] - 32) * 5/9 * 1000)

    # Determine the direction of temperature change
    direction = determine_direction(start_temp, end_temp)

    total_temp_change = end_temp - start_temp
    number_of_changes = DEFAULTS['time'] * 60  # Total number of changes (1 per second)
    temp_change_per_interval = total_temp_change / number_of_changes

    gravity = max(DEFAULTS['og'], DEFAULTS['fg'])  # Start with the higher value (OG)
    final_gravity = min(DEFAULTS['og'], DEFAULTS['fg'])  # Target the lower value (FG)

    start_time = time.time()

    # Convert initial temperature to Fahrenheit for logging
    current_temp_fahrenheit = start_temp / 1000 * 9/5 + 32
    start_temp_fahrenheit = DEFAULTS['starttemp']

    # CLI output at start of simulation
    print("Simulated fermentation started. Monitor log file for progress.")

    # Open log file, in same dir as simferm.py, in write mode to overwrite existing content
    log_file_path = os.path.join(SCRIPT_DIR, 'simferm.log')
    with open(log_file_path, 'w') as log_file:
        # Start of simulation run
        timestamp = datetime.now()
        update_log(log_file, timestamp, script_version, current_temp_fahrenheit, DEFAULTS['color'], gravity, start_temp_fahrenheit, DEFAULTS['og'], is_start=True)

        # Run the simulation loop
        for i in range(number_of_changes):
            if (direction == "up" and start_temp >= end_temp) or (direction == "down" and start_temp <= end_temp):
                break  # Exit loop if target temperature is reached
            
            # Adjust the temperature based on the direction
            if direction == "up":
                start_temp += abs(temp_change_per_interval)
            else:  # direction == "down"
                start_temp -= abs(temp_change_per_interval)

            current_temp_fahrenheit = start_temp / 1000 * 9/5 + 32

            # Update log file with current progress
            timestamp = datetime.now()
            update_log(log_file, timestamp, script_version, current_temp_fahrenheit, DEFAULTS['color'], gravity, start_temp_fahrenheit, DEFAULTS['og'])

            # Execute curl command with updated values
            execute_curl_command(DEFAULTS['ip'], DEFAULTS['color'], current_temp_fahrenheit, gravity)

            # Adjust gravity value towards Final Gravity (FG)
            gravity_change = (DEFAULTS['og'] - final_gravity) / number_of_changes
            gravity = max(final_gravity, gravity - gravity_change)

            # Sleep to maintain accurate time interval
            elapsed_time = time.time() - start_time
            sleep_time = (i + 1) - elapsed_time
            if sleep_time > 0:
                time.sleep(sleep_time)

        # Execute the final curl command to ensure the last update is sent
        execute_curl_command(DEFAULTS['ip'], DEFAULTS['color'], current_temp_fahrenheit, gravity)

        # End of simulation run - use the current (final) values
        update_log(log_file, timestamp, script_version, current_temp_fahrenheit, DEFAULTS['color'], gravity, start_temp_fahrenheit, DEFAULTS['og'], is_end=True)

    # CLI output at end of simulation
    print("Simulated fermentation complete. Enjoy a simulated beer on me.")

    sys.exit(0)

if __name__ == "__main__":
    main()

