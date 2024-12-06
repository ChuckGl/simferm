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

def daemonize():
    """Daemonizes the current process, allowing it to run in the background."""
    try:
        pid = os.fork()
        if pid > 0:
            # Parent process, exit so that the child process runs in the background
            print(f"Running in background with PID: {pid}")
            with open(os.path.join(SCRIPT_DIR, 'simferm.pid'), 'w') as pid_file:
                pid_file.write(f"{pid}\n")
            sys.exit(0)
    except OSError as e:
        print(f"Fork failed: {e}", file=sys.stderr)
        sys.exit(1)

def parse_testtime(testtime_str):
    """Parses the --testtime argument and returns the total duration in seconds."""
    if testtime_str == "nonstop":
        return None  # Indefinite test time

    if testtime_str.endswith("h"):  # Hours
        return int(testtime_str[:-1]) * 3600
    elif testtime_str.endswith("d"):  # Days
        return int(testtime_str[:-1]) * 86400
    else:
        raise ValueError("Invalid format for --testtime. Use '4h' for hours or '2d' for days.")

# ========================
# Main Function
# ========================

def main():
    parser = argparse.ArgumentParser(
        description="Simulate a fermentation using Tilt-Sim (https://github.com/spouliot/tilt-sim). Simferm logs to $HOME/simferm.log",
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
    parser.add_argument('--background', action='store_true', help='Run the script in the background.')
    parser.add_argument('--testtime', type=str, help='Total test time (e.g., 4h for hours, 2d for days, or nonstop for infinite)')

    args = parser.parse_args()

    # If the --background flag is set, daemonize the process
    # If the --background flag is set, daemonize the process
    if args.background:
        if os.getenv("INVOCATION_ID"):  # Check if running under systemd
            print("Systemd detected: ignoring --background flag")
        else:
            daemonize()

    # Calculate total test time in seconds (None means run indefinitely)
    total_test_duration = None
    if args.testtime:
        total_test_duration = parse_testtime(args.testtime)

    # Load configuration from file if provided
    if args.config:
        config_data = read_config_file(args.config)
        if config_data:
            DEFAULTS.update(config_data)

    # Override defaults with command-line arguments if provided
    for key, value in vars(args).items():
        if value is not None:
            DEFAULTS[key] = value

    start_time = time.time()

    while True:
        # Initialize temperatures and other variables at the start of each run
        start_temp = int((DEFAULTS['starttemp'] - 32) * 5/9 * 1000)
        end_temp = int((DEFAULTS['finaltemp'] - 32) * 5/9 * 1000)
        direction = determine_direction(start_temp, end_temp)
        total_temp_change = end_temp - start_temp
        number_of_changes = DEFAULTS['time'] * 60
        temp_change_per_interval = total_temp_change / number_of_changes
        gravity = max(DEFAULTS['og'], DEFAULTS['fg'])
        final_gravity = min(DEFAULTS['og'], DEFAULTS['fg'])
        current_temp_fahrenheit = start_temp / 1000 * 9/5 + 32
        start_temp_fahrenheit = DEFAULTS['starttemp']
        
        # Log start of the simulation
        print("Simulated fermentation started. Monitor log file for progress.")
        log_file_path = os.path.join(SCRIPT_DIR, 'simferm.log')
        with open(log_file_path, 'w+') as log_file:
            timestamp = datetime.now()
            update_log(log_file, timestamp, script_version, current_temp_fahrenheit, DEFAULTS['color'], gravity, start_temp_fahrenheit, DEFAULTS['og'], is_start=True)

            # Simulation loop for temperature and gravity change
            for i in range(number_of_changes):
                # Skip target temperature check for `nonstop`
                if total_test_duration is not None:
                    if (direction == "up" and start_temp >= end_temp) or (direction == "down" and start_temp <= end_temp):
                        break
                
                # Adjust temperature and gravity
                if direction == "up":
                    start_temp += abs(temp_change_per_interval)
                else:
                    start_temp -= abs(temp_change_per_interval)
                current_temp_fahrenheit = start_temp / 1000 * 9/5 + 32
                timestamp = datetime.now()
                update_log(log_file, timestamp, script_version, current_temp_fahrenheit, DEFAULTS['color'], gravity, start_temp_fahrenheit, DEFAULTS['og'])
                execute_curl_command(DEFAULTS['ip'], DEFAULTS['color'], current_temp_fahrenheit, gravity)

                # Gravity adjustment
                gravity_change = (DEFAULTS['og'] - final_gravity) / number_of_changes
                gravity = max(final_gravity, gravity - gravity_change)
                
                # Maintain accurate time intervals
                elapsed_time = time.time() - start_time
                sleep_time = (i + 1) - elapsed_time
                if sleep_time > 0:
                    time.sleep(sleep_time)

            # Final update and log for the simulation
            execute_curl_command(DEFAULTS['ip'], DEFAULTS['color'], current_temp_fahrenheit, gravity)
            update_log(log_file, timestamp, script_version, current_temp_fahrenheit, DEFAULTS['color'], gravity, start_temp_fahrenheit, DEFAULTS['og'], is_end=True)

        print("Simulated fermentation complete. Restarting due to 'nonstop' mode." if total_test_duration is None else "Simulated fermentation complete.")

        # Check if test time has elapsed if it's not `nonstop`
        if total_test_duration is not None:
            elapsed_time = time.time() - start_time
            if elapsed_time >= total_test_duration:
                print("Total test time has been reached. Stopping simulation.")
                break
        
        time.sleep(1)  # Delay before restarting if `nonstop`
        # Reset start time for the next run in nonstop mode
        start_time = time.time()

    sys.exit(0)


if __name__ == "__main__":
    main()

