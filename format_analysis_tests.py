"""Purpose: tests for each function and analysis component (each subset and subtotal) in the format_analysis.py script.
Each test creates simplified input, runs the code, and compares it to the expected output.
Test results are saved to a directory specified with the script argument.
Comment out any test you do not wish to run.

For any tests that do not import the function from format_analysis.py, sync the code before running the test.
If the input for any function or analysis changes, edit the test input and expected results."""

# usage: python path/format_analysis_tests.py output_folder

from format_analysis_functions import *


def compare_dataframes(test_name, df_actual, df_expected):
    """Compares two dataframes, one with the actual script output and one with the expected values.
    Prints if they match (test passes) or not (test fails) and saves failed tests to a CSV for review."""

    # Makes a new dataframe that merges the values of the two dataframes.
    df_comparison = df_actual.merge(df_expected, indicator=True, how="outer")

    # Makes a dataframe with just the errors (merge value isn't both).
    df_errors = df_comparison[df_comparison["_merge"] != "both"]

    # If the merged dataframe is empty (everything matched), prints that the test passes.
    # Otherwise, saves the dataframe with the complete merge (including matches) to a CSV in the output directory.
    if len(df_errors) == 0:
        print("Test passes: ", test_name)
    else:
        print("Test fails:  ", test_name)
        df_comparison.to_csv(f"{test_name}_comparison_results.csv", index=False)


def test_argument_tbd():
    """Tests error handling for a missing or incorrect script argument."""


def test_check_configuration_function_tbd():
    """Tests error handling from missing configuration file, missing variables and variables with invalid paths."""


def test_csv_to_dataframe_function_tbd():
    """Tests error handling for encoding errors and adding prefixes to FITS and NARA dataframes."""


def test_update_fits_function_tbd():
    """Tests removing FITS for deleted files and adding FITs for new files."""


def test_fits_row_function_tbd():
    """Tests all variations for FITS data extraction and reformatting."""


def test_make_fits_csv_function_tbd():
    """Tests encoding error handling and saving files with one and multiple FITS format ids to the CSV."""


def test_match_nara_risk_function():
    """Tests combining NARA risk information with FITS information to produce df_results."""

    # Makes a dataframe to use for FITS information.
    # PUID variations: match 1 PUID and multiple PUIDs
    # Name variations: match with version or name only, including case not matching
    # Extension variations: match single extension and pipe-separated extension, including case not matching
    # Also includes 2 that won't match
    rows = [[r"C:\PUID\file.zip", "ZIP archive", np.NaN, "https://www.nationalarchives.gov.uk/pronom/x-fmt/263"],
            [r"C:\PUID\Double\movie.ifo", "DVD Data File", np.NaN, "https://www.nationalarchives.gov.uk/pronom/x-fmt/419"],
            [r"C:\Name\img.jp2", "JPEG 2000 File Format", np.NaN, np.NaN],
            [r"C:\Name\Case\file.gz", "gzip", np.NaN, np.NaN],
            [r"C:\Name\Version\database.nsf", "Lotus Notes Database", "2", np.NaN],
            [r"C:\Ext\Both\file.dat", "File Data", np.NaN, np.NaN],
            [r"C:\Ext\Case\file.BIN", "Unknown Binary", np.NaN, np.NaN],
            [r"C:\Ext\Multi\img.jpg", "JPEG", "1", np.NaN],
            [r"C:\Unmatched\file.new", "Brand New Format", np.NaN, np.NaN],
            [r"C:\Unmatched\file.none", "empty", np.NaN, np.NaN]]
    column_names = ["FITS_File_Path", "FITS_Format_Name", "FITS_Format_Version", "FITS_PUID"]
    df_fits = pd.DataFrame(rows, columns=column_names)

    # Reads the NARA risk CSV into a dataframe.
    # In format_analysis.py, this is done in the main body of the script before the function is called.
    df_nara = csv_to_dataframe(c.NARA)

    # Runs the function being tested.
    df_results = match_nara_risk(df_fits, df_nara)

    # Makes a dataframe with the expected values.
    rows = [[r"C:\PUID\file.zip", "ZIP archive", np.NaN, "https://www.nationalarchives.gov.uk/pronom/x-fmt/263",
             "ZIP archive", "zip", "https://www.nationalarchives.gov.uk/pronom/x-fmt/263", "Moderate Risk",
             "Retain but extract files from the container", "PRONOM"],
            [r"C:\PUID\Double\movie.ifo", "DVD Data File", np.NaN,
             "https://www.nationalarchives.gov.uk/pronom/x-fmt/419", "DVD Data Backup File", "bup",
             "https://www.nationalarchives.gov.uk/pronom/x-fmt/419", "Moderate Risk", "Retain", "PRONOM"],
            [r"C:\PUID\Double\movie.ifo", "DVD Data File", np.NaN,
             "https://www.nationalarchives.gov.uk/pronom/x-fmt/419", "DVD Data File", "dvd",
             "https://www.nationalarchives.gov.uk/pronom/x-fmt/419", "Moderate Risk", "Retain", "PRONOM"],
            [r"C:\PUID\Double\movie.ifo", "DVD Data File", np.NaN,
             "https://www.nationalarchives.gov.uk/pronom/x-fmt/419", "DVD Info File", "ifo",
             "https://www.nationalarchives.gov.uk/pronom/x-fmt/419", "Moderate Risk", "Retain", "PRONOM"],
            [r"C:\Name\img.jp2", "JPEG 2000 File Format", np.NaN, np.NaN, "JPEG 2000 File Format", "jp2",
             "https://www.nationalarchives.gov.uk/pronom/x-fmt/392", "Low Risk", "Retain", "Format Name"],
            [r"C:\Name\Case\file.gz", "gzip", np.NaN, np.NaN, "GZIP", "gz|tgz",
             "https://www.nationalarchives.gov.uk/pronom/x-fmt/266", "Low Risk",
             "Retain but extract files from the container", "Format Name"],
            [r"C:\Name\Version\database.nsf", "Lotus Notes Database", "2", np.NaN, "Lotus Notes Database 2",
             "nsf|ns2", "https://www.nationalarchives.gov.uk/pronom/x-fmt/336", "Moderate Risk", "Transform to CSV",
             "Format Name"],
            [r"C:\Ext\Both\file.dat", "File Data", np.NaN, np.NaN, "Data File", "dat", np.NaN, "Moderate Risk",
             "Retain", "File Extension"],
            [r"C:\Ext\Both\file.dat", "File Data", np.NaN, np.NaN, "Windows Registry Files", "reg|dat", np.NaN,
             "Moderate Risk", "Retain", "File Extension"],
            [r"C:\Ext\Case\file.BIN", "Unknown Binary", np.NaN, np.NaN, "Binary file", "bin",
             "https://www.nationalarchives.gov.uk/pronom/fmt/208", "High Risk", "Retain", "File Extension"],
            [r"C:\Ext\Multi\img.jpg", "JPEG", "1", np.NaN, "JPEG File Interchange Format 1.00", "jpg|jpeg",
             "https://www.nationalarchives.gov.uk/pronom/fmt/42", "Low Risk", "Retain", "File Extension"],
            [r"C:\Ext\Multi\img.jpg", "JPEG", "1", np.NaN, "JPEG File Interchange Format 1.01", "jpg|jpeg",
             "https://www.nationalarchives.gov.uk/pronom/fmt/43", "Low Risk", "Retain", "File Extension"],
            [r"C:\Ext\Multi\img.jpg", "JPEG", "1", np.NaN, "JPEG File Interchange Format 1.02", "jpg|jpeg",
             "https://www.nationalarchives.gov.uk/pronom/fmt/44", "Low Risk", "Retain", "File Extension"],
            [r"C:\Ext\Multi\img.jpg", "JPEG", "1", np.NaN, "JPEG Raw Stream", "jpg|jpeg",
             "https://www.nationalarchives.gov.uk/pronom/fmt/41", "Low Risk", "Retain", "File Extension"],
            [r"C:\Ext\Multi\img.jpg", "JPEG", "1", np.NaN, "JPEG unspecified version", "jpg|jpeg", np.NaN,
             "Low Risk", "Retain", "File Extension"],
            [r"C:\Unmatched\file.new", "Brand New Format", np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, "No Match",
             np.NaN, "No NARA Match"],
            [r"C:\Unmatched\file.none", "empty", np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, "No Match", np.NaN,
             "No NARA Match"]]
    column_names = ["FITS_File_Path", "FITS_Format_Name", "FITS_Format_Version", "FITS_PUID",
                    "NARA_Format Name", "NARA_File Extension(s)", "NARA_PRONOM URL", "NARA_Risk Level",
                    "NARA_Proposed Preservation Plan", "NARA_Match_Type"]
    df_expected = pd.DataFrame(rows, columns=column_names)

    # Compares the script output to the expected values.
    compare_dataframes("Match_NARA", df_results, df_expected)


