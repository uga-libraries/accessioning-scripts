"""
Purpose: generate format identification and create reports to support:
    1. Appraisal (technical and content based)
    2. Assigning processing tiers
    3. Identify risks to address immediately.

Produces a spreadsheet with risk information based on NARA preservation action plans and a local list of formats that
typically indicate removal during technical appraisal, with several tabs that summarize this information in different
ways.

Script usage: python path/format-analysis.py accession_folder
The accession_folder is the path to the folder with files to be analyzed.
Script output is saved in the parent folder of the accession folder.
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


def check_configuration():
    """Verifies all the expected variables are in the configuration file and paths are valid.
    Returns a list of paths with errors, or an empty list if there are no errors.
    This avoids wasting processing time by doing earlier steps before the path error is encountered."""

    errors = []

    try:
        if not os.path.exists(c.FITS):
            errors.append(f"FITS path '{c.FITS}' is not correct.")
    except AttributeError:
        errors.append("FITS variable is missing from the configuration file.")

    try:
        if not os.path.exists(c.ITA):
            errors.append(f"ITAfileformats.csv path '{c.ITA}' is not correct.")
    except AttributeError:
        errors.append("ITA variable is missing from the configuration file.")

    try:
        if not os.path.exists(c.RISK):
            errors.append(f"Riskfileformats.csv path '{c.RISK}' is not correct.")
    except AttributeError:
        errors.append("RISK variable is missing from the configuration file.")

    try:
        if not os.path.exists(c.NARA):
            errors.append(f"NARA Preservation Action Plans CSV path '{c.NARA}' is not correct.")
    except AttributeError:
        errors.append("NARA variable is missing from the configuration file.")

    # Returns the errors list. If there were no errors, it will be empty.
    return errors


def fits_to_csv(fits_xml):
    """Extracts desired fields from a FITS XML file, reformats when necessary,
    and saves each format identification as a separate row in a CSV. Returns nothing."""

    def get_text(parent, element):
        """Returns a single value, regardless of if the element is missing, appears once, or repeats.
        For a missing element (some are optional), returns None.
        For an element that appears once, returns a string with the value of the text.
        For an element that repeats, returns a string with the text of every instance separated by semicolons.

        The parent element does not need to be a child of root.
        Always use this function to get values even if haven't seen it repeat or be blank, just in case.
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
    # to have consistent paths regardless of the XML hierarchy.

    # There can be more than one format identity for the same file, so make a list of lists.
    # Each list is the information for one format identity.
    formats_list = []
    for identity in root.find("fits:identification", ns):
        format_data = [identity.get("format")]
        format_data.append(get_text(identity, "version"))

        # If there is a PUID, add the PRONOM URL so it will match the NARA Preservation Action Plan CSV.
        # The value of PUID is None if there is no PUID in the FITs.
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
    # It is saved to its own list and added to each format list before saving it to the CSV.
    # If information does not need reformatting, it is found and appended to the list in the same line.
    # If the information is reformatted or used to calculate additional information, it is saved to a variable first.
    file_data = []

    # Tests if there are multiple IDs for this format, based on how many format lists are in formats_list.
    if len(formats_list) == 1:
        file_data.append(False)
    else:
        file_data.append(True)

    fileinfo = root.find("fits:fileinfo", ns)
    file_data.append(get_text(fileinfo, "filepath"))

    # Calculates file extension from filename, which is everything after the last period in the name.
    # Adds the filename to the list later in the function so it can be the first column.
    filename = get_text(fileinfo, "filename")
    file_data.append(filename.split(".")[-1])

    # Convert from a timestamp to something that is human readable.
    # Only use the first 10 digits to get year, month, and day. Will be formatted YYYY-MM-DD.
    timestamp = get_text(fileinfo, "fslastmodified")
    date = datetime.date.fromtimestamp(int(timestamp[:10]))
    file_data.append(date)

    # Convert size from bytes to KB to be easier to read.
    # Rounded to 3 decimal places unless that will make it 0.
    size = get_text(fileinfo, "size")
    size = float(size) / 1000
    if size > .001:
        size = round(size, 3)
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
            format_data.insert(0, filename)
            format_data.extend(file_data)
            csv_write.writerow(format_data)


