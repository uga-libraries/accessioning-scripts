"""Purpose: tests for each function and analysis component (each subset and subtotal) in the format_analysis.py script.
Each test creates simplified input, runs the code, and compares it to the expected output.
Test results are saved to a directory specified with the script argument.
Comment out any test you do not wish to run.

For any tests that do not import the function from format_analysis.py, sync the code before running the test.
If the input for any function or analysis changes, edit the test input and expected results."""

# usage: python path/format_analysis_tests.py output_folder

import numpy as np
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


def test_match_technical_appraisal():
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

    # Reads the CSV with formats that indicate technical appraisal into the dataframe.
    # In format_analysis.py, this is done a little earlier in the script.
    df_ita = csv_to_dataframe(c.ITA)

    # Adds the format technical appraisal category (defined in ITAfileformats.csv).
    ta_list = df_ita["FITS_FORMAT"].tolist()
    df_results.loc[df_results["FITS_Format_Name"].str.contains("|".join(map(re.escape, ta_list)), case=False),
                   "Technical_Appraisal"] = "Format"

    # Adds the trash folder technical appraisal category.
    # If something is both format and trash, Trash will overwrite Format.
    df_results.loc[df_results["FITS_File_Path"].str.contains("\\\\trash\\\\|\\\\trashes\\\\", case=False),
                   "Technical_Appraisal"] = "Trash"

    # Adds default text for formats that aren't in either technical appraisal category.
    df_results["Technical_Appraisal"] = df_results["Technical_Appraisal"].fillna(value="Not for TA")

    # Makes a dataframe with the expected values.
    df_expected = pd.DataFrame([[r"C:\CD1\Flower.JPG", "JPEG EXIF", "Not for TA"],
                                [r"C:\CD1\Trashes\Flower1.JPG", "JPEG EXIF", "Trash"],
                                [r"C:\CD2\Script\config.pyc", "unknown binary", "Format"],
                                [r"C:\CD2\Trash Data\data.zip", "ZIP Format", "Not for TA"],
                                [r"C:\CD2\trash\New Document.txt", "Plain text", "Trash"],
                                [r"C:\CD2\Trash\New Text.txt", "Plain text", "Trash"],
                                [r"C:\FD1\empty.txt", "empty", "Format"],
                                [r"C:\FD1\trashes\program.dll", "PE32 executable", "Trash"]],
                               columns=["FITS_File_Path", "FITS_Format_Name", "Technical Appraisal"])

    # Compares the script output to the expected values.
    compare_dataframes("Match_TA", df_results, df_expected)


def test_match_other_risk():
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

    # Reads the CSV with formats that indicate other risk into the dataframe.
    # In format_analysis.py, this is done a little earlier in the script.
    df_risk = csv_to_dataframe(c.RISK)

    # Adds the NARA other risk category (defined in ITAfileformats.csv).
    df_results.loc[(df_results["NARA_Risk Level"] == "Low Risk") & (df_results["NARA_Proposed Preservation Plan"].str.startswith("Transform")),
                   "Other_Risk"] = "NARA Low/Transform"

    # Adds the format risk categories (defined in Riskfileformats.csv).
    # If something is both NARA and format, the format category will overwrite NARA.
    risk_list = df_risk["FITS_FORMAT"].tolist()
    indexes = df_results.loc[df_results["FITS_Format_Name"].str.contains("|".join(map(re.escape, risk_list)), case=False)].index
    for index in indexes:
        format_name = df_results.loc[index, "FITS_Format_Name"].lower()
        risk_criteria = df_risk[df_risk["FITS_FORMAT"].str.lower() == format_name]["RISK_CRITERIA"].values[0]
        df_results.loc[index, "Other_Risk"] = risk_criteria

    # Adds default text for formats that aren't in either other risk category.
    df_results["Other_Risk"] = df_results["Other_Risk"].fillna(value="Not for Other")

    # Makes a dataframe with the expected values.
    df_expected = pd.DataFrame([["Adobe Photoshop file", "Moderate Risk", "Transform to TIFF or JPEG2000", "Layered image file"],
                                ["Cascading Style Sheet", "Low Risk", "Retain", "Possible saved web page"],
                                ["CorelDraw Drawing", "High Risk", "Transform to a TBD format, possibly PDF or TIFF", "Layered image file"],
                                ["empty", np.NaN, np.NaN, "Not for Other"],
                                ["Encapsulated Postscript File", "Low Risk", "Transform to TIFF or JPEG2000", "Layered image file"],
                                ["iCalendar", "Low Risk", "Transform to CSV", "NARA Low/Transform"],
                                ["MBOX Email Format", "Low Risk", "Transform to EML but also retain MBOX", "NARA Low/Transform"],
                                ["Plain text", "Low Risk", "Retain", "Not for Other"],
                                ["zip format", "Low Risk", "Retain", "Archive format"]],
                               columns=["FITS_Format_Name", "NARA_Risk Level", "NARA_Proposed Preservation Plan", "Other_Risk"])

    # Compares the script output to the expected values.
    compare_dataframes("Match_Other", df_results, df_expected)


