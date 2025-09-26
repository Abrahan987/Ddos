# ⚡ HTTP Storm - Advanced Load Tester

Powerful HTTP request generator designed for Termux and Linux systems. Perfect for stress testing your own servers and applications.

## 🌩️ Features

- ⚡ **Asynchronous & Multi-threaded**: Up to 1000+ concurrent requests
- 🎯 **Smart Rate Control**: Configurable RPS with burst capabilities  
- 🔄 **Advanced Evasion**: Random headers, user agents, and payloads
- 📊 **Real-time Stats**: Live monitoring with detailed metrics
- ⚙️ **JSON Config**: Easy configuration management
- 🚀 **Multiple Modes**: Sync, Async, Distributed attacks
- 🎭 **Stealth Options**: Proxy rotation and traffic randomization

## ⚡ Quick Installation

### Termux:
```bash
# Clone repository  
git clone https://github.com/tu-usuario/http-storm.git
cd http-storm

# Auto install
chmod +x install.sh
./install.sh
Manual Install:
pkg update && pkg install python git
pip install requests aiohttp asyncio threading
🚀 Usage Examples
Basic Storm:
python storm.py https://your-server.com
Advanced Storm:
# 500 threads, 60 seconds, unlimited RPS
python storm.py https://your-server.com -t 500 -d 60 -r 0

# Async mode with config file
python storm.py https://your-server.com --async --config config/storm_config.json

# POST attack with payloads
python storm.py https://your-server.com -m POST -t 100 -d 30
Stealth Mode:
python storm.py https://your-server.com -t 50 -d 120 --stealth --random-delay
📊 Real-time Statistics
📈 Requests per second (RPS)
✅ Success/failure rates
⏱️ Average response times
📡 Data transfer metrics
🎯 HTTP status code distribution
⚠️ Legal Notice
FOR EDUCATIONAL AND AUTHORIZED TESTING ONLY
This tool is designed for:
Testing your own servers and applications
Load testing with explicit permission
Educational purposes and security research
Performance benchmarking
Users are fully responsible for compliance with applicable laws.
📝 License
MIT License - Use responsibly
