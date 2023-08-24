#!/usr/bin/env python3

import subprocess
import os
import argparse

# Get total system RAM in KB
mem_info = subprocess.check_output(["grep", "MemTotal", "/proc/meminfo"]).decode("utf-8").split()
total_ram = int(mem_info[1])

# Get a list of all parent PIDs
parent_pids = [int(pid) for pid in subprocess.check_output(["ps", "-eo", "pid="]).decode("utf-8").split()]

# Argument parsing
parser = argparse.ArgumentParser(description="Show top processes by RAM and CPU usage.")
parser.add_argument("--cpu", action="store_true", help="Sort by CPU usage. Example: --cpu")
parser.add_argument("--ram", action="store_true", help="Sort by RAM usage. Example: --ram")
parser.add_argument("--limit", type=int, default=10, help="Limit of top processes to show. Example: --limit 5")
parser.add_argument("--info", action="store_true", help="Show additional information about the script.")
args = parser.parse_args()

# If the --info flag is used, print some additional information and exit
if args.info:
    print("This script shows top processes by RAM and CPU usage.")
    print("Use --cpu to sort by CPU usage.")
    print("Use --ram to sort by RAM usage.")
    print("Use --limit <n> to specify the number of processes to show.")
    exit(0)

# Create a dictionary to store the process information
process_info = {}

# For each parent PID...
for pid in parent_pids:
    try:
        # Get the process name
        process_name = subprocess.check_output(["ps", "-p", str(pid), "-o", "comm="]).decode("utf-8").strip()
    except subprocess.CalledProcessError:
        # Skip if the process doesn't exist anymore
        continue

    try:
        # Sum the RSS (Resident Set Size) of the parent process and all its children
        rss_output = subprocess.check_output(["ps", "--ppid", str(pid), "-o", "rss="]).decode("utf-8")
        rss_values = [int(value) for value in rss_output.split()]
        total_ram_used = sum(rss_values)
    except subprocess.CalledProcessError:
        # Handle the case where there are no child processes
        total_ram_used = int(subprocess.check_output(["ps", "-p", str(pid), "-o", "rss="]).decode("utf-8"))

    # Get CPU usage using /proc/stat
    try:
        with open(f"/proc/{pid}/stat") as stat_file:
            stat_data = stat_file.read().split()
            utime = int(stat_data[13])
            stime = int(stat_data[14])
            starttime = int(stat_data[21])
            total_time = utime + stime
            uptime_seconds = float(open("/proc/uptime").read().split()[0])
            uptime_clock_ticks = os.sysconf(os.sysconf_names["SC_CLK_TCK"])
            seconds = uptime_seconds - (starttime / uptime_clock_ticks)
            cpu_usage = 100.0 * ((total_time / uptime_clock_ticks) / seconds)
    except (FileNotFoundError, IndexError, ZeroDivisionError, ValueError):
        cpu_usage = 0.0

    # Store the process information in the dictionary
    process_info[pid] = (process_name, total_ram_used, cpu_usage)

# Determine the sorting key based on the arguments
if args.ram:
    sort_key = lambda x: (x[1][1], -x[1][2])  # RAM, then CPU (desc)
    header = "Top {} Processes by RAM Usage:".format(args.limit)
elif args.cpu or (not args.cpu and not args.ram):
    sort_key = lambda x: (x[1][2], -x[1][1])  # CPU, then RAM (desc)
    header = "Top {} Processes by CPU Usage:".format(args.limit)
else:
    print("Invalid combination of arguments.")
    exit(1)

# Print the header
print(header)
print("{:<7} | {:<20} | {:<15} | {:<15} | {:<20}".format("PID", "Process Name", "RAM Used (KB)", "CPU Usage (%)", "% of Total RAM Used"))
print("-" * 85)

# Sort the dictionary and print the top processes
sorted_processes = sorted(process_info.items(), key=sort_key, reverse=True)[:args.limit]
for pid, (process_name, ram_used, cpu_usage) in sorted_processes:
    ram_percentage = (ram_used / total_ram) * 100
    print("{:<7} | {:<20} | {:<15} | {:<15.2f} | {:.2f}%".format(pid, process_name, ram_used, cpu_usage, ram_percentage))