def test_subtotal_function():
    """Tests both input scenarios for this function: one or two initial criteria."""

    # Makes a dataframe to use for input for both of the scenarios.
    # Data variation: unique rows, rows that will be added together for subtotals.
    rows = [["JPEG EXIF", 13.563, False, "Low Risk"],
            ["JPEG EXIF", 14.1, False, "Low Risk"],
            ["Open Office XML Workbook", 19.316, True, "Low Risk"],
            ["Unknown Binary", 0, False, np.NaN],
            ["Unknown Binary", 1, False, np.NaN],
            ["Unknown Binary", 5, False, np.NaN],
            ["XLSX", 19.316, True, "Low Risk"],
            ["Zip Format", 2.792, False, "Moderate Risk"]]
    column_names = ["FITS_Format_Name", "FITS_Size_KB", "Multiple_IDs", "NARA_Risk Level"]
    df = pd.DataFrame(rows, columns=column_names)

    # Calculates the total files and total size in the dataframe to use for percentages with the subtotals.
    # In format_analysis.py, this is done in the main body of the script before subtotal() is called.
    totals_dict = {"Files": len(df.index), "MB": df["FITS_Size_KB"].sum() / 1000}

    # Runs the subtotal() function for each input scenario.
    df_one = subtotal(df, ["NARA_Risk Level"], totals_dict)
    df_two = subtotal(df, ["Multiple_IDs", "FITS_Format_Name"], totals_dict)

    # Makes dataframes with the expected values for each input scenario.
    # The index values for the dataframes made by subtotal() are column values here
    # so that they are visible in the comparison dataframe to label errors.
    df_one_expected = pd.DataFrame([["Low Risk", 4, 50, 0.066, 87.898],
                                    ["Moderate Risk", 1, 12.5, .003, 3.995],
                                    [np.NaN, 3, 37.5, 0.006, 7.991]],
                                   columns=["NARA_Risk Level", "File Count", "File %", "Size (MB)", "Size %"])
    df_two_expected = pd.DataFrame([[False, "JPEG EXIF", 2, 25, 0.028, 37.29],
                                    [False, "Unknown Binary", 3, 37.5, 0.006, 7.991],
                                    [False, "Zip Format", 1, 12.5, 0.003, 3.995],
                                    [True, "Open Office XML Workbook", 1, 12.5, 0.019, 25.304],
                                    [True, "XLSX", 1, 12.5, 0.019, 25.304]],
                                   columns=["Multiple_IDs", "FITS_Format_Name", "File Count", "File %", "Size (MB)", "Size %"])

    # Compares the script output for each input scenario to the expected values.
    compare_dataframes("Subtotal_Function_One_Criteria", df_one, df_one_expected)
    compare_dataframes("Subtotal_Function_Two_Criteria", df_two, df_two_expected)


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
    df = pd.DataFrame(rows, columns=column_names)

    # Calculates the total files and total size in the dataframe to use for percentages with the subtotals.
    # In format_analysis.py, this is done in the main body of the script before subtotal() is called.
    totals_dict = {"Files": len(df.index), "MB": df["FITS_Size_KB"].sum() / 1000}

    # Runs the subtotal() function for this subtotal.
    df_subtotals = subtotal(df, ["FITS_Format_Name", "NARA_Risk Level"], totals_dict)

    # Makes a dataframe with the expected values.
    # The index values for the dataframe made by subtotal() are column values here
    # so that they are visible in the comparison dataframe to label errors.
    df_expected = pd.DataFrame([["JPEG EXIF", "Low Risk", 2, 25, 0.028, 37.29],
                                ["Unknown Binary", np.NaN, 3, 37.5, 0.006, 7.991],
                                ["Zip Format", "Moderate Risk", 1, 12.5, 0.003, 3.995],
                                ["Open Office XML Workbook", "Low Risk", 1, 12.5, 0.019, 25.304],
                                ["XLSX", "Low Risk", 1, 12.5, 0.019, 25.304]],
                               columns=["FITS_Format_Name", "NARA_Risk Level", "File Count", "File %", "Size (MB)", "Size %"])

    # Compares the script output to the expected values.
    compare_dataframes("Format_Subtotals", df_subtotals, df_expected)


