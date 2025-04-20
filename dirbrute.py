#!/usr/bin/env python3
import requests
import argparse
import sys
import time
import random
import json
import csv
import os
import re
import concurrent.futures
from urllib.parse import urlparse, urljoin
from datetime import datetime
try:
    from tqdm import tqdm
    tqdm_available = True
except ImportError:
    tqdm_available = False
    
try:
    from colorama import init, Fore, Style
    init()  # Initialize colorama
    colorama_available = True
except ImportError:
    colorama_available = False
    # Define dummy color classes if colorama is not available
    class DummyFore:
        def __getattr__(self, name):
            return ""
    class DummyStyle:
        def __getattr__(self, name):
            return ""
    Fore = DummyFore()
    Style = DummyStyle()

# === 🛡️ Banner ===
BANNER = r"""
   ___  _       _           _               _             
  |   \(_)_ _  (_)___ _ _  | |__ _  _ _ __ | |__  ___ _ _ 
  | |) | | ' \ | / _ \ ' \ | '_ \ || | '  \| '_ \/ -_) '_|
  |___/|_|_||_|/ \___/_||_||_.__/\_,_|_|_|_|_.__/\___|_|  
              |__/   [ Enhanced DirBrute v2.0 by AnshTech ]
"""

# List of common user agents for rotation
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1"
]

# Common file extensions to check
DEFAULT_EXTENSIONS = ["", ".html", ".php", ".asp", ".aspx", ".jsp", ".js", ".txt", ".pdf", ".zip", ".bak", ".old", ".cfg", ".config"]

# Common response codes and their meanings
RESPONSE_CODES = {
    200: f"{Fore.GREEN}OK{Style.RESET_ALL}",
    201: f"{Fore.GREEN}Created{Style.RESET_ALL}",
    301: f"{Fore.YELLOW}Moved Permanently{Style.RESET_ALL}",
    302: f"{Fore.YELLOW}Found/Redirect{Style.RESET_ALL}",
    307: f"{Fore.YELLOW}Temporary Redirect{Style.RESET_ALL}",
    401: f"{Fore.RED}Unauthorized{Style.RESET_ALL}",
    403: f"{Fore.RED}Forbidden{Style.RESET_ALL}",
    404: f"{Fore.RED}Not Found{Style.RESET_ALL}",
    500: f"{Fore.MAGENTA}Server Error{Style.RESET_ALL}"
}

