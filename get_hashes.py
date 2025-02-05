import requests
import hashlib
import csv
import os
import re



# Output CSV file to store the hashes
output_file = "whitelisted_js_files.csv"

# Function to calculate the SHA-256 hash of a file
def calculate_sha256(file_name):
    sha256_hash = hashlib.sha256()
    with open(file_name, "rb") as file:
        # Read the entire file content
        content = file.read()

        # Normalize line endings
        normalized_content = content.replace(b'\r\n', b'\n')

        # Decode to string for further normalization
        normalized_content_str = normalized_content.decode('utf-8', errors='ignore')

        # Preserve the header comments (if they start with /* and contain v) 
        # and remove inline comments (// or /* ... */) only from the rest of the content
        header_regex = r'/\*\!(.*?)(\n|\r\n)'
        header_match = re.search(header_regex, normalized_content_str)

        if header_match:
            # Get the header
            header = header_match.group(0)
            # Remove inline comments from the rest of the content
            content_without_inline_comments = re.sub(r'//.*|/\*.*?\*/', '', normalized_content_str[header_match.end():])
            # Combine the header with the cleaned content
            final_content = header + content_without_inline_comments
        else:
            final_content = normalized_content_str  # No header found, keep original content

        # Update the hash
        sha256_hash.update(final_content.encode('utf-8'))

    return sha256_hash.hexdigest()



# Function to load existing hashes from a CSV file into a dictionary
def load_existing_hashes(filename):
    existing_hashes = {}
    if os.path.exists(filename):
        with open(filename, mode="r", newline="") as file:
            reader = csv.reader(file)
            next(reader)  # Skip the header
            for row in reader:
                if len(row) == 2:
                    existing_hashes[row[0]] = row[1]  # filename -> hash
    return existing_hashes

# Function to save new hashes to the CSV file
def save_to_csv(data, filename):
    """Append new hashes to the existing CSV file."""
    with open(filename, mode="a", newline="") as file:
        writer = csv.writer(file)
        for file_name, hash_value in data.items():
            writer.writerow([file_name, hash_value])

# Main function to calculate hash and save it
def add_hash_to_whitelist(file_path):
    # Load existing hashes from the CSV file
    existing_hashes = load_existing_hashes(output_file)

    # Extract the file name (basename) from the full file path
    file_name = os.path.basename(file_path)

    # Calculate the hash of the new file
    new_hash_data = {}
    file_hash = calculate_sha256(file_path)
    
    # Check if the file's hash already exists in the whitelist
    if file_name not in existing_hashes or existing_hashes[file_name] != file_hash:
        new_hash_data[file_name] = file_hash
        print(f"New hash for {file_name}: {file_hash}")
        
        # Save the new hash to the CSV file
        save_to_csv(new_hash_data, output_file)
        print(f"Hash for {file_name} added to {output_file}")
    else:
        print(f"Hash for {file_name} already exists in the whitelist.")
