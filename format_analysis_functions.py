import csv
import datetime
import numpy as np
import os
import pandas as pd
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

# Configuration is made by the user on each new machine the script is installed on, so it could be missing.
try:
    import configuration as c
except ModuleNotFoundError:
    print("\nCould not run the script. Missing the required configuration.py file.")
    print("Make a configuration.py file using configuration_template.py and save it to the folder with the script.")
    sys.exit()


def argument(arg_list):
    """Gets the accession folder path from the script argument and verifies it is correct.
       Prints an explanation of any error encountered.
       Returns the path or False if there is an error."""

    # Tests if the required argument was given.
    try:
        accession_folder = arg_list[1]
    except IndexError:
        print("\nThe required script argument (accession_folder) is missing.")
        return False

    # If the argument is given, tests that it is a valid path.
    if not os.path.exists(accession_folder):
        print(f"\nThe provided accession folder '{accession_folder}' is not a valid directory.")
        return False

    # If the tests are passed, returns the path.
    return accession_folder


def check_configuration():
    """Verifies all the expected variables are in the configuration file and paths are valid.
    Returns a list of errors or an empty list if there are no errors."""

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

    return errors


def csv_to_dataframe(csv_file):
    """Reads a CSV into a dataframe, renames columns if it is FITs or NARA, and returns the dataframe.
    If special characters require the CSV to be read while ignoring encoding errors, it prints a warning."""

    # Reads the CSV into a dataframe, ignoring encoding errors from special characters if necessary.
    try:
        df = pd.read_csv(csv_file)
    except UnicodeDecodeError:
        print("UnicodeDecodeError when trying to read:", csv_file)
        print("The CSV was read by ignoring encoding errors, so those characters are omitted from the dataframe.")
        df = pd.read_csv(csv_file, encoding_errors="ignore")

    # Adds a prefix to the FITS and NARA dataframe columns so the source of the data is clear when the data is combined.
    if "fits" in csv_file:
        df = df.add_prefix("FITS_")
    elif "NARA" in csv_file:
        df = df.add_prefix("NARA_")

    return df


def update_fits(accession_folder, fits_output, collection_folder, accession_number):
    """Deletes any XML files in the FITS folder that do not have a corresponding file in the accession folder
    and makes a FITS XML file for anything in the accession folder that doesn't have one.
    This is used when the script is run again after doing some appraisal and/or file renaming."""

    # Makes a dataframe with the file paths from the accession folder.
    accession_paths = []
    for root, directories, files in os.walk(accession_folder):
        for file in files:
            accession_paths.append(os.path.join(root, file))
    accession_df = pd.DataFrame(accession_paths, columns=["accession_path"])

    # Makes a dataframe with the file names from the FITS folder and the original path from the FITS XML.
    # The original path will match the accession path.
    fits_data = {"fits_name": [], "fits_path": []}
    for file in os.listdir(fits_output):
        fits_data["fits_name"].append(file)
        tree = ET.parse(os.path.join(fits_output, file))
        root = tree.getroot()
        ns = {"fits": "http://hul.harvard.edu/ois/xml/ns/fits/fits_output"}
        fileinfo = root.find("fits:fileinfo", ns)
        path = fileinfo.find("fits:filepath", ns)
        fits_data["fits_path"].append(path.text)
    fits_df = pd.DataFrame(fits_data)

    # Makes a list of any files in the FITS folder but not the accession folder.
    # Deletes the FITS files without a corresponding file in the accession folder.
    compare_df = fits_df.merge(accession_df, left_on="fits_path", right_on="accession_path", how="left")
    fits_only_df = compare_df[compare_df["accession_path"].isnull()]
    fits_only_list = fits_only_df["fits_name"].to_list()
    for fits in fits_only_list:
        os.remove(os.path.join(fits_output, fits))

    # Makes a list of any files in the accession folder but not in the FITs folder.
    # Creates a FITS file for any files in the accession folder that do not have one.
    compare_df = fits_df.merge(accession_df, left_on="fits_path", right_on="accession_path", how="right")
    acc_only_df = compare_df[compare_df["fits_path"].isnull()]
    acc_only_list = acc_only_df["accession_path"].to_list()
    for file in acc_only_list:
        file_name = os.path.basename(file)
        fits_status = subprocess.run(f'"{c.FITS}" -i "{file}" -o "{collection_folder}/{accession_number}_FITS/{file_name}.fits.xml"',
                                     shell=True, stderr=subprocess.PIPE)
        if fits_status.stderr == b'Error: Could not find or load main class edu.harvard.hul.ois.fits.Fits\r\n':
            print("Unable to generate FITS XML.")
            print("The FITS folder and accession folder need to be on the same letter drive.")
            sys.exit()


