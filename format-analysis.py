"""
Purpose: generate format identification and create reports to support:
    1. Appraisal (technical and content based)
    2. Assigning processing tiers
    3. Identify risks to address immediately.
"""
import os
import sys

# Get accession folder path from script argument, verify it is correct, and make it the current directory.
# If there is an error, ends the script.
try:
    accession = sys.argv[1]
    os.chdir(accession)
except IndexError:
    print("\nThe required script argument is missing.")
    print("Please run the script again.")
    print("Script usage: python path/format-analysis.py path/accession_folder")
    sys.exit()
except FileNotFoundError:
    print(f"\nThe provided accession folder '{accession}' is not a valid directory.")
    print("Please run the script again.")
    print("Script usage: python path/format-analysis.py path/accession_folder")
    sys.exit()

# Generate format identification information for the accession using FITS
# and save the output to a folder in the same parent directory as the accession folder.


# Extract select format information for each file, with some data reformatting (PRONOM URL, date, size unit).

# Add additional information (file extension, parent folder).

# Add risk information.

# Summarize: by format identification.
# Summarize: by risk.
# Summarize: by parent.

# Make subsets based on different risk factors.

# Save reports.