def test_match_technical_appraisal_function():
    """Tests adding technical appraisal categories to df_results,
    which will already have information from FITS and NARA.
    In format_analysis.py, this is done in the main body of the script."""

    # Makes a dataframe to use as input.
    # Data variation: examples that match both, one, or neither of the technical appraisal categories,
    # with identical cases and different cases (match is case-insensitive).
    rows = [[r"C:\CD1\Flower.JPG", "JPEG EXIF"],
            [r"C:\CD1\Trashes\Flower1.JPG", "JPEG EXIF"],
            [r"C:\CD2\Script\config.pyc", "unknown binary"],
            [r"C:\CD2\Trash Data\data.zip", "ZIP Format"],
            [r"C:\CD2\trash\New Document.txt", "Plain text"],
            [r"C:\CD2\Trash\New Text.txt", "Plain text"],
            [r"C:\FD1\empty.txt", "empty"],
            [r"C:\FD1\trashes\program.dll", "PE32 executable"]]
    column_names = ["FITS_File_Path", "FITS_Format_Name"]
    df_results = pd.DataFrame(rows, columns=column_names)

    # Reads the technical appraisal CSV into a dataframe.
    # In format_analysis.py, this is done in the main body of the script before the function is called.
    df_ita = csv_to_dataframe(c.ITA)

    # Runs the function being tested.
    df_results = match_technical_appraisal(df_results, df_ita)

    # Makes a dataframe with the expected values.
    rows = [[r"C:\CD1\Flower.JPG", "JPEG EXIF", "Not for TA"],
            [r"C:\CD1\Trashes\Flower1.JPG", "JPEG EXIF", "Trash"],
            [r"C:\CD2\Script\config.pyc", "unknown binary", "Format"],
            [r"C:\CD2\Trash Data\data.zip", "ZIP Format", "Not for TA"],
            [r"C:\CD2\trash\New Document.txt", "Plain text", "Trash"],
            [r"C:\CD2\Trash\New Text.txt", "Plain text", "Trash"],
            [r"C:\FD1\empty.txt", "empty", "Format"],
            [r"C:\FD1\trashes\program.dll", "PE32 executable", "Trash"]]
    column_names = ["FITS_File_Path", "FITS_Format_Name", "Technical Appraisal"]
    df_expected = pd.DataFrame(rows, columns=column_names)

    # Compares the script output to the expected values.
    compare_dataframes("Match_TA", df_results, df_expected)


