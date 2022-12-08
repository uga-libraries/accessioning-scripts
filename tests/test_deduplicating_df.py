"""Tests code from the main body of the script that removes duplicates from the dataframe caused by
multiple possible NARA matches to a single FITS identification.

Manually sync the code in the test with any changes in the main script."""

import pandas as pd
import unittest


class MyTestCase(unittest.TestCase):
    def test_no_duplicates(self):
        """
        Test for when there are no duplicates.
        Result for testing is the dataframe after duplicates are removed, converted to a list for easier comparison.
        """

        # Makes a dataframe to use as input, with a subset of the columns usually in df_results.
        rows = [['C:\\acc\\disk1\\data.csv', 'Comma-Separated Values (CSV)', 'Comma Separated Values', 'csv',
                 'https://www.nationalarchives.gov.uk/pronom/x-fmt/18', 'Low Risk', 'Retain'],
                ['C:\\acc\\disk1\\data.xlsx', 'Open Office XML Workbook', 'Microsoft Excel Office Open XML', 'xlsx',
                 'https://www.nationalarchives.gov.uk/pronom/fmt/214', 'Low Risk', 'Retain'],
                ['C:\\acc\\disk1\\data.xlsx', 'XLSX', 'Microsoft Excel Office Open XML', 'xlsx',
                 'https://www.nationalarchives.gov.uk/pronom/fmt/214', 'Low Risk', 'Retain']]
        column_names = ['FITS_File_Path', 'FITS_Format_Name', 'NARA_Format Name', 'NARA_File Extension(s)',
                        'NARA_PRONOM URL', 'NARA_Risk Level', 'NARA_Proposed Preservation Plan']
        df_results = pd.DataFrame(rows, columns=column_names)

        # Runs the code being tested.
        # Removes columns with NARA identification info and then removes duplicate rows.
        df_results.drop(['NARA_Format Name', 'NARA_File Extension(s)', 'NARA_PRONOM URL'], inplace=True, axis=1)
        df_results.drop_duplicates(inplace=True)

        # Makes lists of the actual results from the test and the expected results.
        results = df_results.values.tolist()
        expected = [['C:\\acc\\disk1\\data.csv', 'Comma-Separated Values (CSV)', 'Low Risk', 'Retain'],
                    ['C:\\acc\\disk1\\data.xlsx', 'Open Office XML Workbook', 'Low Risk', 'Retain'],
                    ['C:\\acc\\disk1\\data.xlsx', 'XLSX', 'Low Risk', 'Retain']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(results, expected, 'Problem with no risk')

    def test_duplicates_same_risk(self):
        """
        Test for when there are duplicates which all have the same NARA risk level.
        Result for testing is the dataframe after duplicates are removed, converted to a list for easier comparison.
        """

        # Makes a dataframe to use as input, with a subset of the columns usually in df_results.
        rows = [['C:\\acc\\disk1\\empty.txt', 'empty', 'ASCII 7-bit Text', 'txt|asc|csv|tab',
                 'https://www.nationalarchives.gov.uk/pronom/x-fmt/22', 'Low Risk', 'Retain'],
                ['C:\\acc\\disk1\\empty.txt', 'empty', 'ASCII 8-bit Text', 'txt|asc|csv|tab',
                 'https://www.nationalarchives.gov.uk/pronom/x-fmt/283', 'Low Risk', 'Retain'],
                ['C:\\acc\\disk1\\empty.txt', 'empty', 'JSON', 'json|txt',
                 'https://www.nationalarchives.gov.uk/pronom/fmt/817', 'Low Risk', 'Retain'],
                ['C:\\acc\\disk1\\empty.txt', 'empty', 'Plain Text', 'Plain_Text|txt|text|asc|rte',
                 'https://www.nationalarchives.gov.uk/pronom/x-fmt/111', 'Low Risk', 'Retain']]
        column_names = ['FITS_File_Path', 'FITS_Format_Name', 'NARA_Format Name', 'NARA_File Extension(s)',
                        'NARA_PRONOM URL', 'NARA_Risk Level', 'NARA_Proposed Preservation Plan']
        df_results = pd.DataFrame(rows, columns=column_names)

        # Runs the code being tested.
        # Removes columns with NARA identification info and then removes duplicate rows.
        df_results.drop(['NARA_Format Name', 'NARA_File Extension(s)', 'NARA_PRONOM URL'], inplace=True, axis=1)
        df_results.drop_duplicates(inplace=True)

        # Makes lists of the actual results from the test and the expected results.
        results = df_results.values.tolist()
        expected = [['C:\\acc\\disk1\\empty.txt', 'empty', 'Low Risk', 'Retain']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(results, expected, 'Problem with duplicates, same risk')
        
    def test_duplicates_diff_risk(self):
        """
        Test for when there are duplicates, some of which have a different NARA risk.
        Result for testing is the dataframe after duplicates are removed, converted to a list for easier comparison.
        """

        # Makes a dataframe to use as input, with a subset of the columns usually in df_results.
        rows = [['C:\\acc\\disk1\\file.pdf', 'PDF', 'Portable Document Format (PDF) version 1.7', 'pdf',
                 'https://www.nationalarchives.gov.uk/pronom/fmt/276', 'Moderate Risk', 'Retain'],
                ['C:\\acc\\disk1\\file.pdf', 'PDF', 'Portable Document Format (PDF) version 2.0', 'pdf',
                 'https://www.nationalarchives.gov.uk/pronom/fmt/1129', 'Moderate Risk', 'Retain'],
                ['C:\\acc\\disk1\\file.pdf', 'PDF', 'Portable Document Format/Archiving (PDF/A-1a) accessible', 'pdf',
                 'https://www.nationalarchives.gov.uk/pronom/fmt/95', 'Low Risk', 'Retain']]
        column_names = ['FITS_File_Path', 'FITS_Format_Name', 'NARA_Format Name', 'NARA_File Extension(s)',
                        'NARA_PRONOM URL', 'NARA_Risk Level', 'NARA_Proposed Preservation Plan']
        df_results = pd.DataFrame(rows, columns=column_names)

        # Runs the code being tested.
        # Removes columns with NARA identification info and then removes duplicate rows.
        df_results.drop(['NARA_Format Name', 'NARA_File Extension(s)', 'NARA_PRONOM URL'], inplace=True, axis=1)
        df_results.drop_duplicates(inplace=True)

        # Makes lists of the actual results from the test and the expected results.
        results = df_results.values.tolist()
        expected = [['C:\\acc\\disk1\\file.pdf', 'PDF', 'Moderate Risk', 'Retain'],
                    ['C:\\acc\\disk1\\file.pdf', 'PDF', 'Low Risk', 'Retain']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(results, expected, 'Problem with duplicates, different risk')


if __name__ == '__main__':
    unittest.main()
