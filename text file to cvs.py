# Made by Jeremy Floyd December 2025
# Integrated with text file parsing logic March 2024
import csv
from pathlib import Path

# --- Configuration ---
output_filename = "digital_object_ingest_manifest.csv"
metadata_filename = "metadata.csv" 
manifest_filename = "VAA9500_manifest.txt"

# --- 1. Ask for user input ONCE at the start
USER_PURL_PREFIX = input("Input purl prefix [default: http://purl.dlib.indiana.edu/iudl/africanstudies/]: ") or "http://purl.dlib.indiana.edu/iudl/africanstudies/"
USER_PARENTS = input("Input parents [default: pz50gz79h]: ") or "pz50gz79h"
USER_RELATED_URL = input("Input related url [default: https://purl.dlib.indiana.edu/iudl/findingaids/africanstudies/VAA9500]: ") or "https://purl.dlib.indiana.edu/iudl/findingaids/africanstudies/VAA9500"


current_path = Path.cwd()
csv_data = []

# --- 2. Load External Metadata into a Dictionary ---
metadata_map = {}
metadata_path = current_path / metadata_filename

try:
    with open(metadata_path, mode='r', newline='', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            key = row.get("source_metadata_identifier")
            if key:
                metadata_map[key] = {"title": row.get("title", "")}
    print(f"Successfully loaded {len(metadata_map)} entries from {metadata_filename}.")
except FileNotFoundError:
    print(f"Warning: {metadata_filename} not found. Titles will be blank.")

# --- 3. Process the Manifest File ---
manifest_path = current_path / manifest_filename
current_dir_name = None
current_files = []

# temporary list to store parsed manifest groups before final processing
manifest_groups = []

try:
    with open(manifest_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            # Identify and clean directory (e.g., "./VAA9500-U-10486:" -> "VAA9500-U-10486")
            if line.startswith('./') and line.endswith(':'):
                if current_dir_name is not None:
                    manifest_groups.append((current_dir_name, ";".join(current_files)))
                
                current_dir_name = line.lstrip('./').rstrip(':')
                current_files = []
            
            # Identify .ptif files
            elif line.endswith('.ptif'):
                current_files.append(line)

        # Catch final entry
        if current_dir_name is not None:
            manifest_groups.append((current_dir_name, ";".join(current_files)))

    # --- 3. Build Final CSV Data ---
    for dir_name, concatenated_files in manifest_groups:
        # Lookup title from metadata_map using the directory name as the key
        title = metadata_map.get(dir_name, {}).get("title", "")

        # Assign variables per requirements
        source = dir_name
        source_identifier = dir_name
        source_metadata_identifier = dir_name
        model = "ArchivalMaterial"
        purl = USER_PURL_PREFIX + dir_name
        parents = USER_PARENTS
        series = ""
        related_url = USER_RELATED_URL
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
            concatenated_files, # Concatenated files with ";"
            pdf_state
        ])

except FileNotFoundError:
    print(f"Error: {manifest_filename} not found.")

# --- 4. Write to Output CSV ---
with open(output_filename, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    # Header row
    writer.writerow([
        "title", "source", "source_identifier", "source_metadata_identifier",
        "model", "purl", "parents", "series", "related_url", "file", "pdf_state"
    ])
    writer.writerows(csv_data)

print(f"Manifest created successfully: {output_filename}")