import re
import datetime
import argparse
from collections import Counter

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
def is_matching_ip(ip_address, pattern):
    ip_parts = ip_address.split('.')
    pattern_parts = pattern.split('.')
    for i in range(len(ip_parts)):
        if pattern_parts[i] != '*' and pattern_parts[i] != ip_parts[i]:
            return False
    return True

# Create the argument parser
parser = argparse.ArgumentParser(description='Log Analyzer')
parser.add_argument('--domain', type=str, help='Domain name')
parser.add_argument('--time', type=float, help='Time value')
args = parser.parse_args()

# Prompt the user to enter the domain if not provided as a flag
if args.domain:
    domain = args.domain
else:
    domain = input("Enter the domain: ")

# Construct the log file path
log_file = "/home/jetrails/{domain}/logs/{domain}-ssl-access_log".format(domain=domain)

# Prompt the user to enter the value if not provided as a flag
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

# Display the top 5 URLs and corresponding IP addresses
print("Top 5 URLs and their hit counts:")

for i, (url, count) in enumerate(sorted_urls[:5]):
    print("URL: {}, Hits: {}".format(url, count))

    ip_hits = Counter()
    filtered_entries = filter_log_entries(log_file, start_time, end_time)
    for line in filtered_entries:
        if url in line:
            # Assuming the IP address is the first column in the log file
            ip_address = line.split()[0]
            if not is_matching_ip(ip_address, "69.27.43.*"):
                ip_hits[ip_address] += 1

    top_ip_addresses = ip_hits.most_common(5)
    print("Top 5 IP Addresses:")
    for ip, ip_count in top_ip_addresses:
        print("IP: {}, Hits: {} - https://www.abuseipdb.com/check/{}".format(ip, ip_count, ip))

    print("---------------------------------")