def test_nara_risk_subtotal():
    """Tests the NARA risk subtotals, which is based on NARA_Risk Level."""

    # Makes a dataframe to use as input for the subtotal() function.
    # Data variation: one format with a NARA risk level, multiple formats with a NARA risk level, blanks.
    rows = [["DOS/Windows Executable", 1.23, "High Risk"],
            ["DOS/Windows Executable", 2.34, "High Risk"],
            ["DOS/Windows Executable", 3.45, "High Risk"],
            ["JPEG EXIF", 13.563, "Low Risk"],
            ["JPEG EXIF", 14.1, "Low Risk"],
            ["Open Office XML Workbook", 19.316, "Low Risk"],
            ["Unknown Binary", 0, np.NaN],
            ["Unknown Binary", 5, np.NaN],
            ["XLSX", 19.316, "Low Risk"],
            ["Zip Format", 2.792, "Moderate Risk"]]
    column_names = ["FITS_Format_Name", "FITS_Size_KB", "NARA_Risk Level"]
    df = pd.DataFrame(rows, columns=column_names)

    # Calculates the total files and total size in the dataframe to use for percentages with the subtotals.
    # In format_analysis.py, this is done in the main body of the script before subtotal() is called.
    totals_dict = {"Files": len(df.index), "MB": df["FITS_Size_KB"].sum() / 1000}

    # Runs the subtotal() function for this subtotal.
    df_subtotals = subtotal(df, ["NARA_Risk Level"], totals_dict)

    # Makes a dataframe with the expected values.
    # The index value for the dataframe made by subtotal() is a column value here
    # so that it is visible in the comparison dataframe to label errors.
    df_expected = pd.DataFrame([["Low Risk", 4, 40, 0.066, 81.374],
                                ["Moderate Risk", 1, 10, 0.003, 3.699],
                                ["High Risk", 3, 30, 0.007, 8.631],
                                [np.NaN, 2, 20, 0.005, 6.165]],
                               columns=["NARA_Risk Level", "File Count", "File %", "Size (MB)", "Size %"])

    # Compares the script output to the expected values.
    compare_dataframes("NARA_Risk_Subtotals", df_subtotals, df_expected)


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
    column_names = ["Criteria", "FITS_Format_Name", "FITS_Size_KB"]
    df = pd.DataFrame(rows, columns=column_names)

    # Calculates the total files and total size in the dataframe to use for percentages with the subtotals.
    # In format_analysis.py, this is done in the main body of the script before subtotal() is called.
    totals_dict = {"Files": len(df.index), "MB": df["FITS_Size_KB"].sum() / 1000}

    # Runs the subtotal() function for this subtotal.
    df_subtotals = subtotal(df, ["Criteria", "FITS_Format_Name"], totals_dict)

    # Makes a dataframe with the expected values.
    # The index values for the dataframes made by subtotal() are column values here
    # so that they are visible in the comparison dataframe to label errors.
    df_expected = pd.DataFrame([["Format", "DOS/Windows Executable", 2, 25, 0.301, 27.068],
                                ["Format", "PE32 executable", 1, 12.5, 0.300, 26.978],
                                ["Format", "Unknown Binary", 2, 25, 0.05, 4.496],
                                ["Trash", "JPEG EXIF", 2, 25, 0.271, 24.371],
                                ["Trash", "Open Office XML Workbook", 1, 12.5, 0.19, 17.086]],
                               columns=["Criteria", "FITS_Format_Name", "File Count", "File %", "Size (MB)", "Size %"])

    # Compares the script output to the expected values.
    compare_dataframes("Tech_Appraisal_Subtotals", df_subtotals, df_expected)


def test_other_risk_subtotal():
    """Tests the other risk subtotals, which is based on other risk criteria and FITS_Format_Name."""

    # Makes a dataframe to use as input for the subtotal() function.
    # Data variation: for each of the values for other risk, has unique formats and duplicated formats.
    rows = [[False, "DOS/Windows Executable", 100.23],
            [False, "JPEG EXIF", 1300.563],
            [False, "JPEG EXIF", 1400.1],
            [False, "JPEG EXIF", 1900.316],
            [False, "PE32 Executable", 200.34],
            [True, "Cascading Style Sheet", 10000],
            [True, "Zip Format", 20000],
            [True, "Zip Format", 20000],
            [True, "Zip Format", 30000],
            [True, "Zip Format", 30000]]
    column_names = ["Criteria", "FITS_Format_Name", "FITS_Size_KB"]
    df = pd.DataFrame(rows, columns=column_names)

    # Calculates the total files and total size in the dataframe to use for percentages with the subtotals.
    # In format_analysis.py, this is done in the main body of the script before subtotal() is called.
    totals_dict = {"Files": len(df.index), "MB": df["FITS_Size_KB"].sum() / 1000}

    # Runs the subtotal() function for this subtotal.
    df_subtotals = subtotal(df, ["Criteria", "FITS_Format_Name"], totals_dict)

    # Makes a dataframe with the expected values.
    # The index values for the dataframes made by subtotal() are column values here
    # so that they are visible in the comparison dataframe to label errors.
    df_expected = pd.DataFrame([[False, "DOS/Windows Executable", 1, 10, 0.1, 0.087],
                                [False, "JPEG EXIF", 3, 30, 4.601, 4.004],
                                [False, "PE32 Executable", 1, 10, 0.2, 0.174],
                                [True, "Cascading Style Sheet", 1, 10, 10, 8.703],
                                [True, "ZIP Format", 4, 40, 100, 87.031]],
                               columns=["Criteria", "FITS_Format_Name", "File Count", "File %", "Size (MB)", "Size %"])

    # Compares the script output to the expected values.
    compare_dataframes("Other_Risk_Subtotals", df_subtotals, df_expected)


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
# A summary of the test result is printed to the terminal and details saved to the output folder.
test_match_technical_appraisal()
test_match_other_risk()

test_subtotal_function()
test_format_subtotal()
test_nara_risk_subtotal()
test_technical_appraisal_subtotal()
test_other_risk_subtotal()

print("\nThe script is complete.")
