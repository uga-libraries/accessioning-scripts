"""
Purpose: generate format identification and create reports to support:
    1. Appraisal (technical and content based)
    2. Assigning processing tiers
    3. Identify risks to address immediately.

Produces a spreadsheet with risk information based on NARA preservation action plans and a local list of formats that
typically indicate removal during technical appraisal, with several tabs that summarize this information in different
ways.

Script usage: python path/format_analysis.py accession_folder
The accession_folder is the path to the folder with files to be analyzed.
Script output is saved in the parent folder of the accession folder.
"""

from format_analysis_functions import *

# Configuration is made by the user on each new machine the script is installed on, so it could be missing.
try:
    import configuration as c
except ModuleNotFoundError:
    print("\nCould not run the script. Missing the required configuration.py file.")
    print("Make a configuration.py file using configuration_template.py and save it to the folder with the script.")
    sys.exit()

# Gets the accession folder path from the script argument and verifies it is correct.
# If there is an error, ends the script.
try:
    accession_folder = sys.argv[1]
except IndexError:
    print("\nThe required script argument (accession_folder) is missing.")
    print("Please run the script again.")
    print("Script usage: python path/format_analysis.py path/accession_folder")
    sys.exit()

if not os.path.exists(accession_folder):
    print(f"\nThe provided accession folder '{accession_folder}' is not a valid directory.")
    print("Please run the script again.")
    print("Script usage: python path/format_analysis.py path/accession_folder")
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
# These are only for naming file outputs, so it will not cause an error if they aren't named as expected.
collection_folder, accession_number = os.path.split(accession_folder)

# If there is already a folder with FITS format identification information in the collection folder,
# updates the folder to match the contents of the accession folder.
# Otherwise, runs FITS to generate the format identification information.
# Prints to the terminal which mode the script is using so the archivist can stop the script if there is an error.
fits_output = f"{collection_folder}/{accession_number}_FITS"
if os.path.exists(fits_output):
    print("\nUpdating the report using existing FITS format identification information.")
    update_fits(accession_folder, fits_output, collection_folder, accession_number)
else:
    print("\nGenerating new FITS format identification information.")
    os.mkdir(fits_output)
    subprocess.run(f'"{c.FITS}" -r -i "{accession_folder}" -o "{fits_output}"', shell=True)

# Makes a CSV in the collection folder, with a header row, for combined FITS information.
header = ["File_Path", "Format_Name", "Format_Version", "PUID", "Identifying_Tool(s)", "Multiple_IDs",
          "Date_Last_Modified", "Size_KB", "MD5", "Creating_Application",
          "Valid", "Well-Formed", "Status_Message"]
csv_open = open(f"{collection_folder}/{accession_number}_fits.csv", "w", newline="")
csv_write = csv.writer(csv_open)
csv_write.writerow(header)
csv_open.close()

# Extracts select format information for each file, with some data reformatting, and saves to the FITS CSV.
for fits_xml in os.listdir(fits_output):
    fits_to_csv(f"{accession_folder}_FITS/{fits_xml}", collection_folder, accession_number)

# If an encode errors text file was made during the previous step, removes any duplicate files.
# Files are duplicated in encode_errors.txt if they have more than one format identification.
if os.path.exists(f"{collection_folder}/{accession_number}_encode_errors.txt"):
    error_df = pd.read_csv(f"{collection_folder}/{accession_number}_encode_errors.txt", header=None)
    error_df.drop_duplicates(inplace=True)
    error_df.to_csv(f"{collection_folder}/{accession_number}_encode_errors.txt", header=False, index=False)

# Read the CSVs with data [FITS, ITA (technical appraisal), other formats that can indicate risk, and NARA]
# into pandas for analysis and summarizing, and prints a warning if encoding errors have to be ignored.
df_fits = csv_to_dataframe(f"{collection_folder}/{accession_number}_fits.csv")
df_ita = csv_to_dataframe(c.ITA)
df_risk = csv_to_dataframe(c.RISK)
df_nara = csv_to_dataframe(c.NARA)

# Adds a prefix to the FITS and NARA dataframes so the source of the data is clear when the data is combined.
df_fits = df_fits.add_prefix("FITS_")
df_nara = df_nara.add_prefix("NARA_")

# If there is already a spreadsheet with combined FITs and risk information from a previous iteration of the script,
# reads that into a dataframe for additional analysis. This lets the archivist manually adjust the risk matches.
# Otherwise, combines FITS, NARA, technical appraisal, and other risk data to a dataframe.
csv_path = os.path.join(collection_folder, f"{accession_number}_full_risk_data.csv")
if os.path.exists(csv_path):
    print("\nUpdating the report using existing risk data.")
    df_results = csv_to_dataframe(csv_path)
