## requirements.txt

```
requests>=2.25.1
colorama>=0.4.4
tqdm>=4.62.0
```

## README.md

```markdown
# DirBrute - Enhanced Web Directory/File Scanner

```
   ___  _       _           _               _             
  |   \(_)_ _  (_)___ _ _  | |__ _  _ _ __ | |__  ___ _ _ 
  | |) | | ' \ | / _ \ ' \ | '_ \ || | '  \| '_ \/ -_) '_|
  |___/|_|_||_|/ \___/_||_||_.__/\_,_|_|_|_|_.__/\___|_|  
              |__/   [ Enhanced DirBrute v2.0 by AnshTech ]
```

A powerful and feature-rich web directory and file scanner for web application security testing.

## Features

- **Multi-threaded scanning** for high performance
- **Recursive directory scanning** to find deeply nested content
- **Customizable file extension fuzzing** 
- **Soft 404 detection** to eliminate false positives
- **Multiple output formats**: TXT, JSON, CSV
- **Proxy support** for anonymity
- **User-agent rotation** to avoid detection
- **Progress tracking** with ETA and statistics
- **Response filtering** based on status codes, size and content
- **Authentication support** for protected resources
- **Colored output** for better readability
- **Interactive mode** for easier use
- **Detailed reporting** and statistics

## Installation

1. Clone this repository:
```bash
git clone https://github.com/anshtech/dirbrute.git
cd dirbrute
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Command Line Mode

```bash
python dirbrute.py -u http://example.com -w wordlist.txt
```

### Interactive Mode

Simply run the script without parameters:

```bash
python dirbrute.py
```

### Basic Options

```bash
python dirbrute.py -u https://example.com -w /path/to/wordlist.txt -t 20 -o results.json -f json
```

### Advanced Options

```bash
python dirbrute.py -u https://example.com -w wordlist.txt -e .php,.html,.bak -t 20 \
  --random-agent --follow-redirects -r --max-depth 5 -v \
  --proxy http://127.0.0.1:8080 --delay 0.5 --jitter 0.2
```

## Command Line Arguments

### Target Options
- `-u, --url`: Target URL (e.g., http://example.com/)
- `--force-https`: Force HTTPS if no protocol specified

### Wordlist Options
- `-w, --wordlist`: Path to wordlist file
- `-e, --extensions`: File extensions to check (comma-separated, e.g., .php,.html,.txt)

### Request Configuration
- `-t, --threads`: Number of concurrent threads (default: 10)
- `-d, --delay`: Delay between requests in seconds (default: 0)
- `-j, --jitter`: Random delay jitter in seconds (default: 0)
- `--timeout`: Request timeout in seconds (default: 10)
- `--user-agent`: Custom User-Agent header
- `--random-agent`: Use random User-Agent for each request
- `--headers`: Custom headers (format: "Header1:value1,Header2:value2")
- `--cookies`: Custom cookies (format: "name1=value1,name2=value2")
- `--proxy`: Proxy URL (e.g., http://127.0.0.1:8080)
- `--follow-redirects`: Follow redirects
- `--ignore-cert`: Ignore SSL certificate verification

### Authentication Options
- `--username`: Basic auth username
- `--password`: Basic auth password

### Scan Behavior
- `-r, --recursive`: Recursively scan discovered directories
- `--max-depth`: Maximum recursion depth (default: 3)
- `--filter-size`: Filter out responses with similar size to 404 page (specify threshold)
- `--filter-words`: Filter out responses with similar word count to 404 page (specify threshold)

### Output Options
- `-o, --output`: Output file to save results
- `-f, --format`: Output format (txt, json, csv)
- `-v, --verbose`: Verbose output
- `-q, --quiet`: Quiet mode (only show successful results)

## Examples

### Basic Scan
```bash
python dirbrute.py -u http://example.com -w common.txt
```

### Scan with Custom Extensions
```bash
python dirbrute.py -u http://example.com -w common.txt -e .php,.html,.txt,.zip,.bak
```

### Recursive Scan with Depth Limit
```bash
python dirbrute.py -u http://example.com -w common.txt -r --max-depth 5
```

### Scan with Proxy and Random User-Agent
```bash
python dirbrute.py -u http://example.com -w common.txt --random-agent --proxy http://127.0.0.1:8080
```

### Scan with Authentication
```bash
python dirbrute.py -u http://example.com -w common.txt --username admin --password password123
```

### Export Results as JSON
```bash
python dirbrute.py -u http://example.com -w common.txt -o results.json -f json
```

### Scan with Rate Limiting
```bash
python dirbrute.py -u http://example.com -w common.txt -d 0.5 -j 0.2
```

## Wordlists

The tool requires a wordlist file containing directory and file names to check. Here are some resources for obtaining wordlists:

- [SecLists](https://github.com/danielmiessler/SecLists/tree/master/Discovery/Web-Content)
- [DirBuster Lists](https://github.com/daviddias/node-dirbuster/tree/master/lists)
- [FuzzDB](https://github.com/fuzzdb-project/fuzzdb/tree/master/discovery/predictable-filepaths/filename-dirname-bruteforce)

## Best Practices

1. Always obtain proper authorization before scanning any website
2. Start with small wordlists and expand as needed
3. Use appropriate delays to avoid overwhelming the target server
4. Save your results for future reference
5. Use the appropriate extensions for the target technology (e.g., .php for PHP sites)

## Troubleshooting

### Common Issues

1. **Connection errors**: Check network connectivity and proxy settings
2. **Scan taking too long**: Reduce wordlist size or increase thread count
3. **High false positives**: Adjust filter-size or filter-words parameters
4. **Missing dependencies**: Ensure all required packages are installed

### Debug Mode

For troubleshooting, you can run the script with the `--debug` flag to see full error tracebacks:

```bash
python dirbrute.py -u http://example.com -w common.txt --debug
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool is provided for educational and ethical testing purposes only. Always obtain proper authorization before scanning any systems. The authors are not responsible for any misuse or damage caused by this tool.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

Created by AnshTech
```

The requirements.txt file includes the minimum required dependencies for the enhanced DirBrute tool to function properly. The README.md file provides comprehensive documentation that explains:

1. Tool features and capabilities
2. Installation instructions
3. Basic and advanced usage examples
4. Detailed command-line arguments explanations
5. Best practices for usage
6. Troubleshooting tips
7. License and disclaimer information

This documentation will make your tool more accessible to other users and provide clear instructions on how to get the most out of its enhanced capabilities. You can customize both files as needed to better match your specific requirements or additional features you might add in the future.