def test_match_other_risk_function():
    """Tests adding other risk categories to df_results,
    which will already have information from FITS, NARA, and technical appraisal.
    In format_analysis.py, this is done in the main body of the script."""

    # Makes a dataframe to use as input.
    # Data variation: examples that match both, one, or neither of the other risk categories,
    # with identical cases and different cases (match is case-insensitive),
    # and at least one each of the format risk criteria.
    rows = [["Adobe Photoshop file", "Moderate Risk", "Transform to TIFF or JPEG2000"],
            ["Cascading Style Sheet", "Low Risk", "Retain"],
            ["CorelDraw Drawing", "High Risk", "Transform to a TBD format, possibly PDF or TIFF"],
            ["empty", np.NaN, np.NaN],
            ["Encapsulated Postscript File", "Low Risk", "Transform to TIFF or JPEG2000"],
            ["iCalendar", "Low Risk", "Transform to CSV"],
            ["MBOX Email Format", "Low Risk", "Transform to EML but also retain MBOX"],
            ["Plain text", "Low Risk", "Retain"],
            ["zip format", "Low Risk", "Retain"]]
    column_names = ["FITS_Format_Name", "NARA_Risk Level", "NARA_Proposed Preservation Plan"]
    df_results = pd.DataFrame(rows, columns=column_names)

    # Reads the risk file formats CSV into a dataframe.
    # In format_analysis.py, this is done in the main body of the script before the function is called.
    df_other = csv_to_dataframe(c.RISK)

    # Runs the function being tested.
    df_results = match_other_risk(df_results, df_other)

    # Makes a dataframe with the expected values.
    rows = [["Adobe Photoshop file", "Moderate Risk", "Transform to TIFF or JPEG2000", "Layered image file"],
            ["Cascading Style Sheet", "Low Risk", "Retain", "Possible saved web page"],
            ["CorelDraw Drawing", "High Risk", "Transform to a TBD format, possibly PDF or TIFF", "Layered image file"],
            ["empty", np.NaN, np.NaN, "Not for Other"],
            ["Encapsulated Postscript File", "Low Risk", "Transform to TIFF or JPEG2000", "Layered image file"],
            ["iCalendar", "Low Risk", "Transform to CSV", "NARA Low/Transform"],
            ["MBOX Email Format", "Low Risk", "Transform to EML but also retain MBOX", "NARA Low/Transform"],
            ["Plain text", "Low Risk", "Retain", "Not for Other"],
            ["zip format", "Low Risk", "Retain", "Archive format"]]
    column_names = ["FITS_Format_Name", "NARA_Risk Level", "NARA_Proposed Preservation Plan", "Other_Risk"]
    df_expected = pd.DataFrame(rows, columns=column_names)

    # Compares the script output to the expected values.
    compare_dataframes("Match_Other", df_results, df_expected)


def test_media_subtotal_function_tbd():
    """Tests variations in subtotals."""


def test_deduplicate_results_tbd():
    """Tests that duplicates from multiple NARA matches with the same risk information are correctly removed."""

    # Code to test:
    # df_results.drop(["NARA_Format Name", "NARA_File Extension(s)", "NARA_PRONOM URL"], inplace=True, axis=1)
    # df_results.drop_duplicates(inplace=True)


def test_nara_risk_subset():
    """Tests the NARA risk subset, which is based on the NARA_Risk Level column."""

    # Makes a dataframe to use as input.
    # Data variation: all 4 risk levels and all columns to be dropped.
    rows = [[r"C:\Disk1\file.txt", "Plain text", "Low Risk", "drop", "drop", "drop", "drop", "drop", "drop"],
            [r"C:\Disk1\photo.jpg", "JPEG EXIF", "Low Risk", "drop", "drop", "drop", "drop", "drop", "drop"],
            [r"C:\Disk1\file.psd", "Adobe Photoshop file", "Moderate Risk", "drop", "drop", "drop", "drop", "drop", "drop"],
            [r"C:\Disk1\file.bak", "Backup File", "High Risk", "drop", "drop", "drop", "drop", "drop", "drop"],
            [r"C:\Disk1\new.txt", "empty", "No Match", "drop", "drop", "drop", "drop", "drop", "drop"]]
    column_names = ["FITS_File_Path", "FITS_Format_Name", "NARA_Risk Level", "FITS_PUID", "FITS_Identifying_Tool(s)",
                    "FITS_Creating_Application", "FITS_Valid", "FITS_Well-Formed", "FITS_Status_Message"]
    df_results = pd.DataFrame(rows, columns=column_names)

    # Calculates the subset.
    # In format_analysis.py, this is done in the main body of the script.
    df_nara_risk = df_results[df_results["NARA_Risk Level"] != "Low Risk"].copy()
    df_nara_risk.drop(["FITS_PUID", "FITS_Identifying_Tool(s)", "FITS_Creating_Application",
                       "FITS_Valid", "FITS_Well-Formed", "FITS_Status_Message"], inplace=True, axis=1)

    # Makes a dataframe with the expected values.
    rows = [[r"C:\Disk1\file.psd", "Adobe Photoshop file", "Moderate Risk"],
            [r"C:\Disk1\file.bak", "Backup File", "High Risk"],
            [r"C:\Disk1\new.txt", "empty", "No Match"]]
    column_names = ["FITS_File_Path", "FITS_Format_Name", "NARA_Risk Level"]
    df_expected = pd.DataFrame(rows, columns=column_names)

    # Compares the script output to the expected values.
    compare_dataframes("NARA_Risk_Subset", df_nara_risk, df_expected)