def match_nara_risk():
    """Adds risk information from NARA to the FITS data using different techniques, starting with the most accurate.
    A new column Match_Type is added to identify which technique produced a match.
    Returns a dataframe with the NARA matches."""

    # Adds columns to df_fits and df_nara to assist in better matching.
    # Most are lowercase versions of columns for case-insensitive matching.
    # Also combines format name and version in FITS, since NARA has that information in one column.
    df_fits["name_version"] = df_fits["Format_Name"].str.lower() + " " + df_fits["Format_Version"]
    df_fits["name_lower"] = df_fits["Format_Name"].str.lower()
    df_nara["format_lower"] = df_nara["Format Name"].str.lower()
    df_fits["ext_lower"] = df_fits["File_Extension"].str.lower()
    df_nara["exts_lower"] = df_nara["File Extension(s)"].str.lower()

    # List of columns to look at in NARA each time.
    nara_columns = ["Format Name", "File Extension(s)", "PRONOM URL", "Risk Level",
                    "Proposed Preservation Plan", "format_lower", "exts_lower"]

    # PRONOM Identifier is a match.
    # Have to filter for PUID is not null or it will match unrelated formats with no PUID.
    df_to_match = pd.merge(df_fits[df_fits["PUID"].notnull()], df_nara[nara_columns], left_on="PUID",
                           right_on="PRONOM URL", how="left")
    df_unmatched = df_to_match[df_to_match["Risk Level"].isnull()].copy()
    df_unmatched.drop(nara_columns, inplace=True, axis=1)
    df_puid = df_to_match[df_to_match["Risk Level"].notnull()].copy()
    df_puid = df_puid.assign(Match_Type="PRONOM")

    # Adds the formats with no PUID back into the unmatched dataframe for additional attempted matches.
    # This dataframe will be updated after every attempted match with the ones that still aren't matched.
    df_unmatched = pd.concat([df_fits[df_fits["PUID"].isnull()], df_unmatched])

    # Name and version is a match (case insensitive).
    df_to_match = pd.merge(df_unmatched, df_nara[nara_columns], left_on="name_version", right_on="format_lower",
                           how="left")
    df_unmatched = df_to_match[df_to_match["Risk Level"].isnull()].copy()
    df_unmatched.drop(nara_columns, inplace=True, axis=1)
    df_version = df_to_match[df_to_match["Risk Level"].notnull()].copy()
    df_version = df_version.assign(Match_Type="Format Name and Version")

    # Name is a match (case insensitive).
    # For ones without a version, which are NaN in name_version.
    df_to_match = pd.merge(df_unmatched, df_nara[nara_columns], left_on="name_lower", right_on="format_lower",
                           how="left")
    df_unmatched = df_to_match[df_to_match["Risk Level"].isnull()].copy()
    df_unmatched.drop(nara_columns, inplace=True, axis=1)
    df_name = df_to_match[df_to_match["Risk Level"].notnull()].copy()
    df_name = df_name.assign(Match_Type="Format Name")

    # Extension is a match (case insensitive).
    # Will not match if NARA has more than one possible extension for that format version.
    df_to_match = pd.merge(df_unmatched, df_nara[nara_columns], left_on="ext_lower", right_on="exts_lower", how="left")
    df_unmatched = df_to_match[df_to_match["Risk Level"].isnull()].copy()
    df_unmatched.drop(nara_columns, inplace=True, axis=1)
    df_ext = df_to_match[df_to_match["Risk Level"].notnull()].copy()
    df_ext = df_ext.assign(Match_Type="File Extension")

    # Adds match type of "None" for any that are still unmatched.
    df_unmatched = df_unmatched.assign(Match_Type="None")

    # Combines the dataframes with different matches to save to spreadsheet.
    df_matched = pd.concat([df_puid, df_version, df_name, df_ext, df_unmatched])

    # Removes columns that are just used for FITS and NARA comparisons from all dataframes.
    df_matched.drop(["name_version", "name_lower", "format_lower", "ext_lower", "exts_lower"], inplace=True, axis=1)
    df_fits.drop(["name_version", "name_lower", "ext_lower"], inplace=True, axis=1)
    df_nara.drop(["format_lower", "exts_lower"], inplace=True, axis=1)

    return df_matched


# Gets the accession folder path from the script argument and verifies it is correct.
# If there is an error, ends the script.
try:
    accession_folder = sys.argv[1]
except IndexError:
    print("\nThe required script argument (accession_folder) is missing.")
    print("Please run the script again.")
    print("Script usage: python path/format-analysis.py path/accession_folder")
    sys.exit()

if not os.path.exists(accession_folder):
    print(f"\nThe provided accession folder '{accession_folder}' is not a valid directory.")
    print("Please run the script again.")
    print("Script usage: python path/format-analysis.py path/accession_folder")
    sys.exit()

# Verifies the configuration file has all of the required variables and the file paths are valid.
# If there are any errors, prints an error and ends the script.
configuration_errors = check_configuration()
if len(configuration_errors) > 0:
    print('\nProblems detected with configuration.py:')
    for error in configuration_errors:
        print("   * " + error)
    print('\nCorrect the configuration file and run the script again. Use configuration_template.py as a model.')
    sys.exit()

# Calculates the accession number, which is the name of the last folder in the accession_folder path,
# and the collection folder, which is everything in the accession_folder path except the accession folder.
collection_folder, accession_number = os.path.split(accession_folder)

# Makes a folder for format identification information in the collection folder.
# If this folder already exists, prints an error and ends the script.
fits_output = f"{collection_folder}/{accession_number}_FITS"
try:
    os.mkdir(fits_output)
except FileExistsError:
    print(f"There is already FITS data for accession {accession_number}.")
    print(f"Delete or move the '{fits_output}' folder and run the script again.")
    sys.exit()

