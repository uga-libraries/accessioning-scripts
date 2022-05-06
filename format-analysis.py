"""
Purpose: generate format identification and create reports to support:
    1. Appraisal (technical and content based)
    2. Assigning processing tiers
    3. Identify risks to address immediately.
"""
import os
import subprocess
import sys

import configuration as c

# Get accession folder path from script argument, verify it is correct, and make it the current directory.
# If there is an error, ends the script.
try:
    accession_folder = sys.argv[1]
    os.chdir(accession_folder)
except IndexError:
    print("\nThe required script argument is missing.")
    print("Please run the script again.")
    print("Script usage: python path/format-analysis.py path/accession_folder")
    sys.exit()
except FileNotFoundError:
    print(f"\nThe provided accession folder '{accession_folder}' is not a valid directory.")
    print("Please run the script again.")
    print("Script usage: python path/format-analysis.py path/accession_folder")
    sys.exit()

# Makes a folder for format identification information in the parent directory of the accession folder.
# If this folder already exists, prints an error and ends the script.
try:
    os.mkdir(f"{accession_folder}_FITS")
except FileExistsError:
    print(f"There is already FITS data for accession {accession_folder}.")
    print(f"Delete or move the '{accession_folder}_FITS' folder and run the script again.")
    sys.exit()

# Generates the format identification information for the accession using FITS
subprocess.run(f'"{c.FITS}" -r -i "{accession_folder}" -o "{f"{accession_folder}_FITS"}"', shell=True)

# Calculates the accession number, which is the name of the last folder in the accession_folder path.
accession_number = os.path.basename(accession_folder)

# Extract select format information for each file, with some data reformatting (PRONOM URL, date, size unit).

# Add additional information (file extension, parent folder).

# Add risk information.

# Summarize: by format identification.
# Summarize: by risk.
# Summarize: by parent.

# Make subsets based on different risk factors.

# Save reports.
