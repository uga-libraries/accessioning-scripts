"""Tests the function media_subtotal, which gets summary information for each piece of media."""

import pandas as pd
import unittest
from format_analysis_functions import media_subtotal


class MyTestCase(unittest.TestCase):

    def setUp(self):
        """
        Accession folder variable used for all of the tests.
        """
        self.accession_folder = 'C:\\ACC'

    def test_ta(self):
        """
        Test for technical appraisal subtotal with some files that require technical appraisal ('Format').
        Result for testing is the media subtotal dataframe, converted to a list for easier comparison.
        """
        # Makes a dataframe to use as test input and runs the function being tested.
        rows = [['C:\\ACC\\Disk1\\file1.txt', 1000, 'Low Risk', 'Not for TA', 'Not for Other'],
                ['C:\\ACC\\Disk1\\file2.txt', 2000, 'Low Risk', 'Not for TA', 'Not for Other'],
                ['C:\\ACC\\Disk1\\command1.bat', 3000, 'Moderate Risk', 'Format', 'Not for Other'],
                ['C:\\ACC\\Disk2\\command2.bat', 4000, 'Moderate Risk', 'Format', 'Not for Other'],
                ['C:\\ACC\\Disk2\\command3.bat', 5000, 'Moderate Risk', 'Format', 'Not for Other']]
        column_names = ['FITS_File_Path', 'FITS_Size_KB', 'NARA_Risk Level', 'Technical_Appraisal', 'Other_Risk']
        df_results = pd.DataFrame(rows, columns=column_names)
        df_media_subtotal = media_subtotal(df_results, self.accession_folder)

        # Makes lists of the actual results from the test and the expected results.
        # Uses reset_index() to include the index value in the dataframe, which is the media name.
        results = df_media_subtotal.reset_index().values.tolist()
        expected = [['Disk1', 3, 6, 0, 1, 2, 0, 1, 0],
                    ['Disk2', 2, 9, 0, 2, 0, 0, 2, 0]]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(results, expected, 'Problem with technical appraisal, Format and Not for TA')

    def test_ta_trash(self):
        """
        Test for technical appraisal subtotal with some files categorized as 'Trash',
        a category which is skipped by the subtotal.
        Result for testing is the media subtotal dataframe, converted to a list for easier comparison.
        """
        # Makes a dataframe to use as test input and runs the function being tested.
        rows = [['C:\\ACC\\Disk1\\file1.txt', 1000, 'Low Risk', 'Trash', 'Not for Other'],
                ['C:\\ACC\\Disk1\\file2.txt', 2000, 'Low Risk', 'Trash', 'Not for Other'],
                ['C:\\ACC\\Disk1\\file3.txt', 3000, 'Low Risk', 'Not for TA', 'Not for Other'],
                ['C:\\ACC\\Disk2\\file4.txt', 4000, 'Low Risk', 'Trash', 'Not for Other'],
                ['C:\\ACC\\Disk2\\file5.txt', 5000, 'Low Risk', 'Not for TA', 'Not for Other']]
        column_names = ['FITS_File_Path', 'FITS_Size_KB', 'NARA_Risk Level', 'Technical_Appraisal', 'Other_Risk']
        df_results = pd.DataFrame(rows, columns=column_names)
        df_media_subtotal = media_subtotal(df_results, self.accession_folder)

        # Makes lists of the actual results from the test and the expected results.
        # Uses reset_index() to include the index value in the dataframe, which is the media name.
        results = df_media_subtotal.reset_index().values.tolist()
        expected = [['Disk1', 3, 6, 0, 0, 3, 0, 0, 0],
                    ['Disk2', 2, 9, 0, 0, 2, 0, 0, 0]]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(results, expected, 'Problem with technical appraisal, Trash and Not for TA')

    def test_ta_none(self):
        """
        Test for technical appraisal subtotal when all are 'Not for TA'.
        Result for testing is the media subtotal dataframe, converted to a list for easier comparison.
        """
        # Makes a dataframe to use as test input and runs the function being tested.
        rows = [['C:\\ACC\\Disk1\\file1.txt', 1000, 'Low Risk', 'Not for TA', 'Not for Other'],
                ['C:\\ACC\\Disk1\\file2.txt', 2000, 'Low Risk', 'Not for TA', 'Not for Other'],
                ['C:\\ACC\\Disk1\\file3.txt', 3000, 'Low Risk', 'Not for TA', 'Not for Other'],
                ['C:\\ACC\\Disk2\\file4.txt', 4000, 'Low Risk', 'Not for TA', 'Not for Other'],
                ['C:\\ACC\\Disk2\\file5.txt', 5000, 'Low Risk', 'Not for TA', 'Not for Other']]
        column_names = ['FITS_File_Path', 'FITS_Size_KB', 'NARA_Risk Level', 'Technical_Appraisal', 'Other_Risk']
        df_results = pd.DataFrame(rows, columns=column_names)
        df_media_subtotal = media_subtotal(df_results, self.accession_folder)

        # Makes lists of the actual results from the test and the expected results.
        # Uses reset_index() to include the index value in the dataframe, which is the media name.
        results = df_media_subtotal.reset_index().values.tolist()
        expected = [['Disk1', 3, 6, 0, 0, 3, 0, 0, 0],
                    ['Disk2', 2, 9, 0, 0, 2, 0, 0, 0]]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(results, expected, 'Problem with technical appraisal, Not for TA')

    def test_other_all(self):
        """
        Test for other risk subtotal when all meet an other risk criteria.
        Result for testing is the media subtotal dataframe, converted to a list for easier comparison.
        """
        # Makes a dataframe to use as test input and runs the function being tested.
        rows = [['C:\\ACC\\Disk1\\backup1.gz', 1000, 'Low Risk', 'Not for TA', 'Archive format'],
                ['C:\\ACC\\Disk1\\backup2.gz', 2000, 'Low Risk', 'Not for TA', 'Archive format'],
                ['C:\\ACC\\Disk1\\database.db', 3000, 'Low Risk', 'Not for TA', 'NARA Low/Transform'],
                ['C:\\ACC\\Disk2\\database.db', 4000, 'Low Risk', 'Not for TA', 'NARA Low/Transform'],
                ['C:\\ACC\\Disk2\\backup3.gz', 5000, 'Low Risk', 'Not for TA', 'Archive format']]
        column_names = ['FITS_File_Path', 'FITS_Size_KB', 'NARA_Risk Level', 'Technical_Appraisal', 'Other_Risk']
        df_results = pd.DataFrame(rows, columns=column_names)
        df_media_subtotal = media_subtotal(df_results, self.accession_folder)

        # Makes lists of the actual results from the test and the expected results.
        # Uses reset_index() to include the index value in the dataframe, which is the media name.
        results = df_media_subtotal.reset_index().values.tolist()
        expected = [['Disk1', 3, 6, 0, 0, 3, 0, 0, 3],
                    ['Disk2', 2, 9, 0, 0, 2, 0, 0, 2]]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(results, expected, 'Problem with other risk, all have a risk')

    def test_other_some(self):
        """
        Test for other risk subtotal when some have a risk and others do not.
        Result for testing is the media subtotal dataframe, converted to a list for easier comparison.
        """
        # Makes a dataframe to use as test input and runs the function being tested.
        rows = [['C:\\ACC\\Disk1\\file1.txt', 1000, 'Low Risk', 'Not for TA', 'Not for Other'],
                ['C:\\ACC\\Disk1\\file2.txt', 2000, 'Low Risk', 'Not for TA', 'Not for Other'],
                ['C:\\ACC\\Disk1\\graphic.cdr', 3000, 'High Risk', 'Not for TA', 'Layered image file'],
                ['C:\\ACC\\Disk2\\file.txt', 4000, 'Low Risk', 'Not for TA', 'Not for Other'],
                ['C:\\ACC\\Disk2\\theme.css', 5000, 'Low Risk', 'Not for TA', 'Possible saved web page']]
        column_names = ['FITS_File_Path', 'FITS_Size_KB', 'NARA_Risk Level', 'Technical_Appraisal', 'Other_Risk']
        df_results = pd.DataFrame(rows, columns=column_names)
        df_media_subtotal = media_subtotal(df_results, self.accession_folder)

        # Makes lists of the actual results from the test and the expected results.
        # Uses reset_index() to include the index value in the dataframe, which is the media name.
        results = df_media_subtotal.reset_index().values.tolist()
        expected = [['Disk1', 3, 6, 1, 0, 2, 0, 0, 1],
                    ['Disk2', 2, 9, 0, 0, 2, 0, 0, 1]]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(results, expected, 'Problem with other risk, some have a risk')

    def test_other_none(self):
        """
        Test for other risk subtotal when none have a risk.
        Result for testing is the media subtotal dataframe, converted to a list for easier comparison.
        """
        # Makes a dataframe to use as test input and runs the function being tested.
        rows = [['C:\\ACC\\Disk1\\file1.txt', 1000, 'Low Risk', 'Not for TA', 'Not for Other'],
                ['C:\\ACC\\Disk1\\file2.txt', 2000, 'Low Risk', 'Not for TA', 'Not for Other'],
                ['C:\\ACC\\Disk1\\file3.txt', 3000, 'Low Risk', 'Not for TA', 'Not for Other'],
                ['C:\\ACC\\Disk2\\file4.txt', 4000, 'Low Risk', 'Not for TA', 'Not for Other'],
                ['C:\\ACC\\Disk2\\file5.txt', 5000, 'Low Risk', 'Not for TA', 'Not for Other']]
        column_names = ['FITS_File_Path', 'FITS_Size_KB', 'NARA_Risk Level', 'Technical_Appraisal', 'Other_Risk']
        df_results = pd.DataFrame(rows, columns=column_names)
        df_media_subtotal = media_subtotal(df_results, self.accession_folder)

        # Makes lists of the actual results from the test and the expected results.
        # Uses reset_index() to include the index value in the dataframe, which is the media name.
        results = df_media_subtotal.reset_index().values.tolist()
        expected = [['Disk1', 3, 6, 0, 0, 3, 0, 0, 0],
                    ['Disk2', 2, 9, 0, 0, 2, 0, 0, 0]]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(results, expected, 'Problem with other risk, none have risk')


if __name__ == '__main__':
    unittest.main()
