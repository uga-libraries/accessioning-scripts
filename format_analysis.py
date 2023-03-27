"""
Purpose: generate format identification and create reports to support:
    1. Appraisal (technical and content based)
    2. Assigning processing tiers
    3. Identify risks to address immediately.

Produces a spreadsheet with risk information based on NARA preservation action plans and a local list of formats that
typically indicate removal during technical appraisal or other risks, with several tabs that summarize this information
in different ways.

Script usage: python path/format_analysis.py path/accession_folder
The accession_folder is the path to the folder with files to be analyzed.
Script output is saved in the parent folder of the accession folder.
"""

from format_analysis_functions import *

# Configuration.py is made by the archivist on each new machine the script is installed on, so it could be missing.
try:
    import configuration as c
except ModuleNotFoundError:
    print("\nCould not run the script. Missing the required configuration.py file.")
    print("Make a configuration.py file using configuration_template.py and save it to the folder with the script.")
    sys.exit()

# Gets the accession folder path from the script argument and verifies it is correct.
# If there is an error, ends the script.
accession_folder = argument(sys.argv)
if accession_folder is False:
    sys.exit()

# Verifies the configuration file has all of the required variables and the file paths are valid.
# If there are any errors, ends the script.
configuration_errors = check_configuration()
if len(configuration_errors) > 0:
    print('\nProblems detected with configuration.py:')
    for error in configuration_errors:
        print("   *", error)
    print('\nCorrect the configuration file, using configuration_template.py as a model.')
    sys.exit()

# Calculates the accession number, which is the name of the last folder in the accession_folder path,
# and the collection folder, which is everything in the accession_folder path except the accession folder.
# These are used for naming script outputs, so it will not cause an error if they don't match id naming conventions.
collection_folder, accession_number = os.path.split(accession_folder)

# If there is already a FITS XML folder, updates the FITS folder to match the contents of the accession folder.
# Otherwise, runs FITS to generate the FITS XML.
fits_output = f"{collection_folder}/{accession_number}_FITS"
if os.path.exists(fits_output):
    print("\nUpdating the XML files in the FITS folder to match the files in the accession folder.")
    print("This will update fits.csv but will NOT update full_risk_data.csv from a previous script iteration.")
    print("Delete full_risk_data.csv before the script gets to that step for it to be remade with the new information.")
    update_fits(accession_folder, fits_output, collection_folder, accession_number)
else:
    print("\nGenerating new FITS format identification information.")
    os.mkdir(fits_output)
    fits_status = subprocess.run(f'"{c.FITS}" -r -i "{accession_folder}" -o "{fits_output}"',
                                 shell=True, stderr=subprocess.PIPE)
    if fits_status.stderr == b'Error: Could not find or load main class edu.harvard.hul.ois.fits.Fits\r\n':
        print("Unable to generate FITS XML.")
        print("The FITS folder and accession folder need to be on the same letter drive.")
        sys.exit()

# Combines the FITS data into a CSV. If one is already present, this will replace it.
make_fits_csv(fits_output, collection_folder, accession_number)

# Read the CSVs with data (FITS, ITA (technical appraisal), other formats that can indicate risk, and NARA)
# into pandas for analysis and summarizing, and prints a warning if encoding errors have to be ignored.
df_fits = csv_to_dataframe(f"{collection_folder}/{accession_number}_fits.csv")
df_fits['FITS_Size_KB'] = df_fits['FITS_Size_KB'].astype(float)
df_ita = csv_to_dataframe(c.ITA)
df_other = csv_to_dataframe(c.RISK)
df_nara = csv_to_dataframe(c.NARA)

# If there is already a spreadsheet with combined FITs and risk information from a previous iteration of the script,
# reads that into a dataframe for additional analysis. This lets the archivist manually adjust the risk matches.
# Otherwise, combines FITS, NARA, technical appraisal, and other risk data into a dataframe and saves it as a CSV.
csv_path = os.path.join(collection_folder, f"{accession_number}_full_risk_data.csv")
if os.path.exists(csv_path):
    print("\nUpdating the analysis report using existing risk data.")
    df_results = csv_to_dataframe(csv_path)
    df_results['FITS_Size_KB'] = df_results['FITS_Size_KB'].astype(float)
else:
    print("\nGenerating new risk data for the analysis report.")
    df_results = match_nara_risk(df_fits, df_nara)
    df_results = match_technical_appraisal(df_results, df_ita)
    df_results = match_other_risk(df_results, df_other)
    df_results.to_csv(csv_path, index=False)

# Removes duplicates in df_results from multiple NARA matches (same risk and preservation plan) to a single file.
# The full data with the duplicates is saved in the accession's full risk data CSV if matches need to be checked.
df_results.drop(["NARA_Format Name", "NARA_File Extension(s)", "NARA_PRONOM URL"], inplace=True, axis=1)
df_results.drop_duplicates(inplace=True)

# The next several code blocks make different subsets of the data based on different risk factors
# and removes any columns not typically needed for review. If the subset is empty (no risk of that type),
# the dataframe is given the default value of 'No data of this type'.

# Subset: NARA risk. Any format that is not Low Risk.
df_nara_risk = df_results[df_results["NARA_Risk Level"] != "Low Risk"].copy()
df_nara_risk.drop(["FITS_PUID", "FITS_Identifying_Tool(s)", "FITS_Creating_Application",
                   "FITS_Valid", "FITS_Well-Formed", "FITS_Status_Message"], inplace=True, axis=1)
