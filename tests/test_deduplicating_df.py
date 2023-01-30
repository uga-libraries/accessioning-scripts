"""Tests the code from the main body of the script which removes duplicates from the dataframe caused by
multiple possible NARA matches to a single FITS identification."""

import pandas as pd
import unittest


class MyTestCase(unittest.TestCase):
    def test_no_duplicates(self):
        """
        Test for when there are no duplicates to remove.
        Result for testing is the dataframe after duplicates are removed, converted to a list for easier comparison.
        """
        # Creates an abbreviated dataframe (fewer columns) for test input.
        rows = [['C:\\acc\\disk1\\data.csv', 'Comma-Separated Values (CSV)', 'Comma Separated Values', 'csv',
                 'https://www.nationalarchives.gov.uk/pronom/x-fmt/18', 'Low Risk', 'Retain'],
                ['C:\\acc\\disk1\\data.xlsx', 'Open Office XML Workbook', 'Microsoft Excel Office Open XML', 'xlsx',
                 'https://www.nationalarchives.gov.uk/pronom/fmt/214', 'Low Risk', 'Retain'],
                ['C:\\acc\\disk1\\data.xlsx', 'XLSX', 'Microsoft Excel Office Open XML', 'xlsx',
                 'https://www.nationalarchives.gov.uk/pronom/fmt/214', 'Low Risk', 'Retain']]
        column_names = ['FITS_File_Path', 'FITS_Format_Name', 'NARA_Format Name', 'NARA_File Extension(s)',
                        'NARA_PRONOM URL', 'NARA_Risk Level', 'NARA_Proposed Preservation Plan']
        df_results = pd.DataFrame(rows, columns=column_names)

        # Runs the code being tested and converts the resulting dataframe to a list, including the column headers.
        df_results.drop(['NARA_Format Name', 'NARA_File Extension(s)', 'NARA_PRONOM URL'], inplace=True, axis=1)
        df_results.drop_duplicates(inplace=True)
        result = [df_results.columns.to_list()] + df_results.values.tolist()

        # Creates a list with the expected result.
        expected = [['FITS_File_Path', 'FITS_Format_Name', 'NARA_Risk Level', 'NARA_Proposed Preservation Plan'],
                    ['C:\\acc\\disk1\\data.csv', 'Comma-Separated Values (CSV)', 'Low Risk', 'Retain'],
                    ['C:\\acc\\disk1\\data.xlsx', 'Open Office XML Workbook', 'Low Risk', 'Retain'],
                    ['C:\\acc\\disk1\\data.xlsx', 'XLSX', 'Low Risk', 'Retain']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with no duplicates')

    def test_duplicates_same_risk(self):
        """
        Test for when there are duplicates which all have the same NARA risk level.
        Result for testing is the dataframe after duplicates are removed, converted to a list for easier comparison.
        """
        # Creates an abbreviated dataframe (fewer columns) for test input.
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

        # Runs the code being tested and converts the resulting dataframe to a list, including the column headers.
        df_results.drop(['NARA_Format Name', 'NARA_File Extension(s)', 'NARA_PRONOM URL'], inplace=True, axis=1)
        df_results.drop_duplicates(inplace=True)
        result = [df_results.columns.to_list()] + df_results.values.tolist()

        # Creates a list with the expected result.
        expected = [['FITS_File_Path', 'FITS_Format_Name', 'NARA_Risk Level', 'NARA_Proposed Preservation Plan'],
                    ['C:\\acc\\disk1\\empty.txt', 'empty', 'Low Risk', 'Retain']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with duplicates, same risk')
        
    def test_duplicates_diff_risk(self):
        """
        Test for when there are duplicates, some of which have a different NARA risk.
        Result for testing is the dataframe after duplicates are removed, converted to a list for easier comparison.
        """
        # Creates an abbreviated dataframe (fewer columns) for test input.
        rows = [['C:\\acc\\disk1\\file.pdf', 'PDF', 'Portable Document Format (PDF) version 1.7', 'pdf',
                 'https://www.nationalarchives.gov.uk/pronom/fmt/276', 'Moderate Risk', 'Retain'],
                ['C:\\acc\\disk1\\file.pdf', 'PDF', 'Portable Document Format (PDF) version 2.0', 'pdf',
                 'https://www.nationalarchives.gov.uk/pronom/fmt/1129', 'Moderate Risk', 'Retain'],
                ['C:\\acc\\disk1\\file.pdf', 'PDF', 'Portable Document Format/Archiving (PDF/A-1a) accessible', 'pdf',
                 'https://www.nationalarchives.gov.uk/pronom/fmt/95', 'Low Risk', 'Retain']]
        column_names = ['FITS_File_Path', 'FITS_Format_Name', 'NARA_Format Name', 'NARA_File Extension(s)',
                        'NARA_PRONOM URL', 'NARA_Risk Level', 'NARA_Proposed Preservation Plan']
        df_results = pd.DataFrame(rows, columns=column_names)

        # Runs the code being tested and converts the resulting dataframe to a list, including the column headers.
        df_results.drop(['NARA_Format Name', 'NARA_File Extension(s)', 'NARA_PRONOM URL'], inplace=True, axis=1)
        df_results.drop_duplicates(inplace=True)
        result = [df_results.columns.to_list()] + df_results.values.tolist()

        # Creates a list with the expected result.
        expected = [['FITS_File_Path', 'FITS_Format_Name', 'NARA_Risk Level', 'NARA_Proposed Preservation Plan'],
                    ['C:\\acc\\disk1\\file.pdf', 'PDF', 'Moderate Risk', 'Retain'],
                    ['C:\\acc\\disk1\\file.pdf', 'PDF', 'Low Risk', 'Retain']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with duplicates, different risk')


if __name__ == '__main__':
    unittest.main()
