import abuseipdb # Abuse IP DB integration broken into discrete file
import argparse # Used to parse arguments for script
import datetime # Used to calculate location in log file to start parsing
import json # Used to process json object from abuseipdb api
import re # Used to construct regex for URLs
import subprocess # Used to run shell commands
from collections import Counter # Used to count instance of IPs

# Regular expression pattern to extract URLs
url_pattern = re.compile(r'\"([^\"]*)\"')

# Define text colors
class colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

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

        # Get results for IP
        results = abuseipdb.ipCheck(ip)
        results_dict = json.loads(results)

        # Assign relevant info
        abuseScore = str(results_dict['data']['abuseConfidenceScore'])
        countryName = str(results_dict['data']['countryName'])
        domain = str(results_dict['data']['domain'])
        hostnames = str(results_dict['data']['hostnames'])
        isTor = str(results_dict['data']['isTor'])
        isp = str(results_dict['data']['isp'])
        lastReport = str(results_dict['data']['lastReportedAt'])
        totalReports = str(results_dict['data']['totalReports'])
        usageType = str(results_dict['data']['usageType'])

        # set associated text color for abuse score
        if abuseScore <= 33:
            scoreColor = colors.OKGREEN
        elif abuseScore <= 66 and abuseScore > 33:
            scoreColor = colors.WARNING
        else:
            scoreColor = colors.FAIL

        # Print report for IP
        print()
        print(colors.HEADER + "IP: {}, Hits: {} - https://www.abuseipdb.com/check/{}".format(ip, ip_count, ip) + colors.ENDC)
        print()

        print(colors.HEADER + "Host Info:" + colors.ENDC)
        print("Country: " + countryName)
        print("ISP: " + isp)
        print("Usage Type: " + usageType)
        print("Hostnames: " + hostnames)
        print("Domains: " + domain)
        print("Is TOR? " + isTor)
        print()

        print(colors.HEADER + "Abuse Info:" + colors.ENDC)
        print("Last Reported: " + lastReport)
        print("Number of Reports: " + totalReports)
        print(scoreColor + "Abuse Score: " + abuseScore + colors.ENDC)

    print("---------------------------------")