else:
    print("\nGenerating new risk data for the report.")
    # Adds risk information from NARA using different techniques, starting with the most accurate.
    # A new column Match_Type is added to identify which technique produced a match.
    df_results = match_nara_risk(df_fits, df_nara)

    # Adds technical appraisal information.
    # Creates a column to indicate the appraisal category: in a trash folder or matches a format in ITAfileformats.csv.
    # Matches are case insensitive and will match partial strings.
    # If a format matches both categories, it will be put in the trash category.
    # re.escape is used to escape any unusual characters in the filename that have regex meanings.
    # Trash matches include the "\" on either side to match entire folder names.
    ta_list = df_ita["FITS_FORMAT"].tolist()
    df_results.loc[df_results["FITS_Format_Name"].str.contains("|".join(map(re.escape, ta_list)), case=False),
                   "Technical_Appraisal"] = "Format"
    df_results.loc[df_results["FITS_File_Path"].str.contains("\\\\trash\\\\|\\\\trashes\\\\", case=False),
                   "Technical_Appraisal"] = "Trash"
    df_results["Technical_Appraisal"] = df_results["Technical_Appraisal"].fillna(value="Not for TA")

    # Adds other risk information.
    # Creates a column to indicate the risk category: NARA low risk/transform or the format risk criteria.
    # Matches are case insensitive and will match partial strings.
    # If a format matches NARA and a format risk criteria, it will be put in the risk criteria category.
    df_results.loc[(df_results["NARA_Risk Level"] == "Low Risk") & (df_results["NARA_Proposed Preservation Plan"].str.startswith("Transform")),
                   "Other_Risk"] = "NARA Low/Transform"
    risk_list = df_risk["FITS_FORMAT"].tolist()
    indexes = df_results.loc[df_results["FITS_Format_Name"].str.contains("|".join(map(re.escape, risk_list)), case=False)].index
    for index in indexes:
        format_name = df_results.loc[index, "FITS_Format_Name"].lower()
        risk_criteria = df_risk[df_risk["FITS_FORMAT"].str.lower() == format_name]["RISK_CRITERIA"].values[0]
        df_results.loc[index, "Other_Risk"] = risk_criteria
    df_results["Other_Risk"] = df_results["Other_Risk"].fillna(value="Not for Other")

    # Saves the information in df_results to a CSV for archivist review.
    df_results.to_csv(csv_path, index_label="Index")

# Removes duplicates in df_results from multiple NARA matches with the same risk and proposed preservation plan.
# This information is saved in the accession's full risk data CSV if matches need to be checked.
df_results.drop(["Index", "NARA_Format Name", "NARA_File Extension(s)", "NARA_PRONOM URL"], inplace=True, axis=1)
df_results.drop_duplicates(inplace=True)

# The next several code blocks make different subsets of the data based on different risk factors
# and removes any columns not typically needed for review.

nara_at_risk = df_results[df_results["NARA_Risk Level"] != "Low Risk"].copy()
nara_at_risk.drop(["FITS_Format_Name", "FITS_Format_Version", "FITS_PUID", "FITS_Identifying_Tool(s)",
                   "FITS_Creating_Application", "FITS_Valid", "FITS_Well-Formed", "FITS_Status_Message"],
                  inplace=True, axis=1)

multiple_ids = df_results[df_results.duplicated("FITS_File_Path", keep=False) == True].copy()
multiple_ids.drop(["FITS_Valid", "FITS_Well-Formed", "FITS_Status_Message"], inplace=True, axis=1)

validation_error = df_results[(df_results["FITS_Valid"] == False) | (df_results["FITS_Well-Formed"] == False) |
                              (df_results["FITS_Status_Message"].notnull())].copy()

tech_appraisal = df_results[df_results["Technical_Appraisal"] != "Not for TA"].copy()
tech_appraisal.drop(["FITS_PUID", "FITS_Date_Last_Modified", "FITS_MD5", "FITS_Valid", "FITS_Well-Formed",
                     "FITS_Status_Message"], inplace=True, axis=1)

other_risk = df_results[df_results["Other_Risk"] != "Not for Other"].copy()
other_risk.drop(["FITS_PUID", "FITS_Date_Last_Modified", "FITS_MD5", "FITS_Creating_Application", "FITS_Valid",
                 "FITS_Well-Formed", "FITS_Status_Message"], inplace=True, axis=1)

df_duplicates = df_results[["FITS_File_Path", "FITS_Size_KB", "FITS_MD5"]].copy()
df_duplicates = df_duplicates.drop_duplicates(subset=["FITS_File_Path"], keep=False)
df_duplicates = df_duplicates.loc[df_duplicates.duplicated(subset="FITS_MD5", keep=False)]

# Calculates the total files and total size in the dataframe to use for percentages with the subtotals.
totals_dict = {"Files": len(df_results.index), "MB": df_results["FITS_Size_KB"].sum()/1000}

# Calculates file and size subtotals based on different criteria.
format_subtotals = subtotal(df_results, ["FITS_Format_Name", "NARA_Risk Level"], totals_dict)
nara_risk_subtotals = subtotal(df_results, ["NARA_Risk Level"], totals_dict)
technical_appraisal_subtotals = subtotal(df_results, ["Technical_Appraisal", "FITS_Format_Name"], totals_dict)
other_risk_subtotals = subtotal(df_results, ["Other_Risk", "FITS_Format_Name"], totals_dict)
media_subtotals = media_subtotal(df_results, accession_folder)

# Saves all dataframes to a separate tab in an Excel spreadsheet in the collection folder.
# The index is not included if it is the row numbers.
with pd.ExcelWriter(f"{collection_folder}/{accession_number}_format-analysis.xlsx") as result:
    format_subtotals.to_excel(result, sheet_name="Format Subtotals")
    nara_risk_subtotals.to_excel(result, sheet_name="NARA Risk Subtotals")
    technical_appraisal_subtotals.to_excel(result, sheet_name="Tech Appraisal Subtotals")
    other_risk_subtotals.to_excel(result, sheet_name="Other Risk Subtotals")
    media_subtotals.to_excel(result, sheet_name="Media Subtotals", index_label="Media")
    nara_at_risk.to_excel(result, sheet_name="NARA Risk", index=False)
    tech_appraisal.to_excel(result, sheet_name="For Technical Appraisal", index=False)
    other_risk.to_excel(result, sheet_name="Other Risks", index=False)
    multiple_ids.to_excel(result, sheet_name="Multiple Formats", index=False)
    df_duplicates.to_excel(result, sheet_name="Duplicates", index=False)
    validation_error.to_excel(result, sheet_name="Validation", index=False)