def get_text(parent, element):
    """Returns a single string, regardless of if the element is missing, appears once, or repeats.
    The parent element does not need to be a child of root.
    This function cannot be used if the desired value is an attribute instead of element text.
    This function's output is used by fits_row as part of combining data from one XML into a list."""

    # FITS namespace. All elements in the FITS XML are part of this namespace.
    ns = {"fits": "http://hul.harvard.edu/ois/xml/ns/fits/fits_output"}

    # If one or more instances of the element are present, returns the element value(s) as a string.
    # For multiple instances, puts a semicolon between the value for each instance.
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


def fits_row(fits_file):
    """Extracts desired fields from a FITS XML file, reformatting when necessary, for each format identification.
    A single file may have multiple possible format identifications.
    Returns a list of lists, where each list is the information for a single format identification.
    This function's output is used by make_fits_csv() to combine all FITS information into a single CSV."""

    # Reads the FITS XML file. If there is a read error (rare), prints the filename and continues the script.
    try:
        tree = ET.parse(fits_file)
        root = tree.getroot()
    except ET.ParseError as et_error:
        print(f"\nCould not get format information from {os.path.basename(fits_file)}")
        print("ElementTree error:", et_error.msg)
        print("This file will not be included in the analysis.")
        return

    # FITS namespace. All elements in the FITS XML are part of this namespace.
    ns = {"fits": "http://hul.harvard.edu/ois/xml/ns/fits/fits_output"}

    # Gets the data from the desired elements and saves it to a list, which will be the row in the CSV.
    # Selects the parent element (identity, fileinfo, and filestatus) from root first
    # to have consistent paths regardless of the XML hierarchy.

    # There can be more than one format identity for the same file, so makes a dictionary with this information.
    # This will later be combined with information from other parts of FITS that never repeat.
    # The key is name+version (to keep unique) and the value is a dictionary with all the data points.
    # It doesn't include identifications that aren't useful (e.g., name+version same but only one has PUID).
    formats_dictionary = {}
    for identity in root.find("fits:identification", ns):

        # Gets the format name and version. No reformatting is required.
        format_data = {"name": identity.get("format"), "version": get_text(identity, "version")}

        # If there is a PUID, adds the PRONOM URL so it will match the NARA Preservation Action Plan CSV.
        # The value of PUID is None if there is no PUID in the FITs.
        puid = get_text(identity, "externalIdentifier[@type='puid']")
        if puid:
            puid = "https://www.nationalarchives.gov.uk/pronom/" + puid
        format_data["puid"] = puid

        # For each tool, combines the attributes with the name and version.
        # Makes a single, semicolon-separated string with all the tools.
        tools = ""
        tools_list = identity.findall("fits:tool", ns)
        for tool in tools_list:
            tool_name = f"{tool.get('toolname')} version {tool.get('toolversion')}"
            if tools == "":
                tools += tool_name
            else:
                tools += f"; {tool_name}"
        format_data["tools"] = tools

        # The rest of the loop adds format information to the formats dictionary
        # unless it meets one of the criteria used to simplify format identifications.
        format_key = format_data["name"] + format_data["version"]

        # Don't include a format identification if there is an identical name+version that has a PUID.
        # If a format with this name and version is already in the dictionary, this identification is only added
        # if the one in the dictionary has no PUID, which means this identification does have a PUID.
        if format_key in formats_dictionary:
            if formats_dictionary[format_key]["puid"] == "":
                formats_dictionary[format_key] = format_data

        # If one of the format identifications is empty, do not include any other format identifications.
        # If the current identification is empty, it deletes any previous identifications from the dictionary.
        # No new identifications are added to the dictionary if empty is already present.
        elif format_key == "empty":
            formats_dictionary = {format_key: format_data}
        elif "empty" in formats_dictionary:
            continue

        # If the identification did not match a simplification rule, adds the format to the dictionary.
        else:
            formats_dictionary[format_key] = format_data

    # The information from fileinfo and filestatus is never repeated.
    # It is saved to a list and added to each format identification before saving the format id to the CSV.
    # If information does not need reformatting, it is found and appended to the list in the same line.
    # If the information is reformatted or used to calculate additional information, it is saved to a variable first.
    file_data = []

    # Calculates if there are multiple IDs for this format, based on how many items are in the formats_dictionary.
    if len(formats_dictionary) == 1:
        file_data.append(False)
    else:
        file_data.append(True)

    fileinfo = root.find("fits:fileinfo", ns)

    # Converts the date last modified from a timestamp to something that is human readable.
    # Only uses the first 10 digits to get year, month, and day. Will be formatted YYYY-MM-DD.
    timestamp = get_text(fileinfo, "fslastmodified")
    date = datetime.date.fromtimestamp(int(timestamp[:10]))
    file_data.append(date)

    # Converts size from bytes to KB to be easier to read.
    # Rounded to 3 decimal places unless that will make it 0.
    size = get_text(fileinfo, "size")
    size = float(size) / 1000
    if size > .001:
        size = round(size, 3)
    file_data.append(size)

    # The rest of the data do not require reformatting.
    file_data.append(get_text(fileinfo, "md5checksum"))
    file_data.append(get_text(fileinfo, "creatingApplicationName"))
    filestatus = root.find("fits:filestatus", ns)
    file_data.append(get_text(filestatus, "valid"))
    file_data.append(get_text(filestatus, "well-formed"))
    file_data.append(get_text(filestatus, "message"))

    # Creates a list for each format identification by combining the file path, information from the formats_dictionary,
    # and the file_data list, and saves that list to the list which this function will return.
    fits_rows = []
    for format_id in formats_dictionary:
        row = [get_text(fileinfo, "filepath"), formats_dictionary[format_id]["name"],
               formats_dictionary[format_id]["version"], formats_dictionary[format_id]["puid"],
               formats_dictionary[format_id]["tools"]]
        row.extend(file_data)
        fits_rows.append(row)

    return fits_rows


