import argparse
import subprocess
import re
from collections import defaultdict
from heapq import nlargest

# Function to parse the log file and extract relevant information
def parse_logs(log_file):
    hit_counts = defaultdict(int)
    ip_counts = defaultdict(int)
    url_ips = defaultdict(list)
    bot_traffic = []

    # Regular expressions to extract IP addresses and URLs
    ip_pattern = r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"
    url_pattern = r'\"(GET|POST)\s(.+?)\s'

    with open(log_file, 'r') as file:
        for line in file:
            ip_match = re.search(ip_pattern, line)
            url_match = re.search(url_pattern, line)

            if ip_match and url_match:
                ip = ip_match.group()
                url = url_match.group(2)
                hit_counts[url] += 1
                ip_counts[ip] += 1
                url_ips[url].append(ip)

                user_agent = re.search(r'\"(.+?)\"', line)
                if user_agent and is_bot_traffic(user_agent.group(1)):
                    bot_traffic.append(line.strip())

    return hit_counts, ip_counts, url_ips, bot_traffic


# Function to check if the user agent represents bot traffic
def is_bot_traffic(user_agent):
    return not any(browser in user_agent.lower() for browser in ['chrome', 'firefox', 'opera', 'safari'])


# Function to get the top N items from a dictionary based on their values
def get_top_n_items(dictionary, n):
    return nlargest(n, dictionary, key=dictionary.get)


# Function to filter IP addresses starting with a specific prefix
def filter_ips(ip_list, prefix):
    return [ip for ip in ip_list if not ip.startswith(prefix)]


# Function to generate the URL for IP abuse check
def generate_abuse_check_url(ip_address):
    return f"https://ipabusedb.com/check/{ip_address}"


# Function to search the logs within the specified time frame
def search_logs_within_time(log_file, start_time, end_time):
    command = f"sed -n '/{start_time}/,/{end_time}/p' {log_file}"
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()

    return output.decode().strip()


# Main function to parse command-line arguments and execute the script
def main():
    # Define command-line arguments and help messages
    parser = argparse.ArgumentParser(prog='nginx_log_parser', description='Nginx Log Parser')
    parser.add_argument('--time', type=str, help='Specify the time frame to check through the logs')
    parser.add_argument('--domain', type=str, help='Specify the domain to search')
    parser.add_argument('--rotated', type=int, help='Specify the number of rotated logs to check')
    parser.add_argument('--url', action='store_true', help='Search for top 5 URLs and corresponding IP addresses')
    parser.add_argument('--ip', action='store_true', help='Search for top 5 IP addresses and corresponding URLs')
    parser.add_argument('--timeframe', type=str, help='Specify the time frame in 24-hour format')
    parser.add_argument('--bots', action='store_true', help='Include only bot traffic')
    args = parser.parse_args()

    # Print help if no arguments are provided
    if len(vars(args)) == 0:
        parser.print_help()
        return

    # Check the provided flags and execute the corresponding logic
    if args.time:
        # Process the time flag
        # Implement your logic here
        print(f"Checking logs for the last {args.time}...")

    if args.domain:
        # Process the domain flag
        # Implement your logic here
        print(f"Searching logs for the domain: {args.domain}...")

    if args.rotated:
        # Process the rotated flag
        # Implement your logic here
        print(f"Checking rotated logs for the domain: {args.domain} - {args.rotated}...")

    if args.url:
        # Process the URL flag
        # Implement your logic here
        print("Searching for top 5 URLs and corresponding IP addresses...")

    if args.ip:
        # Process the IP flag
        # Implement your logic here
        print("Searching for top 5 IP addresses and corresponding URLs...")

    if args.timeframe:
        # Process the timeframe flag
        # Implement your logic here
        print(f"Searching logs within the timeframe: {args.timeframe}...")

    if args.bots:
        # Process the bots flag
        # Implement your logic here
        print("Including only bot traffic...")

    # Example: Parsing logs using the parse_logs function
    log_file = '/home/jetrails/example.com/logs/example.com-ssl-access_log'
    hit_counts, ip_counts, url_ips, bot_traffic = parse_logs(log_file)

    # Example: Printing top 5 URLs and corresponding IP addresses
    top_urls = get_top_n_items(hit_counts, 5)
    for url in top_urls:
        ips = filter_ips(url_ips[url], '69.27.47')
        ip_with_urls = [f"{ip} ({generate_abuse_check_url(ip)})" for ip in ips]
        print(f"URL: {url} | Hits: {hit_counts[url]} | IP Addresses: {', '.join(ip_with_urls)}")

    # Example: Printing top 5 IP addresses and corresponding URLs
    top_ips = get_top_n_items(ip_counts, 5)
    for ip in top_ips:
        urls = filter_ips(url_ips[ip], '69.27.47')
        url_with_ips = [f"{url} ({generate_abuse_check_url(ip)})" for url in urls]
        print(f"IP Address: {ip} | Hits: {ip_counts[ip]} | URLs: {', '.join(url_with_ips)}")

    # Example: Printing bot traffic
    print("\nBot Traffic:")
    for line in bot_traffic:
        print(line)


if __name__ == '__main__':
    main()
