import re
import datetime
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

# Prompt the user to enter the absolute location of the log file
log_file = input("Enter the absolute location of the log file: ").strip()

# Prompt the user to enter the value in the format: 1 = 1 hour ago, 1.15 = 1 hour 15 minutes ago
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

# Display the top 5 IP addresses
print("Top 5 IP Addresses:")

top_ip_addresses = Counter()
for i, (url, count) in enumerate(sorted_urls[:5]):
    # Assuming the IP address is the first column in the log file
    ip_address = url.split()[0]
    if not is_matching_ip(ip_address, "69.27.43.*"):
        top_ip_addresses[ip_address] += count
        print("IP: {}, Hits: {}".format(ip_address, count))

print("---------------------------------")

# Display the top 5 URLs for each IP address
for ip, ip_count in top_ip_addresses.most_common(5):
    print("URLs for IP: {}, Total Hits: {}".format(ip, ip_count))

    ip_url_hits = Counter()
    filtered_entries = filter_log_entries(log_file, start_time, end_time)
    for line in filtered_entries:
        log_parts = line.split()
        entry_ip = log_parts[0]
        if entry_ip == ip:
            match = url_pattern.search(line)
            if match:
                url = match.group(1)
                ip_url_hits[url] += 1

    top_urls = ip_url_hits.most_common(5)
    print("Top 5 URLs:")
    for url, count in top_urls:
        print("URL: {}, Hits: {}".format(url, count))

    print("---------------------------------")