if len(df_nara_risk) == 0:
    df_nara_risk = pd.DataFrame([['No data of this type']])

# Subset: multiple FITS format identifications for the same file.
# The format name, version, and PUID need to be the same to be considered the same identification.
# Makes a subset with duplicate file paths (so files in multiple places aren't counted),
# removes NARA columns (so duplicates from different NARA identifications aren't counted),
# and drops duplicate rows.
df_multiple = df_results[df_results.duplicated('FITS_File_Path', keep=False) == True].copy()
df_multiple.drop(['FITS_Valid', 'FITS_Well-Formed', 'FITS_Status_Message', 'NARA_Risk Level',
                  'NARA_Proposed Preservation Plan', 'NARA_Match_Type'], inplace=True, axis=1)
df_multiple.drop_duplicates(inplace=True)
if len(df_multiple) == 0:
    df_multiple = pd.DataFrame([['No data of this type']])

# Subset: formats that are not valid.
# FITS could have False in the Valid and/or Well-Formed fields and/or text in the Status Message.
df_validation = df_results[(df_results["FITS_Valid"] == False) |
                           (df_results["FITS_Well-Formed"] == False) |
                           (df_results["FITS_Status_Message"].notnull())].copy()
if len(df_validation) == 0:
    df_validation = pd.DataFrame([['No data of this type']])

# Subset: technical appraisal. Any format that is not 'Not for TA'.
df_tech_appraisal = df_results[df_results["Technical_Appraisal"] != "Not for TA"].copy()
df_tech_appraisal.drop(["FITS_PUID", "FITS_Date_Last_Modified", "FITS_MD5", "FITS_Valid", "FITS_Well-Formed",
                        "FITS_Status_Message"], inplace=True, axis=1)
if len(df_tech_appraisal) == 0:
    df_tech_appraisal = pd.DataFrame([['No data of this type']])

# Subset: other risk. Any format that is not 'Not for Other'.
df_other_risk = df_results[df_results["Other_Risk"] != "Not for Other"].copy()
df_other_risk.drop(["FITS_PUID", "FITS_Date_Last_Modified", "FITS_MD5", "FITS_Creating_Application",
                    "FITS_Valid", "FITS_Well-Formed", "FITS_Status_Message"], inplace=True, axis=1)
if len(df_other_risk) == 0:
    df_other_risk = pd.DataFrame([['No data of this type']])

# Subset: duplicate files. Any file that is in the directory in more than one location.
# It does not include files repeated in the dataframe because of multiple FITS identifications or
# multiple possible NARA matches by removing duplicates from the file path first
# and only including any files with the same fixity and a different file path.
df_duplicates = df_results[["FITS_File_Path", "FITS_Size_KB", "FITS_MD5"]].copy()
df_duplicates = df_duplicates.drop_duplicates(subset=["FITS_File_Path"], keep=False)
df_duplicates = df_duplicates.loc[df_duplicates.duplicated(subset="FITS_MD5", keep=False)]
if len(df_duplicates) == 0:
    df_duplicates = pd.DataFrame([['No data of this type']])

# Calculates the number of files and total size in the dataframe to use for calculating percentages with the subtotals.
# This gives percentages based on the entire accession and not just the files that are in a particular subtotal.
totals_dict = {"Files": len(df_results.index), "MB": df_results["FITS_Size_KB"].sum()/1000}

# Calculates file and size subtotals based on different criteria.
# The input df for tech appraisal and other risk are filtered to exclude files which don't have that risk.
df_format_subtotals = subtotal(df_results, ["FITS_Format_Name", "NARA_Risk Level"], totals_dict)
df_nara_risk_subtotals = subtotal(df_results, ["NARA_Risk Level"], totals_dict)
df_tech_appraisal_subtotals = subtotal(df_results[df_results["Technical_Appraisal"] != "Not for TA"],
                                       ["Technical_Appraisal", "FITS_Format_Name"], totals_dict)
df_other_risk_subtotals = subtotal(df_results[df_results["Other_Risk"] != "Not for Other"],
                                   ["Other_Risk", "FITS_Format_Name"], totals_dict)
df_media_subtotals = media_subtotal(df_results, accession_folder)

# Saves all dataframes to a separate tab in an Excel spreadsheet in the collection folder.
# The index is not included if it is the row numbers.
with pd.ExcelWriter(f"{collection_folder}/{accession_number}_format-analysis.xlsx") as result:
    df_format_subtotals.to_excel(result, sheet_name="Format Subtotal")
    df_nara_risk_subtotals.to_excel(result, sheet_name="NARA Risk Subtotal")
    df_tech_appraisal_subtotals.to_excel(result, sheet_name="Tech Appraisal Subtotal")
    df_other_risk_subtotals.to_excel(result, sheet_name="Other Risk Subtotal")
    df_media_subtotals.to_excel(result, sheet_name="Media Subtotal", index_label="Media")
    df_nara_risk.to_excel(result, sheet_name="NARA Risk", index=False)
    df_tech_appraisal.to_excel(result, sheet_name="For Technical Appraisal", index=False)
    df_other_risk.to_excel(result, sheet_name="Other Risks", index=False)
    df_multiple.to_excel(result, sheet_name="Multiple Formats", index=False)
    df_duplicates.to_excel(result, sheet_name="Duplicates", index=False)
    df_validation.to_excel(result, sheet_name="Validation", index=False)