# Generates the format identification information for the accession using FITS.
subprocess.run(f'"{c.FITS}" -r -i "{accession_folder}" -o "{fits_output}"', shell=True)

# Starts a CSV in the collection folder, with a header row, for combined FITS information.
with open(f"{collection_folder}/{accession_number}_fits.csv", "w", newline="") as csv_open:
    header = ["File_Name", "Format_Name", "Format_Version", "PUID", "Identifying_Tool(s)", "Multiple_IDs",
              "File_Path", "File_Extension", "Date_Last_Modified", "Size_KB", "MD5",
              "Creating_Application", "Valid", "Well-Formed", "Status_Message"]
    csv_write = csv.writer(csv_open)
    csv_write.writerow(header)

# Extracts select format information for each file, with some data reformatting, and saves to the FITS CSV.
for fits_xml in os.listdir(fits_output):
    fits_to_csv(f"{accession_folder}_FITS/{fits_xml}")

# Read the FITS, ITA (technical appraisal), other formats that can indicate risk, and NARA CSVs
# into pandas for analysis and summarizing.
df_fits = pd.read_csv(f"{collection_folder}/{accession_number}_fits.csv")
df_ita = pd.read_csv(c.ITA)
df_risk = pd.read_csv(c.RISK)
df_nara = pd.read_csv(c.NARA)

# Adds risk information from NARA using different techniques, starting with the most accurate.
# A new column Match_Type is added to identify which technique produced a match.
df_results = match_nara_risk()

# Adds technical appraisal information.
# Creates a column with True or False for if that FITS format identification indicates something to delete
# during technical appraisal or if it is in a folder named "trash" or "trashes".
# re.escape is used to escape any unusual characters in the filename that have regex meanings.
ta_list = df_ita["FITS_FORMAT"].tolist()
df_results["Technical Appraisal Candidate"] = df_results["Format_Name"].str.contains("|".join(map(re.escape, ta_list)))
df_results["Technical Appraisal Candidate"] = df_results["File_Path"].str.contains("trash")

# Adds other risk information.
# Creates a column with True or False for if that FITs format identification indicates a possible risk.
risk_list = df_risk["FITS_FORMAT"].tolist()
df_results["Other Risk Indicator"] = df_results["Format_Name"].str.contains("|".join(map(re.escape, risk_list)))

# Summarizes by format name (version is not included).
files = df_fits.groupby("Format_Name")["Format_Name"].count()
files_percent = round((files / len(df_fits.index)) * 100, 2)
size = df_fits.groupby("Format_Name")["Size_KB"].sum()
size_percent = round((size / df_fits["Size_KB"].sum()) * 100, 2)
format_subtotals = pd.concat([files, files_percent, size, size_percent], axis=1)
format_subtotals.columns = ["File Count", "File %", "Size (KB)", "Size %"]

# Summarizes by risk level and technical appraisal,
# since risk is not a concern if will likely delete during technical appraisal.
df_results["Risk Level"].fillna("No NARA Match", inplace=True)
files = df_results.groupby(["Risk Level", "Technical Appraisal Candidate"], dropna=False)["Format_Name"].count()
files_percent = round((files / len(df_results.index)) * 100, 2)
size = df_results.groupby(["Risk Level", "Technical Appraisal Candidate"], dropna=False)["Size_KB"].sum()
size_percent = round((size / df_results["Size_KB"].sum()) * 100, 2)
risk_subtotals = pd.concat([files, files_percent, size, size_percent], axis=1)
risk_subtotals.columns = ["File Count", "File %", "Size (KB)", "Size %"]

# Makes subsets based on different risk factors.
nara_at_risk = df_results[df_results["Risk Level"] != "Low Risk"].copy()
tech_appraisal = df_results[df_results["Technical Appraisal Candidate"] == True].copy()
other_risk = df_results[df_results["Other Risk Indicator"] == True].copy()
multiple_ids = df_results[df_results["Multiple_IDs"] == True].copy()
duplicates = df_results.loc[df_results.duplicated(subset="MD5", keep=False)].copy()

# Saves all dataframes to a separate tab in an Excel spreadsheet in the collection folder.
# The index is not included if it is the row numbers.
with pd.ExcelWriter(f"{collection_folder}/{accession_number}_format-analysis.xlsx") as result:
    df_results.to_excel(result, sheet_name="Risk", index=False)
    format_subtotals.to_excel(result, sheet_name="Format Subtotals")
    risk_subtotals.to_excel(result, sheet_name="Risk Subtotals")
    nara_at_risk.to_excel(result, sheet_name="NARA Risk", index=False)
    tech_appraisal.to_excel(result, sheet_name="For Technical Appraisal", index=False)
    other_risk.to_excel(result, sheet_name="Other Risks", index=False)
    multiple_ids.to_excel(result, sheet_name="Multiple Formats", index=False)
    duplicates.to_excel(result, sheet_name="Duplicates", index=False)