def make_fits_csv(fits_output, collection_folder, accession_number):
    """Makes a single CSV with FITS information for all files in the accession.
    Each row in the CSV is a single format identification. A file may have multiple identifications."""

    # Makes a CSV in the collection folder, with a header row, for combined FITS information.
    header = ["File_Path", "Format_Name", "Format_Version", "PUID", "Identifying_Tool(s)", "Multiple_IDs",
              "Date_Last_Modified", "Size_KB", "MD5", "Creating_Application", "Valid", "Well-Formed", "Status_Message"]
    csv_open = open(f"{collection_folder}/{accession_number}_fits.csv", "w", newline="")
    csv_write = csv.writer(csv_open)
    csv_write.writerow(header)

    # Extracts select format information for each FITS file, with some data reformatting, and saves it to a CSV.
    # If it cannot save due to an encoding error, saves the filepath to a text file.
    for fits_xml in os.listdir(fits_output):
        rows_list = fits_row(os.path.join(fits_output, fits_xml))
        for row in rows_list:
            try:
                csv_write.writerow(row)
            except UnicodeEncodeError:
                with open(f"{collection_folder}/{accession_number}_encode_errors.txt", "a", encoding="utf-8") as text:
                    text.write(row[0] + "\n")
    csv_open.close()

    # If there were encoding errors, removes any duplicate files.
    # Files are duplicated in encode_errors.txt if they have more than one format identification.
    encode_errors_path = f"{collection_folder}/{accession_number}_encode_errors.txt"
    if os.path.exists(encode_errors_path):
        df_error = pd.read_csv(encode_errors_path, header=None)
        df_error.drop_duplicates(inplace=True)
        df_error.to_csv(encode_errors_path, header=False, index=False)


