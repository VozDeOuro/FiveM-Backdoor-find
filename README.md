# FiveM Malware Detection and Prevention Tool

## Overview
This repository contains a set of Python scripts designed to detect and mitigate potential malware threats, specifically in JavaScript and Lua scripts. The tool analyzes files for obfuscated code, suspicious patterns, and known malware signatures, helping administrators secure their environments.

## Features
- **Regex-Based Malware Detection**: Detects obfuscated strings, suspicious function calls, and known malware signatures in JavaScript and Lua files.
- **Whitelist Handling**: Maintains a whitelist of safe files to reduce false positives.
- **Automated Hash Checking**: Computes and verifies SHA-256 hashes of files to track modifications.
- **JavaScript Library Integrity Verification**: Checks JavaScript files for tampering and allows replacement with official versions.
- **Interactive User Prompts**: Asks for user confirmation before modifying or flagging files.
- **Cross-Platform Compatibility**: Runs on Windows and Linux.

## Scripts
### 1. `malwarefind.py`
This is the main script for scanning directories and detecting malware.
#### Functionality:
- Loads a whitelist from a CSV file.
- Scans directories recursively, analyzing file content for suspicious patterns.
- Highlights potential threats and prompts the user for action.
- Offers to open flagged files in a code editor for manual review.
- Provides a secondary scan specifically for JavaScript files.

### 2. `get_hashes.py`
Handles SHA-256 hashing of files and maintains a whitelist of known safe JavaScript files.
#### Functionality:
- Computes file hashes while preserving header comments.
- Loads existing hashes from a CSV file.
- Adds new hashes to the whitelist if they are deemed safe.

### 3. `replacer.py`
Responsible for detecting outdated or potentially compromised JavaScript libraries and replacing them with the latest official versions.
#### Functionality:
- Extracts library name and version from file headers or filenames.
- Downloads verified versions of known JavaScript libraries (e.g., jQuery, Bootstrap, Popper.js).
- Creates a backup before replacing a file.
- Updates the hash whitelist after replacing a file.

## Installation
### Prerequisites
- Python 3.x
- Install dependencies from requirements.txt:
  ```bash
  pip install -r requirements.txt
  ```

## Usage
### Running the Malware Scanner
To scan a directory for malware:
```bash
python malwarefind.py /path/to/scan
```
Alternatively, if no path is provided, the script will prompt for directory selection.

## Contributing
Feel free to submit issues or pull requests to improve this project.

