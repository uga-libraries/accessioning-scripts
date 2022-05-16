"""
Purpose: generate format identification and create reports to support:
    1. Appraisal (technical and content based)
    2. Assigning processing tiers
    3. Identify risks to address immediately.
"""
import csv
import datetime
import os
import pandas as pd
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

import configuration as c


def fits_to_csv(fits_xml):
    """Extracts desired fields from a FITS XML file, reformats when necessary,
    and saves each format identification as a separate row in a CSV. Returns nothing."""

    def get_text(parent, element):
        """Returns a single value, regardless of if the element is missing, appears once, or repeats.
        For a missing element (some are optional), returns None.
        For an element that appears once, returns a string with the value of the text.
        For an element that repeats, returns a string with the text of every instance separated by semicolons.

        The parent element does not need to be a child of root.
        This function cannot be used if the desired value is an attribute instead of element text."""

        # If one or more instances of the element are present, returns the text.
        # For multiple instances, puts a semicolon between the text for each instance.
        try:
            value = ""
            value_list = parent.findall(f"fits:{element}", ns)
            for item in value_list:
                if value == "":
                    value += item.text
                else:
                    value += f"; {item.text}"
            return value
        # If the element is missing, item.text raises an AttributeError.
        # Returns None, which results in a blank cell in the CSV.
        except AttributeError:
            return None

    # Read the fits.xml file.
    tree = ET.parse(fits_xml)
    root = tree.getroot()

    # FITS namespace. All elements in the fits.xml are part of this namespace.
    ns = {"fits": "http://hul.harvard.edu/ois/xml/ns/fits/fits_output"}

    # Get the data from the desired elements and save to a list which will be the row in the CSV.
    # Selects the parent element (identity, fileinfo, and filestatus) from root first
    # to have consistent paths regardless of XML hierarchy.

    # There can be more than one format identity for the same file, so make a list of lists.
    # Each list is the information for one format identity.
    formats_list = []
    for identity in root.find("fits:identification", ns):
        format_data = [identity.get("format")]
        format_data.append(get_text(identity, "version"))
        format_data.append(identity.get("mimetype"))

        # If there is a PUID, add the PRONOM URL so it will match the NARA Preservation Action Plan CSV.
        # The value of PUID is None if there is no match.
        puid = get_text(identity, "externalIdentifier[@type='puid']")
        if puid:
            puid = "https://www.nationalarchives.gov.uk/pronom/" + puid
        format_data.append(puid)

        # For each tool, need to combine attributes with the name and version.
        tools = ""
        tools_list = identity.findall("fits:tool", ns)
        for tool in tools_list:
            tool_name = f"{tool.get('toolname')} version {tool.get('toolversion')}"
            if tools == "":
                tools += tool_name
            else:
                tools += f"; {tool_name}"
        format_data.append(tools)

        formats_list.append(format_data)

    # The information from fileinfo and filestatus is never repeated.
    # It will be added to the information about each format identification after it is gathered.
    file_data = []

    # Tests if there are multiple IDs for this format, based on how many format lists are in formats_list.
    if len(formats_list) == 1:
        file_data.append(False)
    else:
        file_data.append(True)

    fileinfo = root.find("fits:fileinfo", ns)
    file_data.append(get_text(fileinfo, "filepath"))
    filename = get_text(fileinfo, "filename")
    file_data.append(filename)

    # Calculates file extension from filename, which is everything after the last period in the name.
    file_data.append(filename.split(".")[-1])

    # Convert from a timestamp to something that is human readable.
    # Only use the first 10 digits to yet gear, month, and day.
    timestamp = get_text(fileinfo, "fslastmodified")
    date = datetime.date.fromtimestamp(int(timestamp[:10]))
    file_data.append(date)

    # Convert size from bytes to MB to be easier to read.
    # Rounded to 2 decimal places unless that will make it 0.
    size = get_text(fileinfo, "size")
    size = float(size) / 1000000
    if size > .01:
        size = round(size, 2)
    file_data.append(size)

    file_data.append(get_text(fileinfo, "md5checksum"))
    file_data.append(get_text(fileinfo, "creatingApplicationName"))

    filestatus = root.find("fits:filestatus", ns)
    file_data.append(get_text(filestatus, "valid"))
    file_data.append(get_text(filestatus, "well-formed"))
    file_data.append(get_text(filestatus, "message"))

    # Create the CSV rows by combining each list in format_list with file_data.
    # Save each row to the CSV.
    with open(f"{collection_folder}/{accession_number}_fits.csv", "a", newline="") as csv_open:
        csv_write = csv.writer(csv_open)

        for format_data in formats_list:
            format_data.extend(file_data)
            csv_write.writerow(format_data)


# Get accession folder path from script argument and verify it is correct.
# If there is an error, ends the script.
try:
    accession_folder = sys.argv[1]
except IndexError:
    print("\nThe required script argument is missing.")
    print("Please run the script again.")
    print("Script usage: python path/format-analysis.py path/accession_folder")
    sys.exit()

if not os.path.exists(accession_folder):
    print(f"\nThe provided accession folder '{accession_folder}' is not a valid directory.")
    print("Please run the script again.")
    print("Script usage: python path/format-analysis.py path/accession_folder")
    sys.exit()

# Calculates the accession number, which is the name of the last folder in the accession_folder path,
# and the collection folder, which is everything in the accession_folder path except the accession folder.
collection_folder, accession_number = os.path.split(accession_folder)

# Makes a folder for format identification information in the collection folder of the accession folder.
# If this folder already exists, prints an error and ends the script.
fits_output = f"{collection_folder}/{accession_number}_FITS"
try:
    os.mkdir(fits_output)