def test_multiple_subset():
    """Tests the files with multiple FITs format ids subset, which is based on the FITS_File_Path column."""

    # Makes a dataframe to use as input.
    # Data variation: files with multiple ids and files without; all columns to be dropped.
    rows = [[r"C:\Disk1\file1.txt", "Plain text", False, "drop", "drop", "drop"],
            [r"C:\Disk1\file2.html", "Hypertext Markup Language", True, "drop", "drop", "drop"],
            [r"C:\Disk1\file2.html", "HTML Transitional", True, "drop", "drop", "drop"],
            [r"C:\Disk1\file3.xlsx", "Open Office XML Document", True, "drop", "drop", "drop"],
            [r"C:\Disk1\file3.xlsx", "Open Office XML Workbook", True, "drop", "drop", "drop"],
            [r"C:\Disk1\file3.xlsx", "XLSX", True, "drop", "drop", "drop"],
            [r"C:\Disk1\photo.jpg", "JPEG EXIF", False, "drop", "drop", "drop"]]
    column_names = ["FITS_File_Path", "FITS_Format_Name", "FITS_Multiple_IDs",
                    "FITS_Valid", "FITS_Well-Formed", "FITS_Status_Message"]
    df_results = pd.DataFrame(rows, columns=column_names)

    # Calculates the subset.
    # In format_analysis.py, this is done in the main body of the script.
    df_multiple = df_results[df_results.duplicated("FITS_File_Path", keep=False) == True].copy()
    df_multiple.drop(["FITS_Valid", "FITS_Well-Formed", "FITS_Status_Message"], inplace=True, axis=1)

    # Makes a dataframe with the expected values.
    rows = [[r"C:\Disk1\file2.html", "Hypertext Markup Language", True],
            [r"C:\Disk1\file2.html", "HTML Transitional", True],
            [r"C:\Disk1\file3.xlsx", "Open Office XML Document", True],
            [r"C:\Disk1\file3.xlsx", "Open Office XML Workbook", True],
            [r"C:\Disk1\file3.xlsx", "XLSX", True]]
    column_names = ["FITS_File_Path", "FITS_Format_Name", "FITS_Multiple_IDs"]
    df_expected = pd.DataFrame(rows, columns=column_names)

    # Compares the script output to the expected values.
    compare_dataframes("Multiple_Subset", df_multiple, df_expected)


def test_validation_subset():
    """Tests the FITS validation subset, which is based on the FITS_Valid, FITS_Well-Formed,
    and FITS_Status_Message columns."""

    # Makes a dataframe to use as input.
    # Data variation: values in 0, 1, 2, or 3 columns will include the file in the validation subset.
    # Some of these combinations probably wouldn't happen in real data, but want to be thorough.
    rows = [[r"C:\Disk1\file1.txt", "Plain text", True, True, np.NaN],
            [r"C:\Disk1\file2.html", "Hypertext Markup Language", np.NaN, np.NaN, np.NaN],
            [r"C:\Disk1\file2.html", "HTML Transitional", False, True, np.NaN],
            [r"C:\Disk1\file3.xlsx", "Open Office XML Document", True, False, np.NaN],
            [r"C:\Disk1\file3.xlsx", "Open Office XML Workbook", True, True, "Validation Error"],
            [r"C:\Disk1\file3.xlsx", "XLSX", False, False, np.NaN],
            [r"C:\Disk1\photo.jpg", "JPEG EXIF", True, False, "Validation Error"],
            [r"C:\Disk1\photo1.jpg", "JPEG EXIF", False, True, "Validation Error"],
            [r"C:\Disk1\photo2.jpg", "JPEG EXIF", False, False, "Validation Error"]]
    column_names = ["FITS_File_Path", "FITS_Format_Name", "FITS_Valid", "FITS_Well-Formed", "FITS_Status_Message"]
    df_results = pd.DataFrame(rows, columns=column_names)

    # Calculates the subset.
    # In format_analysis.py, this is done in the main body of the script.
    df_validation = df_results[(df_results["FITS_Valid"] == False) | (df_results["FITS_Well-Formed"] == False) |
                               (df_results["FITS_Status_Message"].notnull())].copy()

    # Makes a dataframe with the expected values.
    rows = [[r"C:\Disk1\file2.html", "HTML Transitional", False, True, np.NaN],
            [r"C:\Disk1\file3.xlsx", "Open Office XML Document", True, False, np.NaN],
            [r"C:\Disk1\file3.xlsx", "Open Office XML Workbook", True, True, "Validation Error"],
            [r"C:\Disk1\file3.xlsx", "XLSX", False, False, np.NaN],
            [r"C:\Disk1\photo.jpg", "JPEG EXIF", True, False, "Validation Error"],
            [r"C:\Disk1\photo1.jpg", "JPEG EXIF", False, True, "Validation Error"],
            [r"C:\Disk1\photo2.jpg", "JPEG EXIF", False, False, "Validation Error"]]
    column_names = ["FITS_File_Path", "FITS_Format_Name", "FITS_Valid", "FITS_Well-Formed", "FITS_Status_Message"]
    df_expected = pd.DataFrame(rows, columns=column_names)

    # Compares the script output to the expected values.
    compare_dataframes("Validation_Subset", df_validation, df_expected)