def update_risk(df_fits, df_risk, csv_path):
    """When the acc_full_risk_data.csv was produced during a previous iteration of the script,
    removes files in the risk csv which were deleted by the archivist since the csv was made and
    saves the updated information to acc_full_risk_data.csv.
    Returns the updated risk dataframe to be df_results for the rest of the script."""

    # Compares the file paths in the fits and risk dataframes,
    # and makes a list of unique paths that are only in the risk dataframe.
    df_compare = df_fits.merge(df_risk, on="FITS_File_Path", how="right")
    df_risk_only = df_compare[df_compare["FITS_Format_Name_x"].isnull()]
    risk_only_list = list(set(df_risk_only["FITS_File_Path"].to_list()))

    # Removes rows from df_risk if the path is not in df_fits.
    df_risk = df_risk[df_risk["FITS_File_Path"].isin(risk_only_list) == False]

    # Overwrites the existing acc_full_risk_data.csv with the updated information.
    df_risk.to_csv(csv_path, index=False)

    # Returns df_risk to use for df_results in the rest of the script.
    return df_risk


def match_nara_risk(df_fits, df_nara):
    """Combines risk information from NARA with the FITS data using different techniques,
    starting with the most accurate. A new column Match_Type is added to identify which technique produced a match.
    Returns a dataframe that incorporates the NARA matches."""

    # Adds temporary columns to df_fits and df_nara to assist in better matching.
    # Most are lowercase versions of columns for case-insensitive matching.
    # Also combines format name and version in FITS, since NARA has that information in one column,
    # and makes a column of the file extension in FITS, since NARA has that as a separate column.
    df_fits["name_version"] = df_fits["FITS_Format_Name"].str.lower() + " " + df_fits["FITS_Format_Version"].astype(str)
    df_fits["name_version"] = df_fits["name_version"].str.strip(" nan")
    df_fits["name_lower"] = df_fits["FITS_Format_Name"].str.lower()
    df_nara["format_lower"] = df_nara["NARA_Format Name"].str.lower()
    df_fits["ext_lower"] = df_fits["FITS_File_Path"].str.lower().str.split(".").str[-1]
    df_nara["exts_lower"] = df_nara["NARA_File Extension(s)"].str.lower()

    # List of columns to look at in the NARA dataframe each time.
    # These are removed from df_unmatched before a new technique is tried so the merge doesn't duplicate these columns.
    nara_columns = ["NARA_Format Name", "NARA_File Extension(s)", "NARA_PRONOM URL", "NARA_Risk Level",
                    "NARA_Proposed Preservation Plan", "format_lower", "exts_lower"]

    # For each matching technique, makes a dataframe merging FITS and NARA in a particular way and creates two df:
    # one with files that still aren't matched and one with files that matched.
    # The dataframes from matches for each technique are combined at the end of the function with any still unmatched.

    # Technique 1: PRONOM Identifier is a match.
    # Have to filter for PUID is not null or it will match unrelated formats with no PUID.
    df_matching = pd.merge(df_fits[df_fits["FITS_PUID"].notnull()], df_nara[nara_columns], left_on="FITS_PUID",
                           right_on="NARA_PRONOM URL", how="left")
    df_unmatched = df_matching[df_matching["NARA_Risk Level"].isnull()].copy()
    df_unmatched.drop(nara_columns, inplace=True, axis=1)
    df_unmatched = pd.concat([df_fits[df_fits["FITS_PUID"].isnull()], df_unmatched])
    df_puid = df_matching[df_matching["NARA_Risk Level"].notnull()].copy()
    df_puid = df_puid.assign(NARA_Match_Type="PRONOM")

    # Technique 2: Name, and version if it has one, is a match (case insensitive).
    # FITS has the pattern of "format_name version" since that is most common in NARA.
    # If the format name and version are combined in another way in NARA, this will not match it.
    df_matching = pd.merge(df_unmatched, df_nara[nara_columns], left_on="name_version", right_on="format_lower",
                           how="left")
    df_unmatched = df_matching[df_matching["NARA_Risk Level"].isnull()].copy()
    df_unmatched.drop(nara_columns, inplace=True, axis=1)
    df_format = df_matching[df_matching["NARA_Risk Level"].notnull()].copy()
    df_format = df_format.assign(NARA_Match_Type="Format Name")

    # Technique 3: Extension is a match (case insensitive).
    # Makes an expanded version of the NARA dataframe with one row per extension instead of one per format version.
    # NARA has a pipe separated string of extensions if a format has more than one.
    df_nara_expanded = df_nara[nara_columns].copy()
    df_nara_expanded["ext_separate"] = df_nara_expanded["exts_lower"].str.split(r"|")
    df_nara_expanded = df_nara_expanded.explode("ext_separate")
    df_matching = pd.merge(df_unmatched, df_nara_expanded, left_on="ext_lower", right_on="ext_separate", how="left")
    df_matching.drop("ext_separate", inplace=True, axis=1)
    df_unmatched = df_matching[df_matching["NARA_Risk Level"].isnull()].copy()
    df_unmatched.drop(nara_columns, inplace=True, axis=1)
    df_ext = df_matching[df_matching["NARA_Risk Level"].notnull()].copy()
    df_ext = df_ext.assign(NARA_Match_Type="File Extension")

    # Adds default text for risk and match type for any that are still unmatched.
    df_unmatched["NARA_Risk Level"] = "No Match"
    df_unmatched["NARA_Match_Type"] = "No NARA Match"

    # Combines each dataframe, with temporary columns removed and the index reset to one run of sequential numbers.
    df_matched = pd.concat([df_puid, df_format, df_ext, df_unmatched])
    df_matched.drop(["name_version", "name_lower", "format_lower", "ext_lower", "exts_lower"], inplace=True, axis=1)
    df_matched.index = np.arange(len(df_matched))

    return df_matched


