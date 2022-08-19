"""Purpose: tests for each function and analysis component in the format-analysis.py script.
Each test produces input, runs the code, and compares it to the expected output.
Test results are saved to a directory specified with the script argument.
Comment out any test you do not wish to run.

For any tests that do not import the function from format-analysis.py, sync the code before running the test.
If the input for any function or analysis changes, edit the test input and expected results."""

# usage: python path/format-analysis-tests.py output_folder

import os
import sys

# Makes the output directory (the only script argument) the current directory for easier saving.
# If the argument is missing or not a valid directory, ends the script.
try:
    output = sys.argv[1]
    os.chdir(output)
except (IndexError, FileNotFoundError):
    print("\nThe required script argument (output folder) is missing or incorrect.")
    sys.exit()

# Calls each of the test functions, which either test a function in format-analysis.py or
# one of the analysis components, such as a particular subtotal or subset.
# A summary of the test result is printed to the terminal and details saved to the output folder.

print("\nThe script is complete.")
