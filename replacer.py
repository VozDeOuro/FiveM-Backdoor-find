import os
import re
import requests
from colorama import Fore, Back, Style, init
from get_hashes import add_hash_to_whitelist
import time

# List of library names to detect in headers and multiline formats
library_names = ["Bootstrap", "jQuery", "Popper"]  # Add more libraries here as needed

# Dictionary for various JavaScript libraries and their download URLs and options for fetching the latest version
js_libraries = {
    "jquery": {
        "core": {
            "url": "https://code.jquery.com/jquery-{version}.min.js",
            "has_version": True  # jQuery has versioning in both headers and filenames
        },
        "ui": {
            "url": "https://code.jquery.com/ui/{version}/jquery-ui.min.js",
            "has_version": True  # jQuery UI has versioning in both headers and filenames
        }
    },
    "bootstrap": {
        "core": {
            "url": "https://cdn.jsdelivr.net/npm/bootstrap@{version}/dist/js/bootstrap.min.js",
            "has_version": True  # Bootstrap has versioning in both headers and filenames
        }
    },
    "popper": {
        "core": {
            "url": "https://cdn.jsdelivr.net/npm/popper.js@{version}/dist/umd/popper.min.js",  # For specific version
            "latest_url": "https://cdn.jsdelivr.net/npm/popper.js/dist/umd/popper.min.js",  # To fetch the latest version
            "has_version": False  # Popper.js doesn't have versioning in filenames or headers
        }
    }
    # New libraries can be added here following the same structure,
    # with 'has_version' set to True if the library typically includes version information
}

# Generalized regex for detecting libraries with headers like /*! jQuery v3.5.1 */
generalized_header_regex = rf'/\*!\s*({"|".join(library_names)})\s*(?:[^\d]*v)?(\d+\.\d+\.\d+)'

# Generic regex for lines starting with * Bootstrap v4.5.2 or similar multiline formats
generic_star_regex = rf'^\s*\*\s*({"|".join(library_names)})\s*v?(\d+\.\d+\.\d+)'

# Function to download JavaScript library files (like jQuery, Bootstrap, Popper.js)
def download_js_file(library, file_type="core", version=None):
    # Check if the library exists in the js_libraries dictionary
    if library in js_libraries and file_type in js_libraries[library]:
        library_info = js_libraries[library][file_type]

        # If no version is provided and the library supports versioning, fall back to latest if available
        if version is None:
            if not library_info["has_version"]:
                # For libraries without a version in the header (e.g., Popper.js)
                url = library_info.get("latest_url")
                if url:
                    print(Fore.WHITE + Style.BRIGHT +Back.YELLOW + f"Version not found, downloading the latest version of {library}...")
                    time.sleep(3)  # Pause for 5 seconds
                else:
                    raise ValueError(f"No version found and no latest version available for {library}.")
            else:
                # If `has_version` is True but no version was found, still try to fetch the latest version
                url = library_info.get("latest_url")
                if url:
                    print(Fore.YELLOW + f"Version not found, downloading the latest version of {library}...")
                    time.sleep(3)  # Pause for 5 seconds
                else:
                    raise ValueError(f"Version required for {library}, but no version found.")
        else:
            # Format the URL with the provided or default version
            url = library_info["url"].format(version=version)

        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            raise Exception(f"Failed to download {library} {file_type} version {version}")
    else:
        raise Exception(f"Unknown library or file type: {library} - {file_type}")

# Function to extract library name and version from header or multiline formats
def get_library_type_and_version(header):
    match = re.search(generalized_header_regex, header, re.MULTILINE)
    if not match:
        match = re.search(generic_star_regex, header, re.MULTILINE)
    if match:
        library = match.group(1).lower()  # Normalize library name to lowercase
        version = match.group(2)
        return library, "core", version  # Defaulting file_type to "core"
    return None, None, None

# Function to extract library name and version from filename
def get_version_from_filename(file_name):
    # Generic regex for filenames
    match = re.search(r'(\w+)-(\d+\.\d+\.\d+)\.min\.js', file_name)
    if match:
        library = match.group(1).lower()  # Normalize library name to lowercase
        version = match.group(2)
        return library, "core", version  # Defaulting file_type to "core"
    else:
        # Handle cases like popper.js which don't have a version in filename
        if "popper" in file_name.lower():
            return "popper", "core", None
        return None, None, None

# Function to check and replace JavaScript files (like jQuery, Bootstrap, Popper.js)
def check_and_replace(file_path):
    # Try to read up to 10 lines, but handle files with fewer lines gracefully
    header_lines = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for _ in range(10):
                line = next(f, None)  # Read each line, stop if there are fewer than 10
                if line is None:
                    break
                header_lines.append(line)
    except (UnicodeDecodeError, OSError):
        print(Fore.RED + f"Error reading file: {file_path}")
        return

    header = ''.join(header_lines)  # Combine the lines into a single string

    # Try to extract library type and version from the header
    library, file_type, version = get_library_type_and_version(header)

    # If not found in the header, try to get the version from the filename
    if not library or not version:
        file_name = os.path.basename(file_path)
        library, file_type, version = get_version_from_filename(file_name)

    # For libraries that don't have a version or for fallback to latest
    if library in js_libraries and file_type in js_libraries[library]:
        if not version:
            if not js_libraries[library][file_type]["has_version"]:
                version = None  # If no version, download the latest if allowed

    if library:
        version_display = version if version else "latest"
        print(Fore.CYAN + f"Found {library} {file_type} version {version_display} in {file_path}")
        time.sleep(1)  # Pause for 5 seconds

        # Ask user if they want to replace the file
        user_response = input(Fore.CYAN + f"Do you want to replace this file with the original {library} {file_type} version {version_display}? (y/n): ").strip().lower()

        if user_response == 'y':
            print(f"Downloading the original {library} {file_type} {version_display}...")
            time.sleep(5)  # Pause for 5 seconds
            original_content = download_js_file(library, file_type, version)
            
            # Define backup file name
            bkp_file = file_path + ".bkp"

            # Check if the backup file already exists
            if os.path.exists(bkp_file):
                print(Fore.YELLOW + f"Backup file {bkp_file} already exists. Deleting original file without backup.")
                time.sleep(5)  # Pause for 5 seconds
                os.remove(file_path)  # Remove the original file without making a backup
            else:
                # Create a backup of the original file
                os.rename(file_path, bkp_file)
                print(f"Renamed {file_path} to {bkp_file}")
                time.sleep(5)  # Pause for 5 seconds

            # Replace the file with the downloaded content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(original_content)
            print(Fore.GREEN + f"Replaced {file_path} with the original {library} {file_type} {version_display}.")
            time.sleep(5)  # Pause for 5 seconds
            
            # Add the new file's hash to the whitelist
            add_hash_to_whitelist(file_path)
    else:
        print(Fore.RED + f"No known library version found for {file_path}. Skipping...")
        print("=================================================================")
        time.sleep(5)  # Pause for 5 seconds