def test_tech_appraisal_subset():
    """Tests the technical appraisal subset, which is based on the Technical_Appraisal column."""

    # Makes a dataframe to use as input.
    # Data variation: all 3 technical appraisal categories and all columns to drop.
    rows = [["DOS/Windows Executable", "Format", "drop", "drop", "drop", "drop", "drop", "drop"],
            ["JPEG EXIF", "Not for TA", "drop", "drop", "drop", "drop", "drop", "drop"],
            ["Unknown Binary", "Format", "drop", "drop", "drop", "drop", "drop", "drop"],
            ["Plain text", "Not for TA", "drop", "drop", "drop", "drop", "drop", "drop"],
            ["JPEG EXIF", "Trash", "drop", "drop", "drop", "drop", "drop", "drop"],
            ["Open Office XML Workbook", "Trash", "drop", "drop", "drop", "drop", "drop", "drop"]]
    column_names = ["FITS_Format_Name", "Technical_Appraisal", "FITS_PUID", "FITS_Date_Last_Modified",
                    "FITS_MD5", "FITS_Valid", "FITS_Well-Formed", "FITS_Status_Message"]
    df_results = pd.DataFrame(rows, columns=column_names)

    # Calculates the subset.
    # In format_analysis.py, this is done in the main body of the script.
    df_tech_appraisal = df_results[df_results["Technical_Appraisal"] != "Not for TA"].copy()
    df_tech_appraisal.drop(["FITS_PUID", "FITS_Date_Last_Modified", "FITS_MD5", "FITS_Valid", "FITS_Well-Formed",
                            "FITS_Status_Message"], inplace=True, axis=1)

    # Makes a dataframe with the expected values.
    rows = [["DOS/Windows Executable", "Format"],
            ["Unknown Binary", "Format"],
            ["JPEG EXIF", "Trash"],
            ["Open Office XML Workbook", "Trash"]]
    column_names = ["FITS_Format_Name", "Technical_Appraisal"]
    df_expected = pd.DataFrame(rows, columns=column_names)

    # Compares the script output to the expected values.
    compare_dataframes("Tech_Appraisal_Subset", df_tech_appraisal, df_expected)


def test_other_risk_subset():
    """Tests the other risk subset, which is based on the Other_Risk column."""

    # Makes a dataframe to use as input.
    # Data variation: all other risk categories and all columns to drop.
    rows = [["DOS/Windows Executable", "Not for Other", "drop", "drop", "drop", "drop", "drop", "drop", "drop"],
            ["Adobe Photoshop file", "Layered image file", "drop", "drop", "drop", "drop", "drop", "drop", "drop"],
            ["JPEG EXIF", "Not for Other", "drop", "drop", "drop", "drop", "drop", "drop", "drop"],
            ["Cascading Style Sheet", "Possible saved web page", "drop", "drop", "drop", "drop", "drop", "drop", "drop"],
            ["iCalendar", "NARA Low/Transform", "drop", "drop", "drop", "drop", "drop", "drop", "drop"],
            ["Zip Format", "Archive format", "drop", "drop", "drop", "drop", "drop", "drop", "drop"]]
    column_names = ["FITS_Format_Name", "Other_Risk", "FITS_PUID", "FITS_Date_Last_Modified", "FITS_MD5",
                    "FITS_Creating_Application", "FITS_Valid", "FITS_Well-Formed", "FITS_Status_Message"]
    df_results = pd.DataFrame(rows, columns=column_names)

    # Calculates the subset.
    # In format_analysis.py, this is done in the main body of the script.
    df_other_risk = df_results[df_results["Other_Risk"] != "Not for Other"].copy()
    df_other_risk.drop(["FITS_PUID", "FITS_Date_Last_Modified", "FITS_MD5", "FITS_Creating_Application", "FITS_Valid",
                        "FITS_Well-Formed", "FITS_Status_Message"], inplace=True, axis=1)

    # Makes a dataframe with the expected values.
    rows = [["Adobe Photoshop file", "Layered image file"],
            ["Cascading Style Sheet", "Possible saved web page"],
            ["iCalendar", "NARA Low/Transform"],
            ["Zip Format", "Archive format"]]
    column_names = ["FITS_Format_Name", "Other_Risk"]
    df_expected = pd.DataFrame(rows, columns=column_names)

    # Compares the script output to the expected values.
    compare_dataframes("Other_Risk_Subset", df_other_risk, df_expected)


def test_duplicates_subset():
    """Tests the duplicates subset, which is based on the FITS_File_Path and FITS_MD5 columns."""

    # Makes a dataframe to use as input.
    # Data variation: unique files, files duplicate because of multiple FITs file ids, and real duplicate files.
    rows = [[r"C:\Disk1\file1.txt", "Plain text", 0.004, "098f6bcd4621d373cade4e832627b4f6"],
            [r"C:\Disk1\file3.xlsx", "Open Office XML Document", 19.316, "b66e2fa385872d1a16d31b00f4b5f035"],
            [r"C:\Disk1\file3.xlsx", "Open Office XML Workbook", 19.316, "b66e2fa385872d1a16d31b00f4b5f035"],
            [r"C:\Disk1\file3.xlsx", "XLSX", 19.316, "b66e2fa385872d1a16d31b00f4b5f035"],
            [r"C:\Disk1\photo.jpg", "JPEG EXIF", 13.563, "686779fae835aadff6474898f5781e99"],
            [r"C:\Disk2\file1.txt", "Plain text", 0.004, "098f6bcd4621d373cade4e832627b4f6"],
            [r"C:\Disk3\file1.txt", "Plain text", 0.004, "098f6bcd4621d373cade4e832627b4f6"]]
    column_names = ["FITS_File_Path", "FITS_Format_Name", "FITS_Size_KB", "FITS_MD5"]
    df_results = pd.DataFrame(rows, columns=column_names)

    # Calculates the subset.
    # In format_analysis.py, this is done in the main body of the script.
    df_duplicates = df_results[["FITS_File_Path", "FITS_Size_KB", "FITS_MD5"]].copy()
    df_duplicates = df_duplicates.drop_duplicates(subset=["FITS_File_Path"], keep=False)
    df_duplicates = df_duplicates.loc[df_duplicates.duplicated(subset="FITS_MD5", keep=False)]

    # Makes a dataframe with the expected values.
    rows = [[r"C:\Disk1\file1.txt", 0.004, "098f6bcd4621d373cade4e832627b4f6"],
            [r"C:\Disk2\file1.txt", 0.004, "098f6bcd4621d373cade4e832627b4f6"],
            [r"C:\Disk3\file1.txt", 0.004, "098f6bcd4621d373cade4e832627b4f6"]]
    column_names = ["FITS_File_Path", "FITS_Size_KB", "FITS_MD5"]
    df_expected = pd.DataFrame(rows, columns=column_names)

    # Compares the script output to the expected values.
    compare_dataframes("Duplicates_Subset", df_duplicates, df_expected)


