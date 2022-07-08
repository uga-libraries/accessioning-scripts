# accessioning-scripts
Scripts used for accessioning born-digital archives

## format-analysis.py
Usage: `python format-analysis.py accession_folder`

The format analysis script extracts technical metadata from files in the accession folder, compares it to risk criteria, 
and produces a summary report to use for appraisal and evaluating an accession's complexity.

The script is designed to run repeatedly as the archivist makes changes based on the information,
such as deleting unwanted files or editing the risk assigned to each file. 
The script adjusts how it works based on the files in the accession folder, 
reusing information from previous script iterations where it will save time or allow manual updates:

1. If there are no other files in the accession folder, creates FITS data, FITS summary spreadsheet, risk spreadsheet, and analysis spreadsheet.
2. If there is a folder of FITS data, updates the FITS summary spreadsheet to remove anything deleted from the accession folder, and creates the risk spreadsheet and analysis spreadsheet.
3. If there is a risk spreadsheet, uses that to update the format analysis spreadsheet.

## technical-appraisal-logs.py