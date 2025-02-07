"""Tests the function make_fits_csv, which reads the FITS XML in an accession folder and
saves the data to a CSV, with error handling for encoding errors.

For test input, uses FITS XML saved in the script repository tests folder."""

import csv
import os
import unittest
from format_analysis_functions import make_fits_csv


class MyTestCase(unittest.TestCase):

    def tearDown(self):
        """
        Deletes the CSVs and encode error logs created by the different tests, if present.
        """
        filenames = ('csv_multi_id_fits.csv', 'csv_multi_id_encoding_fits.csv',
                     'csv_multi_id_encoding_encode_errors.txt', 'csv_one_file_fits.csv',
                     'csv_one_id_fits.csv', 'csv_one_id_encoding_fits.csv',
                     'csv_one_id_encoding_encode_errors.txt')

        for name in filenames:
            if os.path.exists(name):
                os.remove(name)

    def test_multiple_ids(self):
        """
        Test for FITS XML where all have multiple format identifications.
        Result for testing is the contents of the CSV created by the function.
        """
        # Creates variables for the test input (in the repo) and runs the function being tested.
        fits_output = os.path.join('test_FITS', 'csv_multi_id_FITS')
        collection_folder = os.getcwd()
        accession_number = 'csv_multi_id'
        make_fits_csv(fits_output, collection_folder, accession_number)

        # Reads the CSV created by the function into a list.
        result = []
        with open('csv_multi_id_fits.csv', 'r') as file:
            file_read = csv.reader(file)
            for row in file_read:
                result.append(row)

        # Creates a list with the expected result.
        expected = [['FITS_File_Path', 'FITS_Format_Name', 'FITS_Format_Version', 'FITS_PUID',
                     'FITS_Identifying_Tool(s)', 'FITS_Multiple_IDs', 'FITS_Date_Last_Modified', 'FITS_Size_KB',
                     'FITS_MD5', 'FITS_Creating_Application', 'FITS_Valid', 'FITS_Well-Formed', 'FITS_Status_Message'],
                    ['C:\\csv_multi_id\\disk2\\backup.gz', 'GZIP Format', '',
                     'https://www.nationalarchives.gov.uk/PRONOM/x-fmt/266', 'Droid version 6.4; Tika version 1.21',
                     'True', '2022-12-14', '1.993', '6749b0ec1fbc96faab1a1f98dd7b8a74', '', '', '', ''],
                    ['C:\\csv_multi_id\\disk2\\backup.gz', 'ZIP Format', '', '',
                     'file utility version 5.03; Exiftool version 11.54; ffident version 0.2',
                     'True', '2022-12-14', '1.993', '6749b0ec1fbc96faab1a1f98dd7b8a74', '', '', '', ''],
                    ['C:\\csv_multi_id\\disk1\\spreadsheet.xlsx', 'ZIP Format', '2.0',
                     'https://www.nationalarchives.gov.uk/PRONOM/x-fmt/263',
                     'Droid version 6.4; file utility version 5.03; ffident version 0.2', 'True',
                     '2022-12-14', '20.56', 'db4c3079e3805469c1b47c4864234e66', 'Microsoft Excel',
                     '', '', ''],
                    ['C:\\csv_multi_id\\disk1\\spreadsheet.xlsx', 'XLSX', '', '', 'Exiftool version 11.54', 'True',
                     '2022-12-14', '20.56', 'db4c3079e3805469c1b47c4864234e66', 'Microsoft Excel',
                     '', '', ''],
                    ['C:\\csv_multi_id\\disk1\\spreadsheet.xlsx', 'Office Open XML Workbook', '', '',
                     'Tika version 1.21', 'True', '2022-12-14', '20.56', 'db4c3079e3805469c1b47c4864234e66',
                     'Microsoft Excel', '', '', '']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with multiple ids')

    def test_multiple_ids_encoding(self):
        """
        Test for FITS XML where all have multiple format identifications
        and two (the spreadsheets) of the three have a special character (pi) that cause encoding errors.
        Results for testing are the contents of the CSV and error log created by the function.
        """
        # Creates variables for the test input (in the repo) and runs the function being tested.
        fits_output = os.path.join('test_FITS', 'csv_multi_id_encoding_FITS')
        collection_folder = os.getcwd()
        accession_number = 'csv_multi_id_encoding'
        make_fits_csv(fits_output, collection_folder, accession_number)

        # Reads the CSV created by the function into a list.
        result_csv = []
        with open('csv_multi_id_encoding_fits.csv', 'r') as file:
            file_read = csv.reader(file)
            for row in file_read:
                result_csv.append(row)

        # Creates a list with the expected result for the CSV.
        expected_csv = [['FITS_File_Path', 'FITS_Format_Name', 'FITS_Format_Version', 'FITS_PUID',
                         'FITS_Identifying_Tool(s)', 'FITS_Multiple_IDs', 'FITS_Date_Last_Modified', 'FITS_Size_KB',
                         'FITS_MD5', 'FITS_Creating_Application', 'FITS_Valid', 'FITS_Well-Formed', 'FITS_Status_Message'],
                        ['C:\\csv_multi_id_encoding\\disk2\\backup.gz', 'GZIP Format', '',
                         'https://www.nationalarchives.gov.uk/PRONOM/x-fmt/266', 'Droid version 6.4; Tika version 1.21',
                         'True', '2022-12-14', '1.993', '6749b0ec1fbc96faab1a1f98dd7b8a74', '', '', '', ''],
                        ['C:\\csv_multi_id_encoding\\disk2\\backup.gz', 'ZIP Format', '', '',
                         'file utility version 5.03; Exiftool version 11.54; ffident version 0.2',
                         'True', '2022-12-14', '1.993', '6749b0ec1fbc96faab1a1f98dd7b8a74', '', '', '', '']]

        # Reads the log created by the function into a list.
        with open('csv_multi_id_encoding_encode_errors.txt', 'r') as file:
            result_log = file.readlines()

        # Creates a list with the expected result for the log.
        expected_log = ['C:\\csv_multi_id_encoding\\diskÏ€\\data1.xlsx\n',
                        'C:\\csv_multi_id_encoding\\diskÏ€\\data2.xlsx\n']

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result_csv, expected_csv, 'Problem with multiple ids, encoding errors - csv')
        self.assertEqual(result_log, expected_log, 'Problem with multiple ids, encoding errors - log')

    def test_one_file(self):
        """
        Test for an accession with only one FITS XML.
        Result for testing is the contents of the CSV created by the function.
        """
        # Creates variables for the test input (in the repo) and runs the function being tested.
        fits_output = os.path.join('test_FITS', 'csv_one_file_FITS')
        collection_folder = os.getcwd()
        accession_number = 'csv_one_file'
        make_fits_csv(fits_output, collection_folder, accession_number)

        # Reads the CSV created by the function into a list.
        result = []
        with open('csv_one_file_fits.csv', 'r') as file:
            file_read = csv.reader(file)
            for row in file_read:
                result.append(row)

        # Creates a list with the expected result.
        expected = [['FITS_File_Path', 'FITS_Format_Name', 'FITS_Format_Version', 'FITS_PUID',
                     'FITS_Identifying_Tool(s)', 'FITS_Multiple_IDs', 'FITS_Date_Last_Modified', 'FITS_Size_KB',
                     'FITS_MD5', 'FITS_Creating_Application', 'FITS_Valid', 'FITS_Well-Formed', 'FITS_Status_Message'],
                    ['C:\\csv_one_file\\disk2\\web.html', 'Extensible Markup Language', '1.0', '',
                     'Jhove version 1.20.1', 'False', '2022-12-14', '0.001', 'e080b3394eaeba6b118ed15453e49a34', '',
                     'true', 'true', 'Not able to determine type of end of line severity=info']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with one file')

    def test_one_id(self):
        """
        Test for FITS XML where all have one format identification.
        Result for testing is the contents of the CSV created by the function.
        """
        # Creates variables for the test input (in the repo) and runs the function being tested.
        fits_output = os.path.join('test_FITS', 'csv_one_id_FITS')
        collection_folder = os.getcwd()
        accession_number = 'csv_one_id'
        make_fits_csv(fits_output, collection_folder, accession_number)

        # Reads the CSV created by the function into a list.
        result = []
        with open('csv_one_id_fits.csv', 'r') as file:
            file_read = csv.reader(file)
            for row in file_read:
                result.append(row)

        # Creates a list with the expected result.
        expected = [['FITS_File_Path', 'FITS_Format_Name', 'FITS_Format_Version', 'FITS_PUID',
                     'FITS_Identifying_Tool(s)', 'FITS_Multiple_IDs', 'FITS_Date_Last_Modified', 'FITS_Size_KB',
                     'FITS_MD5', 'FITS_Creating_Application', 'FITS_Valid', 'FITS_Well-Formed', 'FITS_Status_Message'],
                    ['C:\\csv_one_id\\disk1\\file.txt', 'Plain text', '',
                     'https://www.nationalarchives.gov.uk/PRONOM/x-fmt/111',
                     'Droid version 6.4; Jhove version 1.20.1; file utility version 5.03', 'False',
                     '2022-12-14', '2.0', '7b71af3fdf4a2f72a378e3e77815e497', '', 'true', 'true', ''],
                    ['C:\\csv_one_id\\disk1\\spreadsheet1.csv', 'Comma-Separated Values (CSV)', '',
                     'https://www.nationalarchives.gov.uk/PRONOM/x-fmt/18', 'Droid version 6.4', 'False',
                     '2022-12-14', '6002.01', 'f95a4c954014342e4bf03f51fcefaecd', '', '', '', ''],
                    ['C:\\csv_one_id\\disk1\\spreadsheet2.csv', 'Comma-Separated Values (CSV)', '',
                     'https://www.nationalarchives.gov.uk/PRONOM/x-fmt/18',
                     'Droid version 6.4', 'False', '2022-12-14', '4.404', 'd5e857a4bd33d2b5a2f96b78ccffe1f3',
                     '', '', '', '']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with one id')

    def test_one_id_encoding(self):
        """
        Test for FITS XML where all have one format identification
        and two (the text files) of the three have a special character (pi) that cause encoding errors.
        Results for testing are the contents of the CSV and error log created by the function.
        """
        # Creates variables for the test input (in the repo) and runs the function being tested.
        fits_output = os.path.join('test_FITS', 'csv_one_id_encoding_FITS')
        collection_folder = os.getcwd()
        accession_number = 'csv_one_id_encoding'
        make_fits_csv(fits_output, collection_folder, accession_number)

        # Reads the CSV created by the function into a list.
        result_csv = []
        with open('csv_one_id_encoding_fits.csv', 'r') as file:
            file_read = csv.reader(file)
            for row in file_read:
                result_csv.append(row)

        # Creates a list with the expected result for the CSV.
        expected_csv = [['FITS_File_Path', 'FITS_Format_Name', 'FITS_Format_Version', 'FITS_PUID',
                         'FITS_Identifying_Tool(s)', 'FITS_Multiple_IDs', 'FITS_Date_Last_Modified', 'FITS_Size_KB',
                         'FITS_MD5', 'FITS_Creating_Application', 'FITS_Valid', 'FITS_Well-Formed', 'FITS_Status_Message'],
                        ['C:\\csv_one_id_encoding\\disk1\\spreadsheet1.csv', 'Comma-Separated Values (CSV)', '',
                         'https://www.nationalarchives.gov.uk/PRONOM/x-fmt/18', 'Droid version 6.4', 'False',
                         '2022-12-14', '6002.01', 'f95a4c954014342e4bf03f51fcefaecd', '', '', '', '']]

        # Reads the log created by the function into a list.
        with open('csv_one_id_encoding_encode_errors.txt', 'r') as file:
            result_log = file.readlines()

        # Creates a list with the expected result for the log.
        expected_log = ['C:\\csv_one_id_encoding\\diskÏ€\\file.txt\n',
                        'C:\\csv_one_id_encoding\\diskÏ€\\file2.txt\n']

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result_csv, expected_csv, 'Problem with one id, encoding errors - csv')
        self.assertEqual(result_log, expected_log, 'Problem with one id, encoding errors - log')


if __name__ == '__main__':
    unittest.main()
