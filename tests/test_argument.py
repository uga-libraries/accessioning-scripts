"""Tests the function argument, which checks for a missing or incorrect script argument (accession folder).

Note: the function will print messages about the errors if it works correctly."""

import os
import unittest
from format_analysis_functions import argument


class MyTestCase(unittest.TestCase):

    def test_argument_correct(self):
        """
        Test for correctly providing the required argument, which is a valid path.
        Result for testing is the string returned by the function.
        """
        # Creates a list of arguments to simulate the contents of sys.argv when running the script.
        # The first list item is the script path and the second is the accession folder (what the function tests).
        arguments = [os.path.join('..', 'format_analysis.py'), os.getcwd()]

        # Runs the function being tested.
        result = argument(arguments)

        # Compares the results to what was expected.
        # assertEqual prints "OK" or the differences between the two strings.
        self.assertEqual(result, os.getcwd(), 'Problem with argument correct')

    def test_error_no_argument(self):
        """
        Test for not including the required argument.
        Result for testing is the value (False) returned by the function.
        """
        # Creates a list of arguments to simulate the contents of sys.argv when running the script.
        # It only contains the script path.
        arguments = [os.path.join('..', 'format_analysis.py')]

        # Runs the function being tested.
        result = argument(arguments)

        # Compares the results to what was expected.
        # assertEqual prints "OK" or the differences between the two strings.
        self.assertEqual(result, False, 'Problem with error - no argument')

    def test_error_path(self):
        """
        Test for running the script with an argument that that isn't a valid path.
        Result for testing is the error message.
        """
        # Creates a list of arguments to simulate the contents of sys.argv when running the script.
        # The first list item is the script path and the second is the accession folder (what the function tests).
        arguments = [os.path.join('..', 'format_analysis.py'), os.path.join(os.getcwd(), 'MISSING_FOLDER')]

        # Runs the function being tested.
        result = argument(arguments)

        # Compares the results to what was expected.
        # assertEqual prints "OK" or the differences between the two strings.
        self.assertEqual(result, False, 'Problem with error - path')


if __name__ == '__main__':
    unittest.main()