class DirBrute:
    def __init__(self, args):
        # Base configuration
        self.target_url = args.url.rstrip('/')
        self.wordlist_path = args.wordlist
        self.extensions = args.extensions.split(',') if args.extensions else DEFAULT_EXTENSIONS
        self.threads = args.threads
        self.timeout = args.timeout
        self.delay = args.delay
        self.jitter = args.jitter
        self.user_agent = args.user_agent
        self.random_agent = args.random_agent
        self.headers = self._parse_headers(args.headers)
        self.cookies = self._parse_cookies(args.cookies)
        self.proxy = {'http': args.proxy, 'https': args.proxy} if args.proxy else None
        self.output_file = args.output
        self.output_format = args.format
        self.follow_redirects = args.follow_redirects
        self.recursive = args.recursive
        self.max_depth = args.max_depth
        self.filter_size = args.filter_size
        self.filter_words = args.filter_words
        self.auth = (args.username, args.password) if args.username and args.password else None
        self.ignore_cert = args.ignore_cert
        self.verbose = args.verbose
        self.quiet = args.quiet
        self.force_https = args.force_https
        
        # Runtime variables
        self.wordlist = []
        self.discovered = []
        self.start_time = None
        self.total_requests = 0
        self.successful_requests = 0
        self.content_samples = {}  # To store response content samples for "soft 404" detection
        
        # Ensure the URL has a scheme
        if not self.target_url.startswith(('http://', 'https://')):
            self.target_url = ('https://' if self.force_https else 'http://') + self.target_url
            
        # Get base response for comparison (for soft 404 detection)
        self.base_response = self._get_base_response()
        
    def _parse_headers(self, headers_str):
        headers = {}
        if headers_str:
            for header in headers_str.split(','):
                if ':' in header:
                    key, value = header.split(':', 1)
                    headers[key.strip()] = value.strip()
        
        # Set user agent
        if self.user_agent:
            headers['User-Agent'] = self.user_agent
        return headers
    
    def _parse_cookies(self, cookies_str):
        cookies = {}
        if cookies_str:
            for cookie in cookies_str.split(','):
                if '=' in cookie:
                    key, value = cookie.split('=', 1)
                    cookies[key.strip()] = value.strip()
        return cookies
    
    def _get_base_response(self):
        """Get the base response to compare with for soft 404 detection"""
        try:
            # Make a request to a path that definitely doesn't exist
            random_path = f"/{random.randint(100000, 999999)}_non_existent_path_{random.randint(100000, 999999)}"
            response = self._make_request(self.target_url + random_path)
            if response:
                return {
                    'status': response.status_code,
                    'size': len(response.text),
                    'words': len(response.text.split()),
                    'content_sample': response.text[:1000]  # Store first 1000 chars
                }
        except:
            pass
        return None
    
    def _get_user_agent(self):
        """Get a random user agent if random_agent is enabled, otherwise return None"""
        if self.random_agent:
            return {'User-Agent': random.choice(USER_AGENTS)}
        return {}
    
    def _make_request(self, url, depth=0):
        """Make a request with all configured options"""
        # Apply delay with jitter if specified
        if self.delay > 0:
            jitter_value = random.uniform(0, self.jitter) if self.jitter > 0 else 0
            time.sleep(self.delay + jitter_value)
        
        headers = self.headers.copy()
        if self.random_agent:
            headers['User-Agent'] = random.choice(USER_AGENTS)
        
        try:
            self.total_requests += 1
            return requests.get(
                url, 
                headers=headers,
                cookies=self.cookies,
                proxies=self.proxy,
                timeout=self.timeout,
                auth=self.auth,
                allow_redirects=self.follow_redirects,
                verify=not self.ignore_cert
            )
        except requests.RequestException as e:
            if self.verbose and not self.quiet:
                print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} {e} - {url}")
            return None
    
    def is_soft_404(self, response):
        """Detect if a 200 response is actually a soft 404"""
        if not self.base_response or not response:
            return False
        
        # If status codes are different, this isn't a soft 404
        if self.base_response['status'] != response.status_code:
            return False
        
        # If the status code is 200 (OK), check for soft 404
        if response.status_code == 200:
            # Compare response sizes
            if self.filter_size:
                size_difference = abs(len(response.text) - self.base_response['size'])
                if size_difference < int(self.filter_size):
                    return True
            
            # Compare word counts
            if self.filter_words:
                words_difference = abs(len(response.text.split()) - self.base_response['words'])
                if words_difference < int(self.filter_words):
                    return True
                
            # Compare content similarity
            content_sample = response.text[:1000]
            similarity = self._calculate_similarity(content_sample, self.base_response['content_sample'])
            if similarity > 0.9:  # If 90% similar, likely a soft 404
                return True
        
        return False
    
    def _calculate_similarity(self, str1, str2):
        """Simple similarity calculation between two strings"""
        # This is a very basic implementation
        # For production, consider using more sophisticated algorithms
        smaller = min(len(str1), len(str2))
        if smaller == 0:
            return 0
        
        matching = sum(c1 == c2 for c1, c2 in zip(str1[:smaller], str2[:smaller]))
        return matching / smaller
    
    def load_wordlist(self):
        """Load and prepare the wordlist"""
        try:
            with open(self.wordlist_path, 'r', encoding='utf-8', errors='ignore') as f:
                self.wordlist = [line.strip() for line in f if line.strip()]
            
            print(f"{Fore.BLUE}[INFO]{Style.RESET_ALL} Loaded {len(self.wordlist)} words from wordlist")
            
            # Calculate total paths to check
            total_paths = len(self.wordlist) * len(self.extensions)
            print(f"{Fore.BLUE}[INFO]{Style.RESET_ALL} Total paths to check: {total_paths} (with {len(self.extensions)} extensions)")
            
            return True
        except FileNotFoundError:
            print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} Wordlist not found: {self.wordlist_path}")
            return False
        except Exception as e:
            print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} Failed to load wordlist: {str(e)}")
            return False
    
    def scan_path(self, path, depth=0):
        """Scan a single path with all configured extensions"""
        results = []
        
        for ext in self.extensions:
            full_path = f"{path}{ext}"
            url = f"{self.target_url}/{full_path}"
            
            response = self._make_request(url, depth)
            if not response:
                continue
            
            # Check if this is a soft 404
            is_soft = self.is_soft_404(response)
            
            # Get status color and description
            status_desc = RESPONSE_CODES.get(response.status_code, f"{Fore.BLUE}Unknown{Style.RESET_ALL}")
            
            # Prepare result data
            result = {
                'url': url,
                'status_code': response.status_code,
                'content_length': len(response.text),
                'words': len(response.text.split()),
                'lines': len(response.text.splitlines()),
                'redirect_url': response.url if self.follow_redirects and response.url != url else None,
                'is_directory': url.endswith('/'),
                'depth': depth,
                'is_soft_404': is_soft
            }
            
            # Determine if this is a "hit" (a valid discovery)
            is_hit = (response.status_code in [200, 201, 301, 302, 307, 401, 403] and not is_soft)
            
            if is_hit:
                self.successful_requests += 1
                self.discovered.append(result)
                results.append(result)
                
                # Print the discovery
                if not self.quiet:
                    size_info = f"[{result['content_length']} bytes]"
                    depth_info = f"[depth:{depth}]" if depth > 0 else ""
                    redirect_info = f" -> {result['redirect_url']}" if result['redirect_url'] else ""
                    soft_404_info = f"{Fore.YELLOW}[SOFT 404]{Style.RESET_ALL}" if is_soft else ""
                    
                    print(f"[{response.status_code}] {status_desc} {size_info} {depth_info} {url}{redirect_info} {soft_404_info}")
            
            # If verbose mode is on, print all results
            elif self.verbose and not self.quiet:
                soft_404_info = f"{Fore.YELLOW}[SOFT 404]{Style.RESET_ALL}" if is_soft else ""
                print(f"[{response.status_code}] {status_desc} [{result['content_length']} bytes] {url} {soft_404_info}")
            
            # If recursive scanning is enabled and this is a directory
            if self.recursive and is_hit and result['is_directory'] and depth < self.max_depth:
                # If this is a success and looks like a directory, add it to the scan queue
                if url.endswith('/'):
                    # This will be processed in the main scan method
                    pass
                else:
                    # Try adding a slash to see if it's a directory
                    dir_url = f"{url}/"
                    dir_response = self._make_request(dir_url, depth)
                    if dir_response and dir_response.status_code in [200, 301, 302, 307]:
                        result['is_directory'] = True
        
        return results
    
    def scan(self):
        """Main scanning method"""
        print(f"\n{Fore.BLUE}[INFO]{Style.RESET_ALL} Starting scan of {self.target_url}")
        print(f"{Fore.BLUE}[INFO]{Style.RESET_ALL} Thread count: {self.threads}")
        
        self.start_time = time.time()
        
        # Queue to hold all paths to be scanned (for recursion)
        scan_queue = [(word, 0) for word in self.wordlist]  # (path, depth)
        
        # Process the queue with threading
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.threads) as executor:
            # Submit initial scanning tasks
            future_to_path = {executor.submit(self.scan_path, path, depth): (path, depth) for path, depth in scan_queue}
            
            # Process results as they complete
            if tqdm_available and not self.quiet:
                pbar = tqdm(total=len(scan_queue))
            else:
                pbar = None
                
            for future in concurrent.futures.as_completed(future_to_path):
                path, depth = future_to_path[future]
                if pbar:
                    pbar.update(1)
                
                try:
                    results = future.result()
                    
                    # If recursive scanning is enabled, add discovered directories to the queue
                    if self.recursive and depth < self.max_depth:
                        for result in results:
                            if result['is_directory']:
                                # Extract the relative path
                                url_parts = urlparse(result['url'])
                                rel_path = url_parts.path.strip('/')
                                
                                # Add to queue and submit a new task
                                scan_queue.append((rel_path, depth + 1))
                                new_future = executor.submit(self.scan_path, rel_path, depth + 1)
                                future_to_path[new_future] = (rel_path, depth + 1)
                                if pbar:
                                    pbar.total += 1
                
                except Exception as e:
                    if self.verbose and not self.quiet:
                        print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} {str(e)} - {path}")
            
            if pbar:
                pbar.close()
        
        # Calculate scan time
        scan_time = time.time() - self.start_time
        
        # Print summary
        self._print_summary(scan_time)
        
        # Save results if output file specified
        if self.output_file:
            self._save_results()
        
        return self.discovered
    
    def _print_summary(self, scan_time):
        """Print scan summary"""
        if self.quiet:
            return
        
        print("\n" + "=" * 60)
        print(f"{Fore.GREEN}Scan Summary{Style.RESET_ALL}")
        print("=" * 60)
        print(f"Target URL:         {self.target_url}")
        print(f"Threads:            {self.threads}")
        print(f"Wordlist:           {self.wordlist_path} ({len(self.wordlist)} words)")
        print(f"Extensions:         {', '.join(ext if ext else '(none)' for ext in self.extensions)}")
        print(f"Recursion:          {'Enabled (depth: ' + str(self.max_depth) + ')' if self.recursive else 'Disabled'}")
        print(f"Total requests:     {self.total_requests}")
        print(f"Scan time:          {self._format_time(scan_time)}")
        print(f"Requests/second:    {self.total_requests / scan_time:.2f}")
        print(f"Discovered paths:   {len(self.discovered)}")
        print("=" * 60)
        
        # Print top discovered paths
        if self.discovered:
            print(f"\n{Fore.GREEN}Top Discovered Paths:{Style.RESET_ALL}")
            sorted_discoveries = sorted(self.discovered, key=lambda x: x['status_code'])
            for i, discovery in enumerate(sorted_discoveries[:20]):  # Show top 20
                status_desc = RESPONSE_CODES.get(discovery['status_code'], "Unknown")
                size_info = f"[{discovery['content_length']} bytes]"
                print(f"{i+1}. [{discovery['status_code']}] {status_desc} {size_info} {discovery['url']}")
            
            if len(self.discovered) > 20:
                print(f"... and {len(self.discovered) - 20} more. See output file for complete results.")
    
    def _format_time(self, seconds):
        """Format time in seconds to human-readable format"""
        if seconds < 60:
            return f"{seconds:.2f} seconds"
        elif seconds < 3600:
            minutes = seconds // 60
            remaining_seconds = seconds % 60
            return f"{int(minutes)} minutes, {remaining_seconds:.2f} seconds"
        else:
            hours = seconds // 3600
            remaining = seconds % 3600
            minutes = remaining // 60
            seconds = remaining % 60
            return f"{int(hours)} hours, {int(minutes)} minutes, {seconds:.2f} seconds"
    
    def _save_results(self):
        """Save results to a file"""
        try:
            if self.output_format == 'json':
                with open(self.output_file, 'w') as f:
                    # Convert to JSON-serializable format
                    results = []
                    for item in self.discovered:
                        item_copy = item.copy()
                        # Convert any non-serializable objects
                        for key, value in item_copy.items():
                            if not isinstance(value, (str, int, float, bool, list, dict, type(None))):
                                item_copy[key] = str(value)
                        results.append(item_copy)
                    
                    json.dump({
                        'target_url': self.target_url,
                        'scan_date': datetime.now().isoformat(),
                        'total_requests': self.total_requests,
                        'scan_time': time.time() - self.start_time,
                        'discovered_paths': results
                    }, f, indent=4)
            
            elif self.output_format == 'csv':
                with open(self.output_file, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['URL', 'Status Code', 'Content Length', 'Words', 'Lines', 'Is Directory', 'Depth'])
                    for item in self.discovered:
                        writer.writerow([
                            item['url'],
                            item['status_code'],
                            item['content_length'],
                            item['words'],
                            item['lines'],
                            item['is_directory'],
                            item['depth']
                        ])
            
            else:  # Simple text format
                with open(self.output_file, 'w') as f:
                    f.write(f"# DirBrute Scan Results\n")
                    f.write(f"# Target: {self.target_url}\n")
                    f.write(f"# Date: {datetime.now().isoformat()}\n")
                    f.write(f"# Total Requests: {self.total_requests}\n")
                    f.write(f"# Scan Time: {self._format_time(time.time() - self.start_time)}\n\n")
                    
                    for item in self.discovered:
                        f.write(f"[{item['status_code']}] {item['url']} [{item['content_length']} bytes]\n")
            
            print(f"\n{Fore.GREEN}[SUCCESS]{Style.RESET_ALL} Results saved to {self.output_file}")
        
        except Exception as e:
            print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} Failed to save results: {str(e)}")

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Enhanced DirBrute - Web Directory/File Scanner")
    
    # Target options
    target_group = parser.add_argument_group('Target')
    target_group.add_argument('-u', '--url', help='Target URL (e.g., http://example.com/)')
    target_group.add_argument('--force-https', action='store_true', help='Force HTTPS if no protocol specified')
    
    # Wordlist options
    wordlist_group = parser.add_argument_group('Wordlist')
    wordlist_group.add_argument('-w', '--wordlist', help='Path to wordlist file')
    wordlist_group.add_argument('-e', '--extensions', help='File extensions to check (comma-separated, e.g., .php,.html,.txt)')
    
    # Request options
    request_group = parser.add_argument_group('Request Configuration')
    request_group.add_argument('-t', '--threads', type=int, default=10, help='Number of concurrent threads (default: 10)')
    request_group.add_argument('-d', '--delay', type=float, default=0.0, help='Delay between requests in seconds (default: 0)')
    request_group.add_argument('-j', '--jitter', type=float, default=0.0, help='Random delay jitter in seconds (default: 0)')
    request_group.add_argument('--timeout', type=float, default=10.0, help='Request timeout in seconds (default: 10)')
    request_group.add_argument('--user-agent', help='Custom User-Agent header')
    request_group.add_argument('--random-agent', action='store_true', help='Use random User-Agent for each request')
    request_group.add_argument('--headers', help='Custom headers (format: "Header1:value1,Header2:value2")')
    request_group.add_argument('--cookies', help='Custom cookies (format: "name1=value1,name2=value2")')
    request_group.add_argument('--proxy', help='Proxy URL (e.g., http://127.0.0.1:8080)')
    request_group.add_argument('--follow-redirects', action='store_true', help='Follow redirects')
    request_group.add_argument('--ignore-cert', action='store_true', help='Ignore SSL certificate verification')
    
    # Authentication options
    auth_group = parser.add_argument_group('Authentication')
    auth_group.add_argument('--username', help='Basic auth username')
    auth_group.add_argument('--password', help='Basic auth password')
    
    # Scan options
    scan_group = parser.add_argument_group('Scan Behavior')
    scan_group.add_argument('-r', '--recursive', action='store_true', help='Recursively scan discovered directories')
    scan_group.add_argument('--max-depth', type=int, default=3, help='Maximum recursion depth (default: 3)')
    scan_group.add_argument('--filter-size', type=int, help='Filter out responses with similar size to 404 page (specify threshold)')
    scan_group.add_argument('--filter-words', type=int, help='Filter out responses with similar word count to 404 page (specify threshold)')
    
    # Output options
    output_group = parser.add_argument_group('Output')
    output_group.add_argument('-o', '--output', help='Output file to save results')
    output_group.add_argument('-f', '--format', choices=['txt', 'json', 'csv'], default='txt', help='Output format (default: txt)')
    output_group.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    output_group.add_argument('-q', '--quiet', action='store_true', help='Quiet mode (only show successful results)')
    
    args = parser.parse_args()
    
    # If not enough arguments are provided, return None to trigger interactive mode
    if len(sys.argv) <= 1:
        return None
        
    # Validate required arguments if command line mode
    if args.url is None or args.wordlist is None:
        parser.print_help()
        sys.exit(1)
        
    return args

