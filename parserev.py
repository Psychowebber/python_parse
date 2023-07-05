import re
import datetime
import argparse
from collections import Counter
import ipaddress

# Regular expression pattern to extract URLs
url_pattern = re.compile(r'\"([^\"]*)\"')

# Function to parse the log file and count hits per URL
def parse_log_file(file_path):
    url_hits = Counter()

    with open(file_path, 'r') as file:
        for line in file:
            match = url_pattern.search(line)
            if match:
                url = match.group(1)
                url_hits[url] += 1

    return url_hits

# Function to filter log entries based on time range
def filter_log_entries(file_path, start_time, end_time):
    filtered_entries = []
    with open(file_path, 'r') as file:
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
parser.add_argument('--domain', action='store_true', help='Trigger to input the domain name')
parser.add_argument('--time', type=float, default=1, help='Time value')
args = parser.parse_args()

# Prompt the user to enter the domain if --domain flag is triggered
if args.domain:
    domain = input("Enter the domain: ")
else:
    domain = "moodfabrics.com"

# Construct the log file path
log_file = "/home/jetrails/{domain}/logs/{domain}-ssl-access_log".format(domain=domain)

# Prompt the user to enter the value if --time flag is provided
if args.time:
    value = args.time
else:
    value_str = input("Value Format: 1 = 1 hour ago, 1.15 = 1 hour 15 minutes ago\nEnter the value: ")
    value = float(value_str)

# Calculate the start and end times based on the value provided
current_time = datetime.datetime.now()
start_time = current_time - datetime.timedelta(hours=int(value), minutes=int((value % 1) * 60))
end_time = current_time

# Parse the log file and get URL hit counts
url_hits = parse_log_file(log_file)

# Sort URLs by hit count in descending order
sorted_urls = sorted(url_hits.items(), key=lambda x: x[1], reverse=True)

# Display the top 5 IP addresses by hit number
print("Top 5 IP Addresses by Hit Number:")
top_ip_addresses = Counter()
for i, (url, count) in enumerate(sorted_urls):
    # Assuming the IP address is the first column in the log file
    ip_address = url.split()[0]
    if is_matching_ip(ip_address) and not is_matching_ip(ip_address, "69.27.43.*"):
        top_ip_addresses[ip_address] += count
        if len(top_ip_addresses) >= 5:
            break

for ip, count in top_ip_addresses.most_common(5):
    print("IP: {}, Total Hits: {}".format(ip, count))

    ip_url_hits = Counter()
    filtered_entries = filter_log_entries(log_file, start_time, end_time)
    for line in filtered_entries:
        log_parts = line.split()
        if len(log_parts) < 4:
            continue
        entry_ip = log_parts[0]
        if entry_ip == ip:
            request_method = log_parts[5][1:]
            if request_method not in ("GET", "HEAD"):
                match = url_pattern.search(line)
                if match:
                    url = match.group(1)
                    ip_url_hits[url] += 1

    top_urls = ip_url_hits.most_common(5)
    print("Top 5 URLs and Their Hit Counts:")
    for url, count in top_urls:
        print("URL: {}, Hits: {}".format(url, count))

    print("---------------------------------")