def test_empty_subset():
    """Tests handling of an empty subset, which can happen with any subset.
    Using the file with multiple format ids and duplicate MD5s subsets for testing."""

    # Makes a dataframe to use as input where all files have a unique identification and unique MD5.
    rows = [[r"C:\Disk1\file1.txt", "Plain text", 0.004, "098f6bcd4621d373cade4e832627b4f6"],
            [r"C:\Disk1\file2.txt", "Plain text", 5.347, "c9f6d785a33cfac2cc1f51ab4704b8a1"],
            [r"C:\Disk2\file3.pdf", "Portable Document Format", 187.972, "6dfeecf4e4200a0ad147a7271a094e68"],
            [r"c:\Disk2\file4.txt", "Plain text", 0.178, "97e4f6e6f35e5606855d0917e22740b9"]]
    column_names = ["FITS_File_Path", "FITS_Format_Name", "FITS_Size_KB", "FITS_MD5"]
    df_results = pd.DataFrame(rows, columns=column_names)

    # Calculates both subsets.
    # In format_analysis.py, this is done in the main body of the script.
    df_multiple = df_results[df_results.duplicated("FITS_File_Path", keep=False) == True].copy()

    df_duplicates = df_results[["FITS_File_Path", "FITS_Size_KB", "FITS_MD5"]].copy()
    df_duplicates = df_duplicates.drop_duplicates(subset=["FITS_File_Path"], keep=False)
    df_duplicates = df_duplicates.loc[df_duplicates.duplicated(subset="FITS_MD5", keep=False)]

    # Tests each subset for if they are empty and supplies default text.
    # In format_analysis.py, this is done in the main body of the script
    # and includes all 6 subset dataframes in the tuple.
    for df in (df_multiple, df_duplicates):
        if len(df) == 0:
            df.loc[len(df)] = ["No data of this type"] + [np.NaN] * (len(df.columns) - 1)

    # Makes dataframes with the expected values for each subset.
    rows = [["No data of this type", np.NaN, np.NaN, np.NaN]]
    column_names = ["FITS_File_Path", "FITS_Format_Name", "FITS_Size_KB", "FITS_MD5"]
    df_multiple_expected = pd.DataFrame(rows, columns=column_names)

    rows = [["No data of this type", np.NaN, np.NaN]]
    column_names = ["FITS_File_Path", "FITS_Size_KB", "FITS_MD5"]
    df_duplicates_expected = pd.DataFrame(rows, columns=column_names)

    # Compares the script output to the expected values for each subset.
    compare_dataframes("Empty_Multiple_Subset", df_multiple, df_multiple_expected)
    compare_dataframes("Empty_Duplicate_Subset", df_duplicates, df_duplicates_expected)


def test_format_subtotal():
    """Tests the format subtotals, which is based on FITS_Format_Name and NARA_Risk Level."""

    # Makes a dataframe to use as input for the subtotal() function.
    # Data variation: formats with one row, formats with multiple rows, one format with a NARA risk level,
    # multiple formats with a NARA risk level, blank in NARA risk level.
    rows = [["JPEG EXIF", 13.563, "Low Risk"],
            ["JPEG EXIF", 14.1, "Low Risk"],
            ["Open Office XML Workbook", 19.316, "Low Risk"],
            ["Unknown Binary", 0, np.NaN],
            ["Unknown Binary", 1, np.NaN],
            ["Unknown Binary", 5, np.NaN],
            ["XLSX", 19.316, "Low Risk"],
            ["Zip Format", 2.792, "Moderate Risk"]]
    column_names = ["FITS_Format_Name", "FITS_Size_KB", "NARA_Risk Level"]
    df_results = pd.DataFrame(rows, columns=column_names)

    # Calculates the total files and total size in the dataframe to use for percentages with the subtotals.
    # In format_analysis.py, this is done in the main body of the script before subtotal() is called.
    totals_dict = {"Files": len(df_results.index), "MB": df_results["FITS_Size_KB"].sum() / 1000}

    # Runs the subtotal() function for this subtotal.
    df_format_subtotals = subtotal(df_results, ["FITS_Format_Name", "NARA_Risk Level"], totals_dict)

    # Makes a dataframe with the expected values.
    # The index values for the dataframe made by subtotal() are column values here
    # so that they are visible in the comparison dataframe to label errors.
    rows = [["JPEG EXIF", "Low Risk", 2, 25, 0.028, 37.29],
            ["Unknown Binary", np.NaN, 3, 37.5, 0.006, 7.991],
            ["Zip Format", "Moderate Risk", 1, 12.5, 0.003, 3.995],
            ["Open Office XML Workbook", "Low Risk", 1, 12.5, 0.019, 25.304],
            ["XLSX", "Low Risk", 1, 12.5, 0.019, 25.304]]
    column_names = ["FITS_Format_Name", "NARA_Risk Level", "File Count", "File %", "Size (MB)", "Size %"]
    df_expected = pd.DataFrame(rows, columns=column_names)

    # Compares the script output to the expected values.
    compare_dataframes("Format_Subtotals", df_format_subtotals, df_expected)


