import os
import glob
import pandas as pd
from pathlib import Path

def check_directory(directory_path):
    """Check if a directory exists and list its contents"""
    if os.path.exists(directory_path):
        print(f"\nDirectory exists: {directory_path}")
        files = os.listdir(directory_path)
        if files:
            print(f"Files found ({len(files)}):")
            for file in files[:10]:  # Show first 10 files
                print(f"  - {file}")
            if len(files) > 10:
                print(f"  ... and {len(files) - 10} more files")
        else:
            print("Directory is empty")
        return True
    else:
        print(f"\n❌ Directory does not exist: {directory_path}")
        return False

# Step 1: Check expected download directory
expected_dir = os.path.abspath("ML Data/Arrival_Departure")
check_directory(expected_dir)

# Step 2: Check parent directory
cwd = os.getcwd()
print(f"\nCurrent working directory: {cwd}")
parent_dir = os.path.dirname(cwd)
ml_data_in_parent = os.path.join(parent_dir, "ML Data", "Arrival_Departure")
check_directory(ml_data_in_parent)

# Step 3: Check default download location
home_dir = os.path.expanduser("~")
default_downloads = os.path.join(home_dir, "Downloads")
check_directory(default_downloads)

# Step 4: Search for recently downloaded CSV files
print("\nSearching for recently downloaded CSV files in Downloads directory...")
if os.path.exists(default_downloads):
    csv_files = glob.glob(os.path.join(default_downloads, "*.csv"))
    if csv_files:
        print(f"Found {len(csv_files)} CSV files in Downloads folder:")
        for file in csv_files[:10]:
            print(f"  - {file}")
        if len(csv_files) > 10:
            print(f"  ... and {len(csv_files) - 10} more CSV files")

        # Optional: Preview first 2 CSV files
        for file in csv_files[:2]:
            try:
                df = pd.read_csv(file)
                print(f"\n📄 Preview of {file}:")
                print(df.head())
            except Exception as e:
                print(f"Could not preview {file}: {e}")
    else:
        print("No CSV files found in Downloads folder")

# Step 5: Look for files with airport codes
print("\nSearching for files containing airport codes...")
airport_codes = ["PWA", "DTN", "JAS", "CUB", "GDC", "GMU", "TPF", "AXN", "CLU", "CRG", "EGI", "HYR"]
found_files = []

locations_to_check = [
    os.getcwd(),
    os.path.join(os.getcwd(), "ML Data"),
    default_downloads
]

for location in locations_to_check:
    if os.path.exists(location):
        for root, dirs, files in os.walk(location):
            for file in files:
                for code in airport_codes:
                    if code in file:
                        full_path = os.path.join(root, file)
                        found_files.append(full_path)
                        break

if found_files:
    print(f"Found {len(found_files)} files containing airport codes:")
    for file in found_files[:10]:
        print(f"  - {file}")
    if len(found_files) > 10:
        print(f"  ... and {len(found_files) - 10} more files")
else:
    print("No files containing airport codes found")

# Step 6: Check for Chrome temp download files
print("\nChecking for partial/incomplete downloads (.crdownload)...")
partial_files = glob.glob(os.path.join(default_downloads, "*.crdownload"))
if partial_files:
    print(f"Found {len(partial_files)} partial download(s):")
    for file in partial_files:
        print(f"  - {file}")
else:
    print("No partial downloads found.")

# Step 7: Possible Chrome temp download locations
print("\nChecking other possible Chrome temporary download locations:")
temp_locations = [
    os.path.join(os.environ.get('TEMP', ''), 'Chrome Downloads'),
    os.path.join(os.environ.get('TMP', ''), 'Chrome Downloads'),
    os.path.join(home_dir, 'AppData', 'Local', 'Temp', 'Chrome Downloads') if os.name == 'nt' else None,
    os.path.join(home_dir, '.cache', 'google-chrome') if os.name == 'posix' else None
]

for loc in temp_locations:
    if loc and os.path.exists(loc):
        check_directory(loc)

# Wrap-up
print("\n✅ Done scanning all known locations.")
print("If files are still not found, try rerunning your download script with logging or manual download checks.")