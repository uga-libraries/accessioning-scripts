"""Purpose: tests for each function and analysis component in the format_analysis.py script.
Each test produces input, runs the code, and compares it to the expected output.
Test results are saved to a directory specified with the script argument.
Comment out any test you do not wish to run.

For any tests that do not import the function from format_analysis.py, sync the code before running the test.
If the input for any function or analysis changes, edit the test input and expected results."""

# usage: python path/format_analysis_tests.py output_folder

import numpy as np
from format_analysis_functions import *


def compare_dataframes(test_name, df_actual, df_expected):
    """Compares two dataframes, the actual script output and the expected values.
    Prints if they match (test passes) or not and saves failed tests to a CSV for review."""

    # Makes a new dataframe that merges the values of the two.
    df_comparison = df_actual.merge(df_expected, indicator=True, how="outer")

    # Makes a dataframe with just the errors (merge value isn't both).
    df_errors = df_comparison[df_comparison["_merge"] != "both"]

    # If the merged dataframe is empty (everything matched), prints the test passed.
    # Otherwise, saves the dataframe with all the matches to a CSV in the output (current) directory.
    if len(df_errors) == 0:
        print("Test passes: ", test_name)
    else:
        print("Test fails:  ", test_name)
        df_comparison.to_csv(f"{test_name}_comparison_results.csv", index=False)


def test_subtotal_function():
    """Tests both input scenarios for this function: one or two initial criteria.
    Both scenarios include single-instance values and multi-instance values that need to be combined."""

    # Makes a dataframe as input for both of the scenarios.
    # It contains a subset of the columns that the real dataframe has to simplify testing.
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
    one = subtotal(df, ["NARA_Risk Level"], totals_dict)
    two = subtotal(df, ["Multiple_IDs", "FITS_Format_Name"], totals_dict)

    # Makes a dataframe with the expected values for each input scenario.
    # The index values for the dataframes made by subtotal() are column values here so that they
    # are visible in the results from comparing the dataframes as a label of values with errors.
    one_expected = pd.DataFrame([["Low Risk", 4, 50, 0.066, 87.898],
                                 ["Moderate Risk", 1, 12.5, .003, 3.995],
                                 [np.NaN, 3, 37.5, 0.006, 7.991]],
                                columns=["NARA_Risk Level", "File Count", "File %", "Size (MB)", "Size %"])
    two_expected = pd.DataFrame([[False, "JPEG EXIF", 2, 25, 0.028, 37.29],
                                 [False, "Unknown Binary", 3, 37.5, 0.006, 7.991],
                                 [False, "Zip Format", 1, 12.5, 0.003, 3.995],
                                 [True, "Open Office XML Workbook", 1, 12.5, 0.019, 25.304],
                                 [True, "XLSX", 1, 12.5, 0.019, 25.304]],
                                columns=["Multiple_IDs", "FITS_Format_Name", "File Count", "File %", "Size (MB)", "Size %"])

    # Compares the script output for each input scenario to the expected values.
    compare_dataframes("Subtotal_Function_One_Criteria", one, one_expected)
    compare_dataframes("Subtotal_Function_Two_Criteria", two, two_expected)


def test_format_subtotal():
    """Tests the format subtotals, which is based on FITS_Format_Name and NARA_Risk Level."""

    # Makes a dataframe as input.
    # It contains a subset of the columns that the real dataframe has to simplify testing.
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
    subtotals = subtotal(df, ["FITS_Format_Name", "NARA_Risk Level"], totals_dict)

    # Makes a dataframe with the expected values.
    # The index values for the dataframes made by subtotal() are column values here so that they
    # are visible in the results from comparing the dataframes as a label of values with errors.
    expected = pd.DataFrame([["JPEG EXIF", "Low Risk", 2, 25, 0.028, 37.29],
                             ["Unknown Binary", np.NaN, 3, 37.5, 0.006, 7.991],
                             ["Zip Format", "Moderate Risk", 1, 12.5, 0.003, 3.995],
                             ["Open Office XML Workbook", "Low Risk", 1, 12.5, 0.019, 25.304],
                             ["XLSX", "Low Risk", 1, 12.5, 0.019, 25.304]],
                            columns=["FITS_Format_Name", "NARA_Risk Level", "File Count", "File %", "Size (MB)", "Size %"])

    # Compares the script output to the expected values.
    compare_dataframes("Format_Subtotals", subtotals, expected)


def test_nara_risk_subtotal():
    """Tests the NARA risk subtotals, which is based on NARA_Risk Level."""

    # Makes a dataframe as input.
    # It contains a subset of the columns that the real dataframe has to simplify testing.
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
    subtotals = subtotal(df, ["NARA_Risk Level"], totals_dict)

    # Makes a dataframe with the expected values.
    # The index values for the dataframes made by subtotal() are column values here so that they
    # are visible in the results from comparing the dataframes as a label of values with errors.
    expected = pd.DataFrame([["Low Risk", 4, 40, 0.066, 81.374],
                             ["Moderate Risk", 1, 10, 0.003, 3.699],
                             ["High Risk", 3, 30, 0.007, 8.631],
                             [np.NaN, 2, 20, 0.005, 6.165]],
                            columns=["NARA_Risk Level", "File Count", "File %", "Size (MB)", "Size %"])

    # Compares the script output to the expected values.
    compare_dataframes("NARA_Risk_Subtotals", subtotals, expected)


def test_technical_appraisal_subtotal():
    """Tests the technical appraisal subtotals, which is based on technical appraisal criteria and FITS_Format_Name."""

    # Makes a dataframe as input.
    # It contains a subset of the columns that the real dataframe has to simplify testing.
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
    subtotals = subtotal(df, ["Criteria", "FITS_Format_Name"], totals_dict)

    # Makes a dataframe with the expected values.
    # The index values for the dataframes made by subtotal() are column values here so that they
    # are visible in the results from comparing the dataframes as a label of values with errors.
    expected = pd.DataFrame([["Format", "DOS/Windows Executable", 2, 25, 0.301, 27.068],
                             ["Format", "PE32 executable", 1, 12.5, 0.300, 26.978],
                             ["Format", "Unknown Binary", 2, 25, 0.05, 4.496],
                             ["Trash", "JPEG EXIF", 2, 25, 0.271, 24.371],
                             ["Trash", "Open Office XML Workbook", 1, 12.5, 0.19, 17.086]],
                            columns=["Criteria", "FITS_Format_Name", "File Count", "File %", "Size (MB)", "Size %"])

    # Compares the script output to the expected values.
    compare_dataframes("Tech_Appraisal_Subtotals", subtotals, expected)


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
test_subtotal_function()
test_format_subtotal()
test_nara_risk_subtotal()
test_technical_appraisal_subtotal()

print("\nThe script is complete.")