def main():
    """Main function"""
    print(BANNER)
    
    # Handle command line arguments
    args = parse_arguments()
    
    # If no arguments provided or missing required args, use interactive mode
    if args is None:
        # Create a namespace object to hold our interactive inputs
        args = argparse.Namespace()
        
        # Get interactive inputs with proper validation
        args.url = input(f"{Fore.BLUE}🌐 Enter target URL:{Style.RESET_ALL} ").strip()
        args.wordlist = input(f"{Fore.BLUE}📂 Enter wordlist path:{Style.RESET_ALL} ").strip()
        args.extensions = input(f"{Fore.BLUE}🔍 Enter extensions (comma-separated, leave empty for defaults):{Style.RESET_ALL} ").strip()
        
        # Get threads with validation
        threads_input = input(f"{Fore.BLUE}⚙️ Enter number of threads [10]:{Style.RESET_ALL} ").strip()
        args.threads = int(threads_input) if threads_input and threads_input.isdigit() else 10
        
        # Get delay with validation
        delay_input = input(f"{Fore.BLUE}⏱️ Enter request delay in seconds [0]:{Style.RESET_ALL} ").strip()
        try:
            args.delay = float(delay_input) if delay_input else 0.0
        except ValueError:
            args.delay = 0.0
        
        args.output = input(f"{Fore.BLUE}📊 Enter output file (leave empty to skip):{Style.RESET_ALL} ").strip()
        
        format_input = input(f"{Fore.BLUE}📄 Enter output format (txt/json/csv) [txt]:{Style.RESET_ALL} ").strip().lower()
        args.format = format_input if format_input in ['txt', 'json', 'csv'] else 'txt'
        
        args.recursive = input(f"{Fore.BLUE}🔄 Enable recursive scanning? (y/n) [n]:{Style.RESET_ALL} ").lower() == 'y'
        
        max_depth_input = input(f"{Fore.BLUE}📏 Maximum recursion depth [3]:{Style.RESET_ALL} ").strip()
        args.max_depth = int(max_depth_input) if max_depth_input and max_depth_input.isdigit() else 3
        
        args.follow_redirects = input(f"{Fore.BLUE}➡️ Follow redirects? (y/n) [n]:{Style.RESET_ALL} ").lower() == 'y'
        args.verbose = input(f"{Fore.BLUE}🔊 Enable verbose output? (y/n) [n]:{Style.RESET_ALL} ").lower() == 'y'
        args.proxy = input(f"{Fore.BLUE}🔒 Enter proxy URL (leave empty to skip):{Style.RESET_ALL} ").strip()
        
        filter_size_input = input(f"{Fore.BLUE}🧮 Filter similar size? (enter number or leave empty):{Style.RESET_ALL} ").strip()
        try:
            args.filter_size = int(filter_size_input) if filter_size_input else None
        except ValueError:
            args.filter_size = None
            
        filter_words_input = input(f"{Fore.BLUE}🔤 Filter similar word count? (enter number or leave empty):{Style.RESET_ALL} ").strip()
        try:
            args.filter_words = int(filter_words_input) if filter_words_input else None
        except ValueError:
            args.filter_words = None
        
        # Set default values for other parameters
        args.timeout = 10.0
        args.jitter = 0.0
        args.user_agent = None
        args.random_agent = True
        args.headers = None
        args.cookies = None
        args.ignore_cert = False
        args.username = None
        args.password = None
        args.quiet = False
        args.force_https = False
    
    # Initialize the scanner
    scanner = DirBrute(args)
    
    # Load wordlist
    if not scanner.load_wordlist():
        return
    
    # Run the scan
    scanner.scan()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}[INFO]{Style.RESET_ALL} Scan interrupted by user")
    except Exception as e:
        print(f"\n{Fore.RED}[ERROR]{Style.RESET_ALL} {str(e)}")
        if "--debug" in sys.argv:
            raise