def test_nara_risk_subtotal():
    """Tests the NARA risk subtotals, which is based on NARA_Risk Level."""

    # Makes a dataframe to use as input for the subtotal() function.
    # Data variation: one format with a NARA risk level, multiple formats with a NARA risk level, all 4 risk levels.
    rows = [["DOS/Windows Executable", 1.23, "High Risk"],
            ["DOS/Windows Executable", 2.34, "High Risk"],
            ["DOS/Windows Executable", 3.45, "High Risk"],
            ["JPEG EXIF", 13.563, "Low Risk"],
            ["JPEG EXIF", 14.1, "Low Risk"],
            ["Open Office XML Workbook", 19.316, "Low Risk"],
            ["Unknown Binary", 0, "No Match"],
            ["Unknown Binary", 5, "No Match"],
            ["XLSX", 19.316, "Low Risk"],
            ["Zip Format", 2.792, "Moderate Risk"]]
    column_names = ["FITS_Format_Name", "FITS_Size_KB", "NARA_Risk Level"]
    df_results = pd.DataFrame(rows, columns=column_names)

    # Calculates the total files and total size in the dataframe to use for percentages with the subtotals.
    # In format_analysis.py, this is done in the main body of the script before subtotal() is called.
    totals_dict = {"Files": len(df_results.index), "MB": df_results["FITS_Size_KB"].sum() / 1000}

    # Runs the subtotal() function for this subtotal.
    df_nara_risk_subtotals = subtotal(df_results, ["NARA_Risk Level"], totals_dict)

    # Makes a dataframe with the expected values.
    # The index value for the dataframe made by subtotal() is a column value here
    # so that it is visible in the comparison dataframe to label errors.
    rows = [["Low Risk", 4, 40, 0.066, 81.374],
            ["Moderate Risk", 1, 10, 0.003, 3.699],
            ["High Risk", 3, 30, 0.007, 8.631],
            ["No Match", 2, 20, 0.005, 6.165]]
    column_names = ["NARA_Risk Level", "File Count", "File %", "Size (MB)", "Size %"]
    df_expected = pd.DataFrame(rows, columns=column_names)

    # Compares the script output to the expected values.
    compare_dataframes("NARA_Risk_Subtotals", df_nara_risk_subtotals, df_expected)


def test_technical_appraisal_subtotal():
    """Tests the technical appraisal subtotals, which is based on technical appraisal criteria and FITS_Format_Name."""

    # Makes a dataframe to use as input for the subtotal() function.
    # Data variation: for both criteria, has a unique format and duplicated formats.
    rows = [["Format", "DOS/Windows Executable", 100.23],
            ["Format", "DOS/Windows Executable", 200.34],
            ["Format", "PE32 executable", 300.45],
            ["Format", "Unknown Binary", 0],
            ["Format", "Unknown Binary", 50],
            ["Trash", "JPEG EXIF", 130.563],
            ["Trash", "JPEG EXIF", 140.1],
            ["Trash", "Open Office XML Workbook", 190.316]]
    column_names = ["Technical_Appraisal", "FITS_Format_Name", "FITS_Size_KB"]
    df_results = pd.DataFrame(rows, columns=column_names)

    # Calculates the total files and total size in the dataframe to use for percentages with the subtotals.
    # In format_analysis.py, this is done in the main body of the script before subtotal() is called.
    totals_dict = {"Files": len(df_results.index), "MB": df_results["FITS_Size_KB"].sum() / 1000}

    # Runs the subtotal() function for this subtotal.
    df_tech_appraisal_subtotals = subtotal(df_results, ["Technical_Appraisal", "FITS_Format_Name"], totals_dict)

    # Makes a dataframe with the expected values.
    # The index values for the dataframes made by subtotal() are column values here
    # so that they are visible in the comparison dataframe to label errors.
    rows = [["Format", "DOS/Windows Executable", 2, 25, 0.301, 27.068],
            ["Format", "PE32 executable", 1, 12.5, 0.300, 26.978],
            ["Format", "Unknown Binary", 2, 25, 0.05, 4.496],
            ["Trash", "JPEG EXIF", 2, 25, 0.271, 24.371],
            ["Trash", "Open Office XML Workbook", 1, 12.5, 0.19, 17.086]]
    column_names = ["Technical_Appraisal", "FITS_Format_Name", "File Count", "File %", "Size (MB)", "Size %"]
    df_expected = pd.DataFrame(rows, columns=column_names)

    # Compares the script output to the expected values.
    compare_dataframes("Tech_Appraisal_Subtotals", df_tech_appraisal_subtotals, df_expected)