def match_technical_appraisal(df_results, df_ita):
    """Adds technical appraisal categories to the results dataframe, which will already have FITS and NARA information.
    The categories are formats specified in the ITA spreadsheet, temporary files, and files in trash folders.
    Returns an updated results dataframe."""

    # Makes a column Technical_Appraisal and puts the value "Format" for any row with a FITS_Format_Name
    # that exactly matches any format in the ta_list (FITS_FORMAT column in ITAfileformats.csv).
    # re.escape prevents errors from characters in the format name that have regex meanings.
    df_results.loc[df_results["FITS_Format_Name"].isin(df_ita["FITS_FORMAT"].tolist()), "Technical_Appraisal"] = "Format"

    # Puts the value "Temp File" in the Technical_Appraisal column if the filename starts with "." or "~",
    # if the filename ends with ".tmp" or ".TMP", or if the filename is equal to "Thumbs.db" or "thumbs.db".
    # If the row already has "Format", it will be replaced with "Temp File".
    df_results["Path"] = df_results["FITS_File_Path"].apply(Path)
    df_results["Filename"] = df_results["Path"].apply(lambda x: x.name)
    temp_start = df_results["Filename"].str.startswith(('.', '~'))
    temp_end = df_results["Filename"].str.endswith(('.tmp', '.TMP'))
    temp_thumb = df_results["Filename"].isin(['Thumbs.db', 'thumbs.db'])
    df_results.loc[temp_start | temp_end | temp_thumb, "Technical_Appraisal"] = "Temp File"
    df_results.drop(["Path", "Filename"], axis=1, inplace=True)

    # Puts the value "Trash" in the Technical_Appraisal column for any row with a folder named
    # trash, Trash, trashes, or Trashes.
    # Including the \ before and after the search term so it matches a complete folder name.
    # If the row already has "Format" or "Temp File", it will be replaced with "Trash".
    df_results.loc[df_results["FITS_File_Path"].str.contains(r"\\trash\\|\\trashes\\", case=False), "Technical_Appraisal"] = "Trash"

    # Puts a default value for any row that is blank because it didn't match any category of technical appraisal.
    df_results["Technical_Appraisal"] = df_results["Technical_Appraisal"].fillna(value="Not for TA")

    return df_results


def match_other_risk(df_results, df_other):
    """Adds other risks to the results dataframe, which will already have FITS, NARA, and technical
    appraisal information. Other risk candidates include formats specified in the risk spreadsheet
    and formats with NARA low risk but a preservation plan other than retain. Returns an updated results dataframe."""

    # Adds information from Riskfileformats.csv to the dataframe if the format in both is exactly the same.
    # If the format isn't a match, the cells for the two columns from Riskfileformats.csv will be empty for that row.
    df_results = pd.merge(df_results, df_other, left_on="FITS_Format_Name", right_on="FITS_FORMAT", how="left")

    # Cleans up the dataframe after the merge by removing the format column imported from the CSV and
    # renaming the RISK_CRITERIA column (name in the CSV) to Other_Risk.
    df_results.drop(["FITS_FORMAT"], inplace=True, axis=1)
    df_results.rename(columns={"RISK_CRITERIA": "Other_Risk"}, inplace=True)

    # For files that didn't match a format in Riskfileformats.csv (Other_Risk is empty),
    # puts the value "NARA" for any row with a NARA risk level of low
    # and a NARA proposed preservation plan that is not "Retain".
    # It will be matched if the plan starts with the word Retain but includes caveats.
    df_results.loc[(df_results["Other_Risk"].isnull()) &
                   (df_results["NARA_Risk Level"] == "Low Risk") &
                   (df_results["NARA_Proposed Preservation Plan"] != "Retain"), "Other_Risk"] = "NARA"

    # Fills blanks in Other_Risk (no match in the CSV and not NARA Low Risk/Transform) to a default value.
    df_results["Other_Risk"] = df_results["Other_Risk"].fillna(value="Not for Other")

    return df_results


