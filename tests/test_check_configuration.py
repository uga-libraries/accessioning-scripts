""" Tests the function check_configuration, which checks for missing or incorrect variables in the configuration file.
These tests only check error handling. Correct config file is covered by test_x_full_script.py"""

import os
import subprocess
import unittest


class MyTestCase(unittest.TestCase):

    def setUp(self):
        """
        Renames the correct configuration.py file, so it can be restored after the test.
        Makes an accession folder, fake FITS and NARA files, and variables used in the tests.
        """
        # Renames the configuration.py with the correct values as a way to save them.
        # The tests have to use a file named configuration.py.
        os.rename(os.path.join('..', 'configuration.py'), os.path.join('..', 'configuration_correct.py'))

        # Makes an empty folder to use an as the accession directory, which is needed for the script to run.
        # Since the script will give an error for the configuration.py file before it runs, no test files are needed.
        os.mkdir('test_accession')

        # Makes fake FITS and NARA files to use for testing if the paths in the configuration.py file exist.
        # The test is based on the filename, so they don't have to be the real files for the test to pass.
        with open('fits.bat', 'w') as file:
            file.write('Test FITS')
        with open('NARA_PreservationActionPlan_FileFormats.csv', 'w') as file:
            file.write("Test NARA")

        # Makes variables for paths used in most or all tests.
        self.config_path = os.path.join('..', 'configuration.py')
        self.script_path = os.path.join('..', 'format_analysis.py')
        self.ita_path = os.path.join(os.path.dirname(os.getcwd()), 'ITAfileformats.csv')
        self.risk_path = os.path.join(os.path.dirname(os.getcwd()), 'Riskfileformats.csv')

    def tearDown(self):
        """
        Renames configuration_correct.py back to configuration.py, so the script is ready to work correctly.
        Deletes the test accession folder and fake FITS and NARA files.
        """
        if os.path.exists(os.path.join('..', 'configuration.py')):
            os.remove(os.path.join('..', 'configuration.py'))
        os.rename(os.path.join('..', 'configuration_correct.py'), os.path.join('..', 'configuration.py'))
        os.rmdir('test_accession')
        os.remove('fits.bat')
        os.remove('NARA_PreservationActionPlan_FileFormats.csv')

    def test_no_config(self):
        """
        Tests error handling for when there is no configuration.py file.
        Result for testing is the error message returned by the function.
        """
        # Runs the script, without having made the required configuration.py file.
        result = subprocess.run(f'python {self.script_path} test_accession', shell=True, stdout=subprocess.PIPE)

        # Creates a string with the expected result.
        expected = '\r\nCould not run the script. Missing the required configuration.py file.\r\n' \
                   'Make a configuration.py file using configuration_template.py and save it to the folder with the script.\r\n' \

        # Compares the results, which includes converting result to a string.
        # assertEqual prints "OK" or the differences between the two strings.
        self.assertEqual(result.stdout.decode('utf-8'), expected, 'Problem with no configuration.py')

    def test_no_fits(self):
        """
        Tests error handling for when configuration.py file does not have the required FITS variable.
        Result for testing is the error message returned by the function.
        """
        # Makes a configuration.py with the required variables (with correct values),
        # except FITS is missing.
        with open(os.path.join('..', 'configuration.py'), 'a') as file:
            file.write(f'ITA = r"{self.ita_path}"')
            file.write(f'\nRISK = r"{self.risk_path}"')
            file.write('\nNARA = r"NARA_PreservationActionPlan_FileFormats.csv"')

        # Runs the script.
        result = subprocess.run(f'python {self.script_path} test_accession', shell=True, stdout=subprocess.PIPE)

        # Creates a string with the expected result.
        expected = '\r\nProblems detected with configuration.py:\r\n' \
                   '   * FITS variable is missing from the configuration file.\r\n' \
                   '\r\nCorrect the configuration file, using configuration_template.py as a model.\r\n'

        # Compares the results, which includes converting result to a string.
        # assertEqual prints "OK" or the differences between the two strings.
        self.assertEqual(result.stdout.decode('utf-8'), expected, 'Problem with no FITS')

    def test_no_ita(self):
        """
        Tests error handling for when configuration.py file does not have the required ITA variable.
        Result for testing is the error message returned by the function.
        """
        # Makes a configuration.py with the required variables (with correct values),
        # except ITA is missing.
        with open(os.path.join('..', 'configuration.py'), 'a') as file:
            file.write(f'FITS = r"fits.bat"')
            file.write(f'\nRISK = r"{self.risk_path}"')
            file.write('\nNARA = r"NARA_PreservationActionPlan_FileFormats.csv"')

        # Runs the script.
        result = subprocess.run(f'python {self.script_path} test_accession', shell=True, stdout=subprocess.PIPE)

        # Creates a string with the expected result.
        expected = '\r\nProblems detected with configuration.py:\r\n' \
                   '   * ITA variable is missing from the configuration file.\r\n' \
                   '\r\nCorrect the configuration file, using configuration_template.py as a model.\r\n'

        # Compares the results, which includes converting result to a string.
        # assertEqual prints "OK" or the differences between the two strings.
        self.assertEqual(result.stdout.decode('utf-8'), expected, 'Problem with no ITA')

    def test_no_risk(self):
        """
        Tests error handling for when configuration.py file does not have the required RISK variable.
        Result for testing is the error message returned by the function.
        """
        # Makes a configuration.py with the required variables (with correct values),
        # except RISK is missing.
        with open(os.path.join('..', 'configuration.py'), 'a') as file:
            file.write(f'FITS = r"fits.bat"')
            file.write(f'\nITA = r"{self.ita_path}"')
            file.write('\nNARA = r"NARA_PreservationActionPlan_FileFormats.csv"')

        # Runs the script.
        result = subprocess.run(f'python {self.script_path} test_accession', shell=True, stdout=subprocess.PIPE)

        # Creates a string with the expected result.
        expected = '\r\nProblems detected with configuration.py:\r\n' \
                   '   * RISK variable is missing from the configuration file.\r\n' \
                   '\r\nCorrect the configuration file, using configuration_template.py as a model.\r\n'

        # Compares the results, which includes converting result to a string.
        # assertEqual prints "OK" or the differences between the two strings.
        self.assertEqual(result.stdout.decode('utf-8'), expected, 'Problem with no RISK')

    def test_no_nara(self):
        """
        Tests error handling for when configuration.py file does not have the required NARA variable.
        Result for testing is the error message returned by the function.
        """
        # Makes a configuration.py with the required variables (with correct values),
        # except NARA is missing.
        with open(os.path.join('..', 'configuration.py'), 'a') as file:
            file.write('FITS = r"fits.bat"')
            file.write(f'\nITA = r"{self.ita_path}"')
            file.write(f'\nRISK = r"{self.risk_path}"')

        # Runs the script.
        result = subprocess.run(f'python {self.script_path} test_accession', shell=True, stdout=subprocess.PIPE)

        # Creates a string with the expected result.
        expected = '\r\nProblems detected with configuration.py:\r\n' \
                   '   * NARA variable is missing from the configuration file.\r\n' \
                   '\r\nCorrect the configuration file, using configuration_template.py as a model.\r\n'

        # Compares the results, which includes converting result to a string.
        # assertEqual prints "OK" or the differences between the two strings.
        self.assertEqual(result.stdout.decode('utf-8'), expected, 'Problem with no NARA')

    def test_fits_path_error(self):
        """
        Tests error handling for when the configuration.py file FITS variable value is a path that doesn't exist.
        Result for testing is the error message returned by the function.
        """
        # Makes a configuration.py with the required variables (with correct values),
        # except the FITS path is not correct.
        with open(os.path.join('..', 'configuration.py'), 'a') as file:
            file.write(f'FITS = r"{os.path.join("Error", "fits.bat")}"')
            file.write(f'\nITA = r"{self.ita_path}"')
            file.write(f'\nRISK = r"{self.risk_path}"')
            file.write('\nNARA = r"NARA_PreservationActionPlan_FileFormats.csv"')

        # Runs the script.
        result = subprocess.run(f'python {self.script_path} test_accession', shell=True, stdout=subprocess.PIPE)

        # Creates a string with the expected result.
        expected = "\r\nProblems detected with configuration.py:\r\n" \
                   "   * FITS path 'Error\\fits.bat' is not correct.\r\n" \
                   "\r\nCorrect the configuration file, using configuration_template.py as a model.\r\n"

        # Compares the results, which includes converting result to a string.
        # assertEqual prints "OK" or the differences between the two strings.
        self.assertEqual(result.stdout.decode('utf-8'), expected, 'Problem with FITS path error')

    def test_ita_path_error(self):
        """
        Tests error handling for when the configuration.py file ITA variable value is a path that doesn't exist.
        Result for testing is the error message returned by the function.
        """
        # Makes a configuration.py with the required variables (with correct values),
        # except the ITA path is not correct.
        with open(os.path.join('..', 'configuration.py'), 'a') as file:
            file.write('FITS = r"fits.bat"')
            file.write(f'\nITA = r"{os.path.join("Error", "ITAfileformats.csv")}"')
            file.write(f'\nRISK = r"{self.risk_path}"')
            file.write('\nNARA = r"NARA_PreservationActionPlan_FileFormats.csv"')

        # Runs the script.
        result = subprocess.run(f'python {self.script_path} test_accession', shell=True, stdout=subprocess.PIPE)

        # Creates a string with the expected result.
        expected = "\r\nProblems detected with configuration.py:\r\n" \
                   "   * ITAfileformats.csv path 'Error\\ITAfileformats.csv' is not correct.\r\n" \
                   "\r\nCorrect the configuration file, using configuration_template.py as a model.\r\n"

        # Compares the results, which includes converting result to a string.
        # assertEqual prints "OK" or the differences between the two strings.
        self.assertEqual(result.stdout.decode('utf-8'), expected, 'Problem with ITA path error')

    def test_risk_path_error(self):
        """
        Tests error handling for when the configuration.py file RISK variable value is a path that doesn't exist.
        Result for testing is the error message returned by the function.
        """
        # Makes a configuration.py with the required variables (with correct values),
        # except the RISK path is not correct.
        with open(os.path.join('..', 'configuration.py'), 'a') as file:
            file.write('FITS = r"fits.bat"')
            file.write(f'\nITA = r"{self.ita_path}"')
            file.write(f'\nRISK = r"{os.path.join("Error", "Riskfileformats.csv")}"')
            file.write('\nNARA = r"NARA_PreservationActionPlan_FileFormats.csv"')

        # Runs the script.
        result = subprocess.run(f'python {self.script_path} test_accession', shell=True, stdout=subprocess.PIPE)

        # Creates a string with the expected result.
        expected = "\r\nProblems detected with configuration.py:\r\n" \
                   "   * Riskfileformats.csv path 'Error\\Riskfileformats.csv' is not correct.\r\n" \
                   "\r\nCorrect the configuration file, using configuration_template.py as a model.\r\n"

        # Compares the results, which includes converting result to a string.
        # assertEqual prints "OK" or the differences between the two strings.
        self.assertEqual(result.stdout.decode('utf-8'), expected, 'Problem with RISK path error')

    def test_nara_path_error(self):
        """
        Tests error handling for when the configuration.py file NARA variable value is a path that doesn't exist.
        Result for testing is the error message returned by the function.
        """
        # Makes a configuration.py with the required variables (with correct values),
        # except the NARA path is not correct.
        with open(os.path.join('..', 'configuration.py'), 'a') as file:
            file.write('FITS = r"fits.bat"')
            file.write(f'\nITA = r"{self.ita_path}"')
            file.write(f'\nRISK = r"{self.risk_path}"')
            file.write(f'\nNARA = r"{os.path.join("Error", "NARA_PreservationActionPlan_FileFormats.csv")}"')

        # Runs the script.
        result = subprocess.run(f'python {self.script_path} test_accession', shell=True, stdout=subprocess.PIPE)

        # Creates a string with the expected result.
        expected = "\r\nProblems detected with configuration.py:\r\n" \
                   "   * NARA Preservation Action Plans CSV path 'Error\\NARA_PreservationActionPlan_FileFormats.csv' is not correct.\r\n" \
                   "\r\nCorrect the configuration file, using configuration_template.py as a model.\r\n"

        # Compares the results, which includes converting result to a string.
        # assertEqual prints "OK" or the differences between the two strings.
        self.assertEqual(result.stdout.decode('utf-8'), expected, 'Problem with NARA path error')


if __name__ == '__main__':
    unittest.main()
