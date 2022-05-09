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
    with open(f"{accession_folder}_FITS/{accession_number}_FITS.csv", "a", newline="") as csv_open:
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

# Calculates the accession number, which is the name of the last folder in the accession_folder path.
accession_number = os.path.basename(accession_folder)

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

# Extract select format information for each file, with some data reformatting (PRONOM URL, date, size unit),
# and save to a CSV.
with open(f"{accession_folder}_FITS/{accession_number}_FITS.csv", "w", newline="") as csv_open:
    header = ["Format_Name", "Format_Version", "MIME_Type", "PUID", "Identifying_Tool(s)", "Multiple_IDs",
              "File_Path", "File_Name", "File_Extension", "Date_Last_Modified", "Size_(MB)", "MD5",
              "Creating_Application", "Valid", "Well-Formed", "Status_Message"]
    csv_write = csv.writer(csv_open)
    csv_write.writerow(header)

for fits_xml in os.listdir(f"{accession_folder}_FITS"):
    if fits_xml.endswith(".csv"):
        continue
    fits_to_csv(f"{accession_folder}_FITS/{fits_xml}")

# Read the FITS, ITA (technical appraisal), and NARA CSVs into pandas for analysis and summarizing.
df_fits = pd.read_csv(f"{accession_folder}_FITS/{accession_number}_FITS.csv")
df_ita = pd.read_csv("ITAfiles.csv")
df_nara = pd.read_csv("NARA_PreservationActionPlan_FileFormats.csv")

# Add risk information.

# Make a dataframe with just formats that have a PUID and match them exactly to NARA.
# Include all the FITS information and from NARA "Risk Level", "Preservation Action", "Proposed Preservation Plan".
# Also add a column to indicate the match type is PUID.
df_puid = pd.merge(df_fits[df_fits["PUID"].notnull()],
                   df_nara[["PRONOM URL", "Risk Level", "Preservation Action", "Proposed Preservation Plan"]],
                   left_on="PUID", right_on="PRONOM URL", how="left")
df_puid = df_puid.assign(Match_Type="PRONOM")

# Add technical appraisal information.

# Summarize: by format identification.
# Summarize: by risk.
# Summarize: by parent.

# Make subsets based on different risk factors.

# Save reports.
