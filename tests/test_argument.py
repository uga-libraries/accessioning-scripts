"""Tests the code from the main body of the script which provides error handling
for a missing or incorrect script argument, which is the path to the accession folder.

Test for the correct argument is part of test_x_full_script."""

import os
import subprocess
import unittest


class MyTestCase(unittest.TestCase):

    def test_no_argument_error(self):
        """
        Test for running with script without the required argument.
        Result for testing is the error message.
        """
        # Runs the script from the command line and converts the resulting error message to a string.
        script_path = os.path.join('..', 'format_analysis.py')
        script_output = subprocess.run(f'python {script_path}', shell=True, stdout=subprocess.PIPE)
        result = script_output.stdout.decode("utf-8")

        # Creates a string with the expected result.
        expected = '\r\nThe required script argument (accession_folder) is missing.\r\n'

        # Compares the results. assertEqual prints "OK" or the differences between the two strings.
        self.assertEqual(result, expected, 'Problem with no argument')

    def test_path_error(self):
        """
        Trest for running the script with an argument that that isn't a valid path.
        Result for testing is the error message.
        """
        # Runs the script from the command line and converts the resulting error message to a string.
        script_path = os.path.join('..', 'format_analysis.py')
        script_output = subprocess.run(f"python {script_path} C:/User/Wrong/Path", shell=True, stdout=subprocess.PIPE)
        result = script_output.stdout.decode("utf-8")

        # Creates a string with the expected result.
        expected = "\r\nThe provided accession folder 'C:/User/Wrong/Path' is not a valid directory.\r\n"

        # Compares the results. assertEqual prints "OK" or the differences between the two strings.
        self.assertEqual(result, expected, 'Problem with path error')


if __name__ == '__main__':
    unittest.main()
