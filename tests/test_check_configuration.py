"""Tests error handling from a missing configuration file, missing variables, and variables with invalid paths."""
# TODO: NOT SURE HOW TO CREATE THESE ERRORS, WITHOUT REWORKING FUNCTION

import unittest


class MyTestCase(unittest.TestCase):
    def test_config_missing_error(self):
        """Test for configuration.py is missing. Verifies the correct error message is made."""
        result = 'TBD'
        expected = '\r\nCould not run the script. Missing the required configuration.py file.' \
                   '\r\nMake a configuration.py file using configuration_template.py and save it to the folder with the script.\r\n'
        self.assertEqual(result, expected, 'Problem with config missing error')

    def test_config_variables_missing_error(self):
        """Test for if all required variables are missing from configuration.py
        Verifies the correct error message is made."""
        # TODO: test each variable separately?
        result = 'TBD'
        expected = '\r\nProblems detected with configuration.py:\r\n' \
                   '   * FITS variable is missing from the configuration file.\r\n' \
                   '   * ITA variable is missing from the configuration file.\r\n' \
                   '   * RISK variable is missing from the configuration file.\r\n' \
                   '   * NARA variable is missing from the configuration file.\r\n\r\n' \
                   'Correct the configuration file, using configuration_template.py as a model.\r\n'
        self.assertEqual(result, expected, 'Problem with config variables missing error')

    def test_config_variables_error(self):
        """Test for if all required variables are for paths that don't exist.
        Verifies the correct error message is made."""
        # TODO: test each variable separately?
        result = 'TBD'
        expected = "\r\nProblems detected with configuration.py:\r\n" \
                   "   * FITS path 'C:/Users/Error/fits.bat' is not correct.\r\n" \
                   "   * ITAfileformats.csv path 'C:/Users/Error/ITAfileformats.csv' is not correct.\r\n" \
                   "   * Riskfileformats.csv path 'C:/Users/Error/Riskfileformats.csv' is not correct.\r\n" \
                   "   * NARA Preservation Action Plans CSV path 'C:/Users/Error/NARA.csv' is not correct.\r\n\r\n" \
                   "Correct the configuration file, using configuration_template.py as a model.\r\n"
        self.assertEqual(result, expected, 'Problem with config variables error')


if __name__ == '__main__':
    unittest.main()
