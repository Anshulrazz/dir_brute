# DirBrute - Enhanced Web Directory & File Scanner

```
   ___  _       _           _               _             
  |   \(_)_ _  (_)___ _ _  | |__ _  _ _ __ | |__  ___ _ _
  | |) | | ' \ | / _ \ ' \ | '_ \ || | '  \| '_ \/ -_) '_|
  |___/|_|_||_|/ \___/_||_||_.__/\_,_|_|_|_|_.__/\___|_|  
              |__/   [ Enhanced DirBrute v2.0 by AnshTech ]
```

A powerful and feature-rich web directory and file scanner built for penetration testers, bug bounty hunters, and security researchers.

---

## 🚀 Features

- **Multi-threaded scanning** for maximum speed
- **Recursive directory traversal** for deep scans
- **Smart file extension fuzzing** (e.g., .php, .html, .bak, .zip)
- **Soft 404 detection** to reduce false positives
- **Multiple output formats**: TXT, JSON, CSV
- **Proxy and user-agent rotation support**
- **Authentication support** (Basic Auth)
- **Response filtering** by size, status code, and content
- **Colored console output** for better readability
- **Interactive CLI mode**
- **Real-time progress tracking and statistics**

---

## 📦 Installation

```bash
git clone https://github.com/Anshulrazz/dir_brute.git
cd dirbrute
pip install -r requirements.txt
```

---

## 🛠 Usage

### 🔹 Quick Start

```bash
python dirbrute.py -u http://example.com -w wordlist.txt
```

### 🔹 Interactive Mode

```bash
python dirbrute.py
```

### 🔹 Example with Options

```bash
python dirbrute.py -u https://example.com -w common.txt -e .php,.html,.zip -t 20 -r --max-depth 5 \
  --random-agent --proxy http://127.0.0.1:8080 -o results.json -f json
```

---

## 📋 Command Line Arguments

### 🎯 Target Options

- `-u, --url`: Target URL
- `--force-https`: Use HTTPS if protocol not specified

### 🗂 Wordlist Options

- `-w, --wordlist`: Path to wordlist
- `-e, --extensions`: File extensions to fuzz (comma-separated)

### ⚙ Request Configuration

- `-t, --threads`: Number of threads (default: 10)
- `-d, --delay`: Delay between requests
- `-j, --jitter`: Random jitter delay
- `--timeout`: Timeout per request
- `--user-agent`: Custom user agent
- `--random-agent`: Rotate user agent
- `--headers`: Custom headers
- `--cookies`: Custom cookies
- `--proxy`: Proxy URL
- `--follow-redirects`: Follow redirects
- `--ignore-cert`: Ignore SSL verification

### 🔐 Authentication

- `--username`: Username (basic auth)
- `--password`: Password (basic auth)

### 🔎 Scan Behavior

- `-r, --recursive`: Enable recursive scan
- `--max-depth`: Maximum recursion depth
- `--filter-size`: Ignore responses similar in size to 404
- `--filter-words`: Ignore responses similar in word count to 404

### 📤 Output

- `-o, --output`: Output file
- `-f, --format`: Format (txt, json, csv)
- `-v, --verbose`: Verbose output
- `-q, --quiet`: Only show successful results

---

## 💡 Examples

### ✅ Basic Scan

```bash
python dirbrute.py -u http://example.com -w wordlist.txt
```

### 🧠 Recursive Depth-Limited Scan

```bash
python dirbrute.py -u http://example.com -w wordlist.txt -r --max-depth 4
```

### 🕵 Scan with Proxy + Random Agent

```bash
python dirbrute.py -u http://example.com -w wordlist.txt --random-agent --proxy http://127.0.0.1:8080
```

### 🔒 Authenticated Scan

```bash
python dirbrute.py -u http://example.com -w wordlist.txt --username admin --password 1234
```

### 📄 Export JSON Report

```bash
python dirbrute.py -u http://example.com -w wordlist.txt -o result.json -f json
```

### 🐢 Delay & Jitter

```bash
python dirbrute.py -u http://example.com -w wordlist.txt -d 0.5 -j 0.2
```

---

## 📁 Wordlist Resources

- [SecLists - Web Content](https://github.com/danielmiessler/SecLists/tree/master/Discovery/Web-Content)
- [DirBuster lists](https://github.com/daviddias/node-dirbuster/tree/master/lists)
- [FuzzDB](https://github.com/fuzzdb-project/fuzzdb)

---

## ✅ Best Practices

- Get **legal permission** before scanning any system
- Start small and increase scan complexity as needed
- Use relevant file extensions for the target (e.g. `.php` for PHP apps)
- Respect target server limits — use delay and jitter
- Export and archive results for future review

---

## 🐞 Troubleshooting

- **Connection Errors**: Check proxies or internet
- **Long Scans**: Use smaller wordlists or increase threads
- **Too Many False Positives**: Use `--filter-size` or `--filter-words`
- **Debug Mode**:

```bash
python dirbrute.py -u http://example.com -w wordlist.txt --debug
```

---

## 📜 License

This project is licensed under the **MIT License**. See `LICENSE` file for details.

---

## ⚠ Disclaimer

This tool is intended **only for authorized testing and educational use**. Unauthorized scanning of systems is illegal. The developer is **not responsible** for any misuse.

---

## 🤝 Contributing

Pull requests are welcome!

```bash
git checkout -b feature/amazing-feature
git commit -m "Add amazing feature"
git push origin feature/amazing-feature
```

---

Created by **AnshTech Solutions**

📧 info\@anshtechsolutions.tech 