def test_technical_appraisal_subtotal_empty():
    """Tests the technical appraisal subtotals when there are no files in the input
    which meet any technical appraisal criteria."""

    # Makes an empty dataframe to use as input for the subtotal() function.
    df_results = pd.DataFrame(columns=["Technical_Appraisal", "FITS_Format_Name", "FITS_Size_KB"])

    # Calculates the total files and total size in the dataframe to use for percentages with the subtotals.
    # In format_analysis.py, this is done in the main body of the script before subtotal() is called.
    totals_dict = {"Files": len(df_results.index), "MB": df_results["FITS_Size_KB"].sum() / 1000}

    # Runs the subtotal() function for this subtotal.
    df_tech_appraisal_subtotals = subtotal(df_results, ["Technical_Appraisal", "FITS_Format_Name"], totals_dict)

    # Makes a dataframe with the expected values.
    rows = [["No data of this type", np.NaN, np.NaN, np.NaN]]
    column_names = ["File Count", "File %", "Size (MB)", "Size %"]
    df_expected = pd.DataFrame(rows, columns=column_names)

    # Compares the script output to the expected values.
    compare_dataframes("Tech_Appraisal_Subtotals_Empty", df_tech_appraisal_subtotals, df_expected)


def test_other_risk_subtotal():
    """Tests the other risk subtotals, which is based on other risk criteria and FITS_Format_Name."""

    # Makes a dataframe to use as input for the subtotal() function.
    # Data variation: for each of the values for other risk, has unique formats and duplicated formats.
    rows = [["Not for Other", "DOS/Windows Executable", 100.23],
            ["Not for Other", "JPEG EXIF", 1300.563],
            ["Not for Other", "JPEG EXIF", 1400.1],
            ["Not for Other", "JPEG EXIF", 1900.316],
            ["Not for Other", "PE32 Executable", 200.34],
            ["Possible saved web page", "Cascading Style Sheet", 10000],
            ["Archive format", "Zip Format", 20000],
            ["Archive format", "Zip Format", 20000],
            ["Archive format", "Zip Format", 30000],
            ["Archive format", "Zip Format", 30000]]
    column_names = ["Other_Risk", "FITS_Format_Name", "FITS_Size_KB"]
    df_results = pd.DataFrame(rows, columns=column_names)

    # Calculates the total files and total size in the dataframe to use for percentages with the subtotals.
    # In format_analysis.py, this is done in the main body of the script before subtotal() is called.
    totals_dict = {"Files": len(df_results.index), "MB": df_results["FITS_Size_KB"].sum() / 1000}

    # Runs the subtotal() function for this subtotal.
    df_other_risk_subtotals = subtotal(df_results, ["Other_Risk", "FITS_Format_Name"], totals_dict)

    # Makes a dataframe with the expected values.
    # The index values for the dataframes made by subtotal() are column values here
    # so that they are visible in the comparison dataframe to label errors.
    rows = [["Not for Other", "DOS/Windows Executable", 1, 10, 0.1, 0.087],
            ["Not for Other", "JPEG EXIF", 3, 30, 4.601, 4.004],
            ["Not for Other", "PE32 Executable", 1, 10, 0.2, 0.174],
            ["Possible saved web page", "Cascading Style Sheet", 1, 10, 10, 8.703],
            ["Archive format", "ZIP Format", 4, 40, 100, 87.031]]
    column_names = ["Other_Risk", "FITS_Format_Name", "File Count", "File %", "Size (MB)", "Size %"]
    df_expected = pd.DataFrame(rows, columns=column_names)

    # Compares the script output to the expected values.
    compare_dataframes("Other_Risk_Subtotals", df_other_risk_subtotals, df_expected)


def test_other_risk_subtotal_empty():
    """Tests the other risk subtotals when there are no files in the input which meet any other risk criteria."""

    # Makes an empty dataframe to use as input for the subtotal() function.
    df_results = pd.DataFrame(columns=["Other_Risk", "FITS_Format_Name", "FITS_Size_KB"])

    # Calculates the total files and total size in the dataframe to use for percentages with the subtotals.
    # In format_analysis.py, this is done in the main body of the script before subtotal() is called.
    totals_dict = {"Files": len(df_results.index), "MB": df_results["FITS_Size_KB"].sum() / 1000}

    # Runs the subtotal() function for this subtotal.
    df_other_risk_subtotals = subtotal(df_results, ["Other_Risk", "FITS_Format_Name"], totals_dict)

    # Makes a dataframe with the expected values.
    rows = [["No data of this type", np.NaN, np.NaN, np.NaN]]
    column_names = ["File Count", "File %", "Size (MB)", "Size %"]
    df_expected = pd.DataFrame(rows, columns=column_names)

    # Compares the script output to the expected values.
    compare_dataframes("Other_Risk_Subtotals_Empty", df_other_risk_subtotals, df_expected)


def test_iteration_tbd():
    """Tests that the script follows the correct logic based on the contents of the accession folder and
    that the contents are updated correctly. Runs the script 3 times to check all iterations.
    This may be enough for testing script output or may make a separate test."""


# Makes the output directory (the only script argument) the current directory for easier saving.
# If the argument is missing or not a valid directory, ends the script.
try:
    output = sys.argv[1]
    os.chdir(output)
except (IndexError, FileNotFoundError):
    print("\nThe required script argument (output folder) is missing or incorrect.")
    sys.exit()

# Calls each of the test functions, which either test a function in format_analysis.py or
# one of the analysis components, such as the duplicates subset or NARA risk subtotal.
# A summary of the test result is printed to the terminal and failed tests are saved to the output folder.

test_match_nara_risk_function()
test_match_technical_appraisal_function()
test_match_other_risk_function()

test_nara_risk_subset()
test_multiple_subset()
test_validation_subset()
test_tech_appraisal_subset()
test_other_risk_subset()
test_duplicates_subset()
test_empty_subset()

test_format_subtotal()
test_nara_risk_subtotal()
test_technical_appraisal_subtotal()
test_technical_appraisal_subtotal_empty()
test_other_risk_subtotal()
test_other_risk_subtotal_empty()

print("\nThe script is complete.")