except FileExistsError:
    print(f"There is already FITS data for accession {accession_number}.")
    print(f"Delete or move the '{fits_output}' folder and run the script again.")
    sys.exit()

# Generates the format identification information for the accession using FITS
subprocess.run(f'"{c.FITS}" -r -i "{accession_folder}" -o "{fits_output}"', shell=True)

# Extract select format information for each file, with some data reformatting (PRONOM URL, date, size unit),
# and save to a CSV in the collection folder.
with open(f"{collection_folder}/{accession_number}_fits.csv", "w", newline="") as csv_open:
    header = ["Format_Name", "Format_Version", "MIME_Type", "PUID", "Identifying_Tool(s)", "Multiple_IDs",
              "File_Path", "File_Name", "File_Extension", "Date_Last_Modified", "Size_(MB)", "MD5",
              "Creating_Application", "Valid", "Well-Formed", "Status_Message"]
    csv_write = csv.writer(csv_open)
    csv_write.writerow(header)

for fits_xml in os.listdir(fits_output):
    fits_to_csv(f"{accession_folder}_FITS/{fits_xml}")

# Read the FITS, ITA (technical appraisal), and NARA CSVs into pandas for analysis and summarizing.
df_fits = pd.read_csv(f"{collection_folder}/{accession_number}_fits.csv")
df_ita = pd.read_csv("ITAfiles.csv")
df_nara = pd.read_csv("NARA_PreservationActionPlan_FileFormats.csv")

# Add columns to df_fits and df_nara to assist in better matching.
df_fits["name_version"] = df_fits["Format_Name"].str.lower() + " " + df_fits["Format_Version"]
df_fits["name_lower"] = df_fits["Format_Name"].str.lower()
df_nara["format_lower"] = df_nara["Format Name"].str.lower()
df_fits["ext_lower"] = df_fits["File_Extension"].str.lower()
df_nara["exts_lower"] = df_nara["File Extension(s)"].str.lower()

# List of columns to look at in NARA each time.
# Could not get it to work to save these to a separate dataframe - got duplicate columns after merging.
nara_columns = ["Format Name", "File Extension(s)", "PRONOM URL", "Risk Level", "Preservation Action",
                "Proposed Preservation Plan", "format_lower", "exts_lower"]

# Add risk information.

# PRONOM Identifier. Have to filter for PUID is not null or it will match unrelated formats with no PUID.
df_matching = pd.merge(df_fits[df_fits["PUID"].notnull()], df_nara[nara_columns], left_on="PUID", right_on="PRONOM URL", how="left")
df_unmatched = df_matching[df_matching["Risk Level"].isnull()].copy()
df_unmatched.drop(nara_columns, inplace=True, axis=1)
df_puid = df_matching[df_matching["Risk Level"].notnull()].copy()
df_puid = df_puid.assign(Match_Type="PRONOM")

# Add the formats with no PUID back into the unmatched dataframe for additional attempted matches.
# This dataframe will be updated after every attempted match with the ones that still aren't matched.
df_unmatched = pd.concat([df_fits[df_fits["PUID"].isnull()], df_unmatched])

# Name and version is a match (case insensitive).
df_matching = pd.merge(df_unmatched, df_nara[nara_columns], left_on="name_version", right_on="format_lower", how="left")
df_unmatched = df_matching[df_matching["Risk Level"].isnull()].copy()
df_unmatched.drop(nara_columns, inplace=True, axis=1)
df_version = df_matching[df_matching["Risk Level"].notnull()].copy()
df_version = df_version.assign(Match_Type="Format Name and Version")

# Name is a match (case insensitive). For ones without a version, which are NaN in name_version.
df_matching = pd.merge(df_unmatched, df_nara[nara_columns], left_on="name_lower", right_on="format_lower", how="left")
df_unmatched = df_matching[df_matching["Risk Level"].isnull()].copy()
df_unmatched.drop(nara_columns, inplace=True, axis=1)
df_name = df_matching[df_matching["Risk Level"].notnull()].copy()
df_name = df_name.assign(Match_Type="Format Name")

# Extension is a match (case insensitive).
# Will not match if NARA has more than one possible extension for that format version.
df_matching = pd.merge(df_unmatched, df_nara[nara_columns], left_on="ext_lower", right_on="exts_lower", how="left")
df_unmatched = df_matching[df_matching["Risk Level"].isnull()].copy()
df_unmatched.drop(nara_columns, inplace=True, axis=1)
df_ext = df_matching[df_matching["Risk Level"].notnull()].copy()
df_ext = df_ext.assign(Match_Type="File Extension")

# Add match type of "None" for any that are still unmatched.
df_unmatched = df_unmatched.assign(Match_Type="None")

# Combine the dataframes with different matches to save to spreadsheet
df_risk = pd.concat([df_puid, df_version, df_name, df_ext, df_unmatched])

# Add technical appraisal information.
# Creates a column with True or False for if that filename indicates deletion for technical appraisal
# because it contains a string from the first column in df_ita.
# re.escape is used to escape any unusual characters in the filename that have regex meaning.
ta_list = df_ita["SUBSTRING"].tolist()
df_risk["Technical Appraisal Candidate"] = df_risk["File_Name"].str.contains("|".join(map(re.escape, ta_list)))

# Summarize: by format identification.
# Summarize: by risk.
# Summarize: by parent.

# Make subsets based on different risk factors.

# Save reports.
with pd.ExcelWriter(f"{collection_folder}/{accession_number}_format-analysis.xlsx") as result:
    df_risk.to_excel(result, sheet_name="Risk", index=False)
