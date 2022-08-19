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
    print("\nResults from testing the subtotal() function.")
    compare_dataframes("One_Criteria", one, one_expected)
    compare_dataframes("Two_Criteria", two, two_expected)


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

print("\nThe script is complete.")
