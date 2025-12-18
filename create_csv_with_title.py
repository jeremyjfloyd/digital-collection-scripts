# Made by Jeremy Floyd December 2025
# This program reads in title from an external csv, and directory and file names to export as a csv manifest to ingest into a digital collections platform
import csv
from pathlib import Path

# --- Configuration ---
OUTPUT_FILENAME = "digital_object_ingest_manifest.csv"
METADATA_FILENAME = "metadata.csv" # <--- Name of the external metadata file, with source_metadata_identifier as key  to get title information
# --- End Configuration ---

current_path = Path.cwd()
csv_data = []

# --- 1. Load External Metadata into a Dictionary ---
metadata_map = {}
metadata_path = current_path / METADATA_FILENAME

try:
    with open(metadata_path, mode='r', newline='', encoding='utf-8') as infile:
        # Use csv.DictReader to easily access columns by header name
        reader = csv.DictReader(infile)
        
        # Populate the dictionary for quick look-up
        for row in reader:
            # The key for the map is the 'source_metadata_identifier'
            key = row.get("source_metadata_identifier")
            if key:
                # Store the title row information
                metadata_map[key] = {
                    "title": row.get("title", ""), # Default to empty string if 'title' is missing
                }
            
    print(f"Successfully loaded {len(metadata_map)} entries from {METADATA_FILENAME}.")

except FileNotFoundError:
    print(f"ERROR: Metadata file '{METADATA_FILENAME}' not found. Titles will be blank.")
except Exception as e:
    print(f"An error occurred while reading {METADATA_FILENAME}: {e}. Titles will be blank.")


# --- 2. Build the Output CSV Data ---

# Header row
csv_data.append(["title", "source","source_identifier", "source_metadata_identifier",
"model", "purl", "parents", "series", "related_url", "file", "pdf_state"]) # Note: added 'parents' to the header

# Iterate through current directory entries
for entry in current_path.iterdir():
    # Check if the entry is a directory
    if entry.is_dir():
        directory_name = entry.name
        
        # 📌 The common key: directory_name
        source_metadata_identifier = directory_name
        
        # --- Metadata Lookup ---
        # Get the metadata for this directory using the key
        external_metadata = metadata_map.get(source_metadata_identifier, {})
        
        # Get the title from the external metadata, or default to a blank string
        title = external_metadata.get("title", "")
        
        # --- End Metadata Lookup ---

        # List all files within the directory
        try:
            files_list = [
                f.name 
                for f in entry.iterdir() 
                if f.is_file()
            ]
        except Exception:
            files_list = ["(Error: Could not read contents)"]
        
        files_string = ";".join(files_list)
        
        # Adding the other required fields
        source = directory_name
        source_identifier = directory_name
        model = "ArchivalMaterial"
        purl = "http://purl.dlib.indiana.edu/iudl/africanstudies/"+directory_name
        parents = "pz50gz79h"
        series = ""
        related_url = "https://purl.dlib.indiana.edu/iudl/findingaids/africanstudies/VAA9500"
        pdf_state = "downloadable"
        

        csv_data.append([
            title,
            source,
            source_identifier,
            source_metadata_identifier, 
            model, 
            purl, 
            parents, 
            series, 
            related_url, 
            files_string, 
            pdf_state
        ])

# --- 3. Write the Data to the Output CSV File ---
with open(OUTPUT_FILENAME, 'w', newline='', encoding='utf-8') as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerows(csv_data)
    

print(f"Successfully created manifest file: {OUTPUT_FILENAME}")
