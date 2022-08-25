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
fits_output = f"{collection_folder}/{accession_number}_FITS"
if os.path.exists(fits_output):
    print("\nUpdating the report using existing FITS format identification information.")
    update_fits(accession_folder, fits_output, collection_folder, accession_number)
else:
    print("\nGenerating new FITS format identification information.")
    os.mkdir(fits_output)
    subprocess.run(f'"{c.FITS}" -r -i "{accession_folder}" -o "{fits_output}"', shell=True)

# Combines the FITS data into a CSV. If one is already present, will replace it.
make_fits_csv(fits_output, accession_folder, collection_folder, accession_number)

# Read the CSVs with data [FITS, ITA (technical appraisal), other formats that can indicate risk, and NARA]
# into pandas for analysis and summarizing, and prints a warning if encoding errors have to be ignored.
df_fits = csv_to_dataframe(f"{collection_folder}/{accession_number}_fits.csv")
df_ita = csv_to_dataframe(c.ITA)
df_other = csv_to_dataframe(c.RISK)
df_nara = csv_to_dataframe(c.NARA)

# If there is already a spreadsheet with combined FITs and risk information from a previous iteration of the script,
# reads that into a dataframe for additional analysis. This lets the archivist manually adjust the risk matches.
# Otherwise, combines FITS, NARA, technical appraisal, and other risk data to a dataframe and saves it as a CSV.
csv_path = os.path.join(collection_folder, f"{accession_number}_full_risk_data.csv")
if os.path.exists(csv_path):
    print("\nUpdating the report using existing risk data.")
    df_results = csv_to_dataframe(csv_path)
else:
    print("\nGenerating new risk data for the report.")
    df_results = match_nara_risk(df_fits, df_nara)
    df_results = match_technical_appraisal(df_results, df_ita)
    df_results = match_other_risk(df_results, df_other)
    df_results.to_csv(csv_path, index=False)

# Removes duplicates in df_results from multiple NARA matches with the same risk and proposed preservation plan.
# This information is saved in the accession's full risk data CSV if matches need to be checked.
df_results.drop(["NARA_Format Name", "NARA_File Extension(s)", "NARA_PRONOM URL"], inplace=True, axis=1)
df_results.drop_duplicates(inplace=True)

# The next several code blocks make different subsets of the data based on different risk factors
# and removes any columns not typically needed for review.

df_nara_risk = df_results[df_results["NARA_Risk Level"] != "Low Risk"].copy()
df_nara_risk.drop(["FITS_Format_Name", "FITS_Format_Version", "FITS_PUID", "FITS_Identifying_Tool(s)",
                   "FITS_Creating_Application", "FITS_Valid", "FITS_Well-Formed", "FITS_Status_Message"],
                  inplace=True, axis=1)

df_multiple = df_results[df_results.duplicated("FITS_File_Path", keep=False) == True].copy()
df_multiple.drop(["FITS_Valid", "FITS_Well-Formed", "FITS_Status_Message"], inplace=True, axis=1)

df_validation = df_results[(df_results["FITS_Valid"] == False) | (df_results["FITS_Well-Formed"] == False) |
                           (df_results["FITS_Status_Message"].notnull())].copy()

df_tech_appraisal = df_results[df_results["Technical_Appraisal"] != "Not for TA"].copy()
df_tech_appraisal.drop(["FITS_PUID", "FITS_Date_Last_Modified", "FITS_MD5", "FITS_Valid", "FITS_Well-Formed",
                        "FITS_Status_Message"], inplace=True, axis=1)

df_other_risk = df_results[df_results["Other_Risk"] != "Not for Other"].copy()
df_other_risk.drop(["FITS_PUID", "FITS_Date_Last_Modified", "FITS_MD5", "FITS_Creating_Application", "FITS_Valid",
                    "FITS_Well-Formed", "FITS_Status_Message"], inplace=True, axis=1)

df_duplicates = df_results[["FITS_File_Path", "FITS_Size_KB", "FITS_MD5"]].copy()
df_duplicates = df_duplicates.drop_duplicates(subset=["FITS_File_Path"], keep=False)
df_duplicates = df_duplicates.loc[df_duplicates.duplicated(subset="FITS_MD5", keep=False)]

# Calculates the total files and total size in the dataframe to use for percentages with the subtotals.
totals_dict = {"Files": len(df_results.index), "MB": df_results["FITS_Size_KB"].sum()/1000}

# Calculates file and size subtotals based on different criteria.
df_format_subtotals = subtotal(df_results, ["FITS_Format_Name", "NARA_Risk Level"], totals_dict)
df_nara_risk_subtotals = subtotal(df_results, ["NARA_Risk Level"], totals_dict)
df_tech_appraisal_subtotals = subtotal(df_tech_appraisal, ["Technical_Appraisal", "FITS_Format_Name"], totals_dict)
df_other_risk_subtotals = subtotal(df_other_risk, ["Other_Risk", "FITS_Format_Name"], totals_dict)
df_media_subtotals = media_subtotal(df_results, accession_folder)

# Saves all dataframes to a separate tab in an Excel spreadsheet in the collection folder.
# The index is not included if it is the row numbers.
with pd.ExcelWriter(f"{collection_folder}/{accession_number}_format-analysis.xlsx") as result:
    df_format_subtotals.to_excel(result, sheet_name="Format Subtotals")
    df_nara_risk_subtotals.to_excel(result, sheet_name="NARA Risk Subtotals")
    df_tech_appraisal_subtotals.to_excel(result, sheet_name="Tech Appraisal Subtotals")
    df_other_risk_subtotals.to_excel(result, sheet_name="Other Risk Subtotals")
    df_media_subtotals.to_excel(result, sheet_name="Media Subtotals", index_label="Media")
    df_nara_risk.to_excel(result, sheet_name="NARA Risk", index=False)
    df_tech_appraisal.to_excel(result, sheet_name="For Technical Appraisal", index=False)
    df_other_risk.to_excel(result, sheet_name="Other Risks", index=False)
    df_multiple.to_excel(result, sheet_name="Multiple Formats", index=False)
    df_duplicates.to_excel(result, sheet_name="Duplicates", index=False)
    df_validation.to_excel(result, sheet_name="Validation", index=False)
