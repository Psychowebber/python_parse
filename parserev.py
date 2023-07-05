import re
import datetime
import argparse
import gzip
from collections import Counter
import ipaddress

# Regular expression pattern to extract URLs
url_pattern = re.compile(r'\"([^\"]*)\"')

# Function to parse the log file and count hits per URL
def parse_log_file(file_path):
    url_hits = Counter()

    with open_log_file(file_path) as file:
        for line in file:
            match = url_pattern.search(line)
            if match:
                url = match.group(1)
                url_hits[url] += 1

    return url_hits

# Function to open log files (supports gzip compressed files)
def open_log_file(file_path):
    if file_path.endswith('.gz'):
        return gzip.open(file_path, 'rt')
    else:
        return open(file_path, 'r')

# Function to filter log entries based on time range
def filter_log_entries(file_path, start_time, end_time):
    filtered_entries = []
    with open_log_file(file_path) as file:
        for line in file:
            log_parts = line.split()
            if len(log_parts) < 4:
                continue  # Skip the entry if it doesn't have enough columns
            entry_time_str = log_parts[3][1:]
            try:
                entry_time = datetime.datetime.strptime(entry_time_str, '%d/%b/%Y:%H:%M:%S')
                if start_time <= entry_time <= end_time:
                    filtered_entries.append(line)
            except ValueError:
                continue  # Skip the entry if the datetime format is incorrect

    return filtered_entries

# Function to check if an IP address matches the specified pattern
def is_matching_ip(ip_address):
    try:
        ip_obj = ipaddress.ip_address(ip_address)
        return ip_obj.version == 4 or ip_obj.version == 6
    except ValueError:
        return False

# Create the argument parser
parser = argparse.ArgumentParser(description='Log Analyzer')
parser.add_argument('--domain', required=True, help='Domain name')
parser.add_argument('--rotated', action='store_true', help='Trigger to search rotated logs with *.gz extension')
parser.add_argument('--days', type=int, help='Number of rotated logs to search')
args = parser.parse_args()

# Construct the log file pattern
log_file_pattern = "/home/jetrails/{domain}/logs/{domain}-ssl-access_log"

# Check if rotated logs are requested
if args.rotated:
    if not args.days:
        parser.error("--days is required when --rotated is specified")

    log_file_pattern += ".{}"

    # Calculate the start and end file numbers based on the number of days
    start_file_number = 1
    end_file_number = args.days

# Get the domain name
domain = args.domain

# Prompt the user to enter the value if --rotated flag is not provided
if not args.rotated:
    value_str = input("Value Format: 1 = 1 hour ago, 1.15 = 1 hour 15 minutes ago\nEnter the value: ")
    value = float(value_str)
else:
    value = None

# Calculate the start and end times based on the value provided
current_time = datetime.datetime.now()
start_time = current_time - datetime.timedelta(hours=int(value), minutes=int((value % 1) * 60))
end_time = current_time

# Parse the log files and get URL hit counts
url_hits = Counter()

if args.rotated:
    for file_number in range(start_file_number, end_file_number + 1):
        log_file = log_file_pattern.format(domain, file_number)
        url_hits += parse_log_file(log_file)
else:
    log_file = log_file_pattern.format(domain)
    url_hits = parse_log_file(log_file)

# Sort URLs by hit count in descending order
sorted_urls = sorted(url_hits.items(), key=lambda x: x[1], reverse=True)

# Display the top 5 URLs and corresponding IP addresses
print("Top 5 URLs and their hit counts:")
for i, (url, count) in enumerate(sorted_urls[:5]):
    print("URL: {}, Hits: {}".format(url, count))

    ip_hits = Counter()

    # Filter log entries for the specified time range and check IP addresses
    if args.rotated:
        filtered_entries = []
        for file_number in range(start_file_number, end_file_number + 1):
            log_file = log_file_pattern.format(domain, file_number)
            filtered_entries.extend(filter_log_entries(log_file, start_time, end_time))
    else:
        filtered_entries = filter_log_entries(log_file, start_time, end_time)

    for line in filtered_entries:
        log_parts = line.split()
        if len(log_parts) < 4:
            continue
        entry_ip = log_parts[0]
        if is_matching_ip(entry_ip):
            request_method = log_parts[5][1:]
            if request_method not in ("GET", "HEAD"):
                match = url_pattern.search(line)
                if match:
                    url = match.group(1)
                    ip_hits[entry_ip] += 1

    top_ip_addresses = ip_hits.most_common(5)
    print("Top 5 IP Addresses:")
    for ip, ip_count in top_ip_addresses:
        print("IP: {}, Hits: {} - https://www.abuseipdb.com/check/{}".format(ip, ip_count, ip))

    print("---------------------------------")
