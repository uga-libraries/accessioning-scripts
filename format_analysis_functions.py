import csv
import datetime
import numpy as np
import os
import pandas as pd
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

# Configuration is made by the user on each new machine the script is installed on, so it could be missing.
try:
    import configuration as c
except ModuleNotFoundError:
    print("\nCould not run the script. Missing the required configuration.py file.")
    print("Make a configuration.py file using configuration_template.py and save it to the folder with the script.")
    sys.exit()


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


def csv_to_dataframe(csv_file):
    """Reads a CSV into a dataframe and returns the result. If the dataframe must be read by ignoring encoding
    errors, also prints a message to the terminal to alert users that something was wrong. This happens when there
    are special characters in the CSV. """

    try:
        df = pd.read_csv(csv_file)
    except UnicodeDecodeError:
        print("UnicodeDecodeError when trying to read:", csv_file)
        print("CSV was read with ignore encoding errors, so data may not be complete.")
        df = pd.read_csv(csv_file, encoding_errors="ignore")

    # Adds a prefix to the FITS and NARA dataframes so the source of the data is clear when the data is combined.
    if "fits" in csv_file:
        df = df.add_prefix("FITS_")
    elif "NARA" in csv_file:
        df = df.add_prefix("NARA_")

    return df


def update_fits(accession_folder, fits_output, collection_folder, accession_number):
    """Deletes any files in the FITS folder that do not have a corresponding file in the accession folder
    and makes a FITS file for anything in the accession folder that doesn't have one.
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
            print("Make sure that the FITS folder, the accession directory, and your current working directory are on the same letter drive.")
            sys.exit()


def fits_row(fits_file):
    """Extracts desired fields from a FITS XML file, reformatting when necessary, for each format identification.
    Returns a list of lists, where each list is the information for a single format identification."""

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

    # Reads the fits.xml file. If there is a read error (rare), prints the filename and continues the script.
    try:
        tree = ET.parse(fits_file)
        root = tree.getroot()
    except ET.ParseError as et_error:
        print(f"\nCould not get format information from {os.path.basename(fits_file)}")
        print("ElementTree error:", et_error.msg)
        print("This file will not be included in the analysis.")
        return

    # FITS namespace. All elements in the fits.xml are part of this namespace.
    ns = {"fits": "http://hul.harvard.edu/ois/xml/ns/fits/fits_output"}

    # Gets the data from the desired elements and saves it to a list, which will be the row in the CSV.
    # Selects the parent element (identity, fileinfo, and filestatus) from root first
    # to have consistent paths regardless of the XML hierarchy.

    # There can be more than one format identity for the same file, so makes a dictionary with this information.
    # The key is name+version (to keep unique) and the value is a dictionary with all the data points.
    # Doesn't include identifications that aren't useful (e.g., name+version same but only one has PUID).
    formats_dictionary = {}
    for identity in root.find("fits:identification", ns):
        format_data = {"name": identity.get("format"), "version": get_text(identity, "version")}

        # If there is a PUID, adds the PRONOM URL so it will match the NARA Preservation Action Plan CSV.
        # The value of PUID is None if there is no PUID in the FITs.
        puid = get_text(identity, "externalIdentifier[@type='puid']")
        if puid:
            puid = "https://www.nationalarchives.gov.uk/pronom/" + puid
        format_data["puid"] = puid

        # For each tool, combines attributes with the name and version.
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
        if format_key in formats_dictionary:
            if formats_dictionary[format_key]["puid"] == "":
                formats_dictionary[format_key] = format_data

        # If one of the format identifications is empty, do not include any other format information.
        elif format_key == "empty":
            formats_dictionary = {format_key: format_data}
        elif "empty" in formats_dictionary:
            continue

        # Otherwise, adds the format to the dictionary.
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

    file_data.append(get_text(fileinfo, "md5checksum"))
    file_data.append(get_text(fileinfo, "creatingApplicationName"))

    filestatus = root.find("fits:filestatus", ns)
    file_data.append(get_text(filestatus, "valid"))
    file_data.append(get_text(filestatus, "well-formed"))
    file_data.append(get_text(filestatus, "message"))

    # Creates a list for each format identification by combining info from formats_dictionary, file path, and file_data.
    # and saves that list to the list which this function will return.
    fits_rows = []
    for format_id in formats_dictionary:
        row = [get_text(fileinfo, "filepath"), formats_dictionary[format_id]["name"],
               formats_dictionary[format_id]["version"], formats_dictionary[format_id]["puid"],
               formats_dictionary[format_id]["tools"]]
        row.extend(file_data)
        fits_rows.append(row)

    return fits_rows


def make_fits_csv(fits_output, accession_folder, collection_folder, accession_number):
    """Makes a single CSV with FITS information for all files in the accession.
    Each row in the CSV is a single format identification. A file may have multiple identifications."""

    # Makes a CSV in the collection folder, with a header row, for combined FITS information.
    header = ["File_Path", "Format_Name", "Format_Version", "PUID", "Identifying_Tool(s)", "Multiple_IDs",
              "Date_Last_Modified", "Size_KB", "MD5", "Creating_Application", "Valid", "Well-Formed", "Status_Message"]
    csv_open = open(f"{collection_folder}/{accession_number}_fits.csv", "w", newline="")
    csv_write = csv.writer(csv_open)
    csv_write.writerow(header)

    # Extracts select format information for each FITS file, with some data reformatting, and saves to a CSV.
    # If it cannot save due to an encoding error, saves the filepath to a text file.
    encode_error = False
    for fits_xml in os.listdir(fits_output):
        rows_list = fits_row(f"{accession_folder}_FITS/{fits_xml}")
        for row in rows_list:
            try:
                csv_write.writerow(row)
            except UnicodeEncodeError:
                encode_error = True
                with open(f"{collection_folder}/{accession_number}_encode_errors.txt", "a", encoding="utf-8") as text:
                    text.write(row[0] + "\n")

    csv_open.close()

    # If there were encoding errors, removes any duplicate files.
    # Files are duplicated in encode_errors.txt if they have more than one format identification.
    if encode_error:
        df_error = pd.read_csv(f"{collection_folder}/{accession_number}_encode_errors.txt", header=None)
        df_error.drop_duplicates(inplace=True)
        df_error.to_csv(f"{collection_folder}/{accession_number}_encode_errors.txt", header=False, index=False)


def match_nara_risk(df_fits, df_nara):
    """Combines risk information from NARA with the FITS data using different techniques,
    starting with the most accurate. A new column Match_Type is added to identify which technique produced a match.
    Returns a dataframe with the NARA matches."""

    # Adds columns to df_fits and df_nara to assist in better matching.
    # Most are lowercase versions of columns for case-insensitive matching.
    # Also combines format name and version in FITS, since NARA has that information in one column,
    # and makes a column of the file extension in FITS, since NARA has that as a separate column.
    df_fits["name_version"] = df_fits["FITS_Format_Name"].str.lower() + " " + df_fits["FITS_Format_Version"].astype(str)
    df_fits["name_version"] = df_fits["name_version"].str.strip(" nan")
    df_fits["name_lower"] = df_fits["FITS_Format_Name"].str.lower()
    df_nara["format_lower"] = df_nara["NARA_Format Name"].str.lower()
    df_fits["ext_lower"] = df_fits["FITS_File_Path"].str.lower().str.split(".").str[-1]
    df_nara["exts_lower"] = df_nara["NARA_File Extension(s)"].str.lower()

    # List of columns to look at in NARA each time.
    nara_columns = ["NARA_Format Name", "NARA_File Extension(s)", "NARA_PRONOM URL", "NARA_Risk Level",
                    "NARA_Proposed Preservation Plan", "format_lower", "exts_lower"]

    # Technique 1: PRONOM Identifier is a match.
    # Have to filter for PUID is not null or it will match unrelated formats with no PUID.
    df_to_match = pd.merge(df_fits[df_fits["FITS_PUID"].notnull()], df_nara[nara_columns], left_on="FITS_PUID",
                           right_on="NARA_PRONOM URL", how="left")
    df_unmatched = df_to_match[df_to_match["NARA_Risk Level"].isnull()].copy()
    df_unmatched.drop(nara_columns, inplace=True, axis=1)
    df_puid = df_to_match[df_to_match["NARA_Risk Level"].notnull()].copy()
    df_puid = df_puid.assign(NARA_Match_Type="PRONOM")

    # Adds the formats with no PUID back into the unmatched dataframe for additional attempted matches.
    # This dataframe will be updated after every attempted match with the ones that still aren't matched.
    df_unmatched = pd.concat([df_fits[df_fits["FITS_PUID"].isnull()], df_unmatched])

    # Technique 2: Name, and version if it has one, is an exact match (case insensitive).
    # Uses a pattern of "format_name version" since that is most common in NARA.
    # If the format name and version are combined in another way, this will not match it.
    df_to_match = pd.merge(df_unmatched, df_nara[nara_columns], left_on="name_version", right_on="format_lower",
                           how="left")
    df_unmatched = df_to_match[df_to_match["NARA_Risk Level"].isnull()].copy()
    df_unmatched.drop(nara_columns, inplace=True, axis=1)
    df_format = df_to_match[df_to_match["NARA_Risk Level"].notnull()].copy()
    df_format = df_format.assign(NARA_Match_Type="Format Name")

    # Technique 3: Extension is a match (case insensitive).
    # Makes an expanded version of the NARA dataframe for one row per possible extension per format.
    # NARA has pipe separated string of extensions if a format has more than one.
    df_nara_expanded = df_nara[nara_columns].copy()
    df_nara_expanded["ext_separate"] = df_nara_expanded["exts_lower"].str.split(r"|")
    df_nara_expanded = df_nara_expanded.explode("ext_separate")
    df_to_match = pd.merge(df_unmatched, df_nara_expanded, left_on="ext_lower", right_on="ext_separate", how="left")
    df_to_match.drop("ext_separate", inplace=True, axis=1)
    df_unmatched = df_to_match[df_to_match["NARA_Risk Level"].isnull()].copy()
    df_unmatched.drop(nara_columns, inplace=True, axis=1)
    df_ext = df_to_match[df_to_match["NARA_Risk Level"].notnull()].copy()
    df_ext = df_ext.assign(NARA_Match_Type="File Extension")

    # Adds default text for risk and match type for any that are still unmatched.
    df_unmatched["NARA_Risk Level"] = "No Match"
    df_unmatched["NARA_Match_Type"] = "No NARA Match"

    # Combines the dataframes with different matches to save to spreadsheet.
    df_matched = pd.concat([df_puid, df_format, df_ext, df_unmatched])

    # Removes columns that are just used for FITS and NARA comparisons from all dataframes.
    df_matched.drop(["name_version", "name_lower", "format_lower", "ext_lower", "exts_lower"], inplace=True, axis=1)

    # Resets the index back to a single sequential number so that row indexes are unique.
    df_matched.index = np.arange(len(df_matched))

    return df_matched


def match_technical_appraisal(df_results, df_ita):
    """Adds technical appraisal to the results dataframe, which will already have FITS and NARA information.
    Technical appraisal candidates include formats specified in the ITA spreadsheet and files in trash folders.
    Returns an updated results dataframe."""

    # Makes a list of FITS formats that are typically deleted during technical appraisal.
    ta_list = df_ita["FITS_FORMAT"].tolist()

    # Makes a column Technical_Appraisal and puts the value "Format" in any row with a FITS_Format_Name
    # that matches any formats in the ta_list. The match is case insensitive and will match partial strings.
    # re.escape prevents errors from characters in the format name that have regex meanings.
    df_results.loc[df_results["FITS_Format_Name"].str.contains("|".join(map(re.escape, ta_list)), case=False),
                   "Technical_Appraisal"] = "Format"

    # Puts the value "Trash" in any row with a complete folder name of Trash, trash, Trashes, or trashes
    # in the FITS file path. Including the \ before and after the search term ensures it matches a complete name.
    # If the row already has "Format", it will be replaced with "Trash".
    df_results.loc[df_results["FITS_File_Path"].str.contains("\\\\trash\\\\|\\\\trashes\\\\", case=False),
                   "Technical_Appraisal"] = "Trash"

    # Puts a default value in any row that is blank because it didn't match either type of technical appraisal.
    df_results["Technical_Appraisal"] = df_results["Technical_Appraisal"].fillna(value="Not for TA")

    return df_results


def match_other_risk(df_results, df_other):
    """Adds other risks to the results dataframe, which will already have FITS, NARA, and technical
    appraisal information. Other risk candidates include formats specified in the risk spreadsheet
    and formats with NARA low risk but a preservation plan to transform. Returns an updated results dataframe."""

    # Makes a column Other_Risk and puts the value "NARA Low/Transform" in any row with a NARA risk level of low
    # and a NARA proposed preservation plan that starts with the word Transform.
    df_results.loc[(df_results["NARA_Risk Level"] == "Low Risk") &
                   (df_results["NARA_Proposed Preservation Plan"].str.startswith("Transform")),
                   "Other_Risk"] = "NARA Low/Transform"

    # Makes a list of FITS formats that typically indicate a risk.
    risk_list = df_other["FITS_FORMAT"].tolist()

    # Gets a list of the row index for any row where the FITS_Format_Name matches a format on the risk list.
    # The match is case insensitive and will match partial strings.
    # re.escape prevents errors from characters in the format name that have regex meanings.
    indexes = df_results.loc[df_results["FITS_Format_Name"].str.contains("|".join(map(re.escape, risk_list)),
                                                                         case=False)].index

    # For each index in the list, gets the FITS format name for that row and looks it up in the risk spreadsheet.
    # The match to the risk spreadsheet is case insensitive by converting values to lower case.
    # Puts the risk criteria from the risk spreadsheet in the Other_Risk column.
    # If the row already has "NARA Low/Transform", it will be replaced with the criteria.
    for index in indexes:
        format_name = df_results.loc[index, "FITS_Format_Name"].lower()
        risk_criteria = df_other[df_other["FITS_FORMAT"].str.lower() == format_name]["RISK_CRITERIA"].values[0]
        df_results.loc[index, "Other_Risk"] = risk_criteria

    # Puts a default value in any row that is blank because it didn't match either type of other risk.
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

    # Adds default text if there were no files of this type and the dataframe is empty.
    # This shows it wasn't an error and prevents an error from trying to save an empty dataframe to Excel.
    if len(df_subtotals) == 0:
        df_subtotals.loc[len(df_subtotals)] = ["No data of this type", np.NaN, np.NaN, np.NaN]

    return df_subtotals


def media_subtotal(df, accession_folder):
    """"Summarizes by media folder (the top level folder inside the accession folder).
    For each folder, includes the number of files, size in MB, and number of files in each risk category.
    Returns a dataframe."""

    # Calculates the media folder names.
    # If a file is not in a folder, it will have a value of NaN and be skipped when groups are calculated.
    df["Media"] = df["FITS_File_Path"].str.extract(fr'{re.escape(accession_folder)}\\(.*?)\\')

    # Calculates the total files and MB in each media folder.
    # Size is converted to MB.
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