def subtotal(df, criteria, totals):
    """Returns a dataframe with file and size subtotals based on the provided criteria.
    If no files meet the criteria, adds an explanatory message to the dataframe instead."""

    # Calculates each subtotal and reformats the numbers.
    # All numbers are 3 decimal places and the size is in MB.
    files = df.groupby(criteria, dropna=False)["FITS_Format_Name"].count()
    files_percent = round((files / totals["Files"]) * 100, 3)
    size = round(df.groupby(criteria, dropna=False)["FITS_Size_KB"].sum()/1000, 3)
    size_percent = round((size / totals["MB"]) * 100, 3)

    # Combines the subtotals to a single dataframe and labels the columns.
    df_subtotals = pd.concat([files, files_percent, size, size_percent], axis=1)
    df_subtotals.columns = ["File Count", "File %", "Size (MB)", "Size %"]

    # If the dataframe is empty (no files that meet the criteria), the dataframe is given a default value.
    # This prevents an error from trying to save an empty dataframe to Excel later.
    if len(df_subtotals) == 0:
        df_subtotals = pd.DataFrame([["No data of this type"]])
    return df_subtotals


def media_subtotal(df, accession_folder):
    """"Returns a dataframe with subtotals by media folder, the top level folder inside the accession folder.
    For each folder, includes the number of files, size in MB, and number of files in each risk category."""

    # Makes a new column with media folder names, which are the first folder in the path after the accession folder.
    # If a file is not in a folder, it will have a value of NaN and be skipped when groups are calculated.
    df["Media"] = df["FITS_File_Path"].str.extract(fr"{re.escape(accession_folder)}\\(.*?)\\")

    # Calculates the total files and MB in each media folder. Size is converted to MB.
    files = df.groupby("Media")["FITS_File_Path"].count()
    size = round(df.groupby("Media")["FITS_Size_KB"].sum() / 1000, 3)

    # Calculates the number of files of each NARA risk level in each media folder.
    high = df[df["NARA_Risk Level"] == "High Risk"].groupby("Media")["FITS_File_Path"].count()
    moderate = df[df["NARA_Risk Level"] == "Moderate Risk"].groupby("Media")["FITS_File_Path"].count()
    low = df[df["NARA_Risk Level"] == "Low Risk"].groupby("Media")["FITS_File_Path"].count()
    unknown = df[df["NARA_Risk Level"] == "No Match"].groupby("Media")["FITS_File_Path"].count()

    # Calculates the number of files with formats that indicate technical appraisal in each media folder.
    # Does not include files in trash folders, which are always deleted.
    technical_appraisal = df[df["Technical_Appraisal"] == "Format"].groupby("Media")["FITS_File_Path"].count()

    # Calculates the number of files in the other risk categories in each media folder.
    other = df[df["Other_Risk"] != "Not for Other"].groupby("Media")["FITS_File_Path"].count()

    # Combines all the data into a single dataframe, with labeled columns.
    # Fills any empty cells with a 0 to make blanks easier to read.
    media = pd.concat([files, size, high, moderate, low, unknown, technical_appraisal, other], axis=1)
    media.columns = ["File Count", "Size (MB)", "NARA High Risk (File Count)", "NARA Moderate Risk (File Count)",
                     "NARA Low Risk (File Count)", "No NARA Match (File Count)",
                     "Technical Appraisal_Format (File Count)", "Other Risk Indicator (File Count)"]
    media.fillna(0, inplace=True)

    # Returns the media_subtotals dataframe.
    return media
