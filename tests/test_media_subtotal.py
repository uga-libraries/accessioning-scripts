"""Tests the function media_subtotal, which gets summary information for each piece of media."""

import pandas as pd
import unittest
from format_analysis_functions import media_subtotal


class MyTestCase(unittest.TestCase):

    def test_nara_high(self):
        """
        Test for NARA risk level subtotal with files that are high risk.
        Result for testing is the media subtotal dataframe, converted to a list for easier comparison.
        """
        # Creates test input.
        rows = [['C:\\ACC\\Disk1\\photo1.crw', 1000, 'High Risk', 'Not for TA', 'Not for Other'],
                ['C:\\ACC\\Disk1\\photo2.crw', 2000, 'High Risk', 'Not for TA', 'Not for Other'],
                ['C:\\ACC\\Disk1\\photo3.crw', 3000, 'High Risk', 'Not for TA', 'Not for Other'],
                ['C:\\ACC\\Disk2\\photo4.crw', 4000, 'High Risk', 'Not for TA', 'Not for Other'],
                ['C:\\ACC\\Disk2\\photo5.crw', 5000, 'High Risk', 'Not for TA', 'Not for Other']]
        column_names = ['FITS_File_Path', 'FITS_Size_KB', 'NARA_Risk Level', 'Technical_Appraisal', 'Other_Risk']
        df_results = pd.DataFrame(rows, columns=column_names)

        # Runs the function being tested and converts the resulting dataframe to a list.
        # Uses reset_index() to include the index value in the dataframe, which is the media name.
        df_media_subtotal = media_subtotal(df_results, accession_folder='C:\\ACC')
        result = df_media_subtotal.reset_index().values.tolist()

        # Creates a list with the expected result.
        expected = [['Disk1', 3, 6, 3, 0, 0, 0, 0, 0],
                    ['Disk2', 2, 9, 2, 0, 0, 0, 0, 0]]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with NARA, high risk')

    def test_nara_moderate(self):
        """
        Test for NARA risk level subtotal with files that are moderate risk.
        Result for testing is the media subtotal dataframe, converted to a list for easier comparison.
        """
        # Creates test input.
        rows = [['C:\\ACC\\Disk1\\flyer1.ai', 1000, 'Moderate Risk', 'Not for TA', 'Not for Other'],
                ['C:\\ACC\\Disk1\\flyer2.ai', 2000, 'Moderate Risk', 'Not for TA', 'Not for Other'],
                ['C:\\ACC\\Disk1\\flyer3.ai', 3000, 'Moderate Risk', 'Not for TA', 'Not for Other'],
                ['C:\\ACC\\Disk2\\flyer4.ai', 4000, 'Moderate Risk', 'Not for TA', 'Not for Other'],
                ['C:\\ACC\\Disk2\\flyer5.ai', 5000, 'Moderate Risk', 'Not for TA', 'Not for Other']]
        column_names = ['FITS_File_Path', 'FITS_Size_KB', 'NARA_Risk Level', 'Technical_Appraisal', 'Other_Risk']
        df_results = pd.DataFrame(rows, columns=column_names)

        # Runs the function being tested and converts the resulting dataframe to a list.
        # Uses reset_index() to include the index value in the dataframe, which is the media name.
        df_media_subtotal = media_subtotal(df_results, accession_folder='C:\\ACC')
        result = df_media_subtotal.reset_index().values.tolist()

        # Creates a list with the expected result.
        expected = [['Disk1', 3, 6, 0, 3, 0, 0, 0, 0],
                    ['Disk2', 2, 9, 0, 2, 0, 0, 0, 0]]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with NARA, moderate risk')

    def test_nara_low(self):
        """
        Test for NARA risk level subtotal with files that are low risk.
        Result for testing is the media subtotal dataframe, converted to a list for easier comparison.
        """
        # Creates test input.
        rows = [['C:\\ACC\\Disk1\\file1.txt', 1000, 'Low Risk', 'Not for TA', 'Not for Other'],
                ['C:\\ACC\\Disk1\\file2.txt', 2000, 'Low Risk', 'Not for TA', 'Not for Other'],
                ['C:\\ACC\\Disk1\\file3.txt', 3000, 'Low Risk', 'Not for TA', 'Not for Other'],
                ['C:\\ACC\\Disk2\\file4.txt', 4000, 'Low Risk', 'Not for TA', 'Not for Other'],
                ['C:\\ACC\\Disk2\\file5.txt', 5000, 'Low Risk', 'Not for TA', 'Not for Other']]
        column_names = ['FITS_File_Path', 'FITS_Size_KB', 'NARA_Risk Level', 'Technical_Appraisal', 'Other_Risk']
        df_results = pd.DataFrame(rows, columns=column_names)

        # Runs the function being tested and converts the resulting dataframe to a list.
        # Uses reset_index() to include the index value in the dataframe, which is the media name.
        df_media_subtotal = media_subtotal(df_results, accession_folder='C:\\ACC')
        result = df_media_subtotal.reset_index().values.tolist()

        # Creates a list with the expected result.
        expected = [['Disk1', 3, 6, 0, 0, 3, 0, 0, 0],
                    ['Disk2', 2, 9, 0, 0, 2, 0, 0, 0]]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with NARA, low risk')

    def test_nara_no_match(self):
        """
        Test for NARA risk level subtotal with files that do not match.
        Result for testing is the media subtotal dataframe, converted to a list for easier comparison.
        """
        # Creates test input.
        rows = [['C:\\ACC\\Disk1\\file1.uk', 1000, 'No Match', 'Not for TA', 'Not for Other'],
                ['C:\\ACC\\Disk1\\file2.uk', 2000, 'No Match', 'Not for TA', 'Not for Other'],
                ['C:\\ACC\\Disk1\\file3.uk', 3000, 'No Match', 'Not for TA', 'Not for Other'],
                ['C:\\ACC\\Disk2\\file4.uk', 4000, 'No Match', 'Not for TA', 'Not for Other'],
                ['C:\\ACC\\Disk2\\file5.uk', 5000, 'No Match', 'Not for TA', 'Not for Other']]
        column_names = ['FITS_File_Path', 'FITS_Size_KB', 'NARA_Risk Level', 'Technical_Appraisal', 'Other_Risk']
        df_results = pd.DataFrame(rows, columns=column_names)

        # Runs the function being tested and converts the resulting dataframe to a list.
        # Uses reset_index() to include the index value in the dataframe, which is the media name.
        df_media_subtotal = media_subtotal(df_results, accession_folder='C:\\ACC')
        result = df_media_subtotal.reset_index().values.tolist()

        # Creates a list with the expected result.
        expected = [['Disk1', 3, 6, 0, 0, 0, 3, 0, 0],
                    ['Disk2', 2, 9, 0, 0, 0, 2, 0, 0]]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with NARA, no match')

    def test_nara_mix(self):
        """
        Test for NARA risk level subtotal with files that are different risk levels.
        Result for testing is the media subtotal dataframe, converted to a list for easier comparison.
        """
        # Creates test input.
        rows = [['C:\\ACC\\Disk1\\file1.txt', 1000, 'Low Risk', 'Not for TA', 'Not for Other'],
                ['C:\\ACC\\Disk1\\file2.txt', 2000, 'Low Risk', 'Not for TA', 'Not for Other'],
                ['C:\\ACC\\Disk1\\photo3.crw', 3000, 'High Risk', 'Not for TA', 'Not for Other'],
                ['C:\\ACC\\Disk2\\command2.bat', 4000, 'Moderate Risk', 'Format', 'Not for Other'],
                ['C:\\ACC\\Disk2\\command3.bat', 5000, 'Moderate Risk', 'Format', 'Not for Other']]
        column_names = ['FITS_File_Path', 'FITS_Size_KB', 'NARA_Risk Level', 'Technical_Appraisal', 'Other_Risk']
        df_results = pd.DataFrame(rows, columns=column_names)

        # Runs the function being tested and converts the resulting dataframe to a list.
        # Uses reset_index() to include the index value in the dataframe, which is the media name.
        df_media_subtotal = media_subtotal(df_results, accession_folder='C:\\ACC')
        result = df_media_subtotal.reset_index().values.tolist()

        # Creates a list with the expected result.
        expected = [['Disk1', 3, 6, 1, 0, 2, 0, 0, 0],
                    ['Disk2', 2, 9, 0, 2, 0, 0, 2, 0]]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with NARA, mix of risk levels')

    def test_ta_format(self):
        """
        Test for technical appraisal subtotal with some files that require technical appraisal ('Format').
        Result for testing is the media subtotal dataframe, converted to a list for easier comparison.
        """
        # Creates test input.
        rows = [['C:\\ACC\\Disk1\\file1.txt', 1000, 'Low Risk', 'Not for TA', 'Not for Other'],
                ['C:\\ACC\\Disk1\\file2.txt', 2000, 'Low Risk', 'Not for TA', 'Not for Other'],
                ['C:\\ACC\\Disk1\\command1.bat', 3000, 'Moderate Risk', 'Format', 'Not for Other'],
                ['C:\\ACC\\Disk2\\command2.bat', 4000, 'Moderate Risk', 'Format', 'Not for Other'],
                ['C:\\ACC\\Disk2\\command3.bat', 5000, 'Moderate Risk', 'Format', 'Not for Other']]
        column_names = ['FITS_File_Path', 'FITS_Size_KB', 'NARA_Risk Level', 'Technical_Appraisal', 'Other_Risk']
        df_results = pd.DataFrame(rows, columns=column_names)

        # Runs the function being tested and converts the resulting dataframe to a list.
        # Uses reset_index() to include the index value in the dataframe, which is the media name.
        df_media_subtotal = media_subtotal(df_results, accession_folder='C:\\ACC')
        result = df_media_subtotal.reset_index().values.tolist()

        # Creates a list with the expected result.
        expected = [['Disk1', 3, 6, 0, 1, 2, 0, 1, 0],
                    ['Disk2', 2, 9, 0, 2, 0, 0, 2, 0]]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with technical appraisal, format')

    def test_ta_trash(self):
        """
        Test for technical appraisal subtotal with some files categorized as 'Trash',
        a category which is skipped by the subtotal.
        Result for testing is the media subtotal dataframe, converted to a list for easier comparison.
        """
        # Creates test input.
        rows = [['C:\\ACC\\Disk1\\file1.txt', 1000, 'Low Risk', 'Trash', 'Not for Other'],
                ['C:\\ACC\\Disk1\\file2.txt', 2000, 'Low Risk', 'Trash', 'Not for Other'],
                ['C:\\ACC\\Disk1\\file3.txt', 3000, 'Low Risk', 'Not for TA', 'Not for Other'],
                ['C:\\ACC\\Disk2\\file4.txt', 4000, 'Low Risk', 'Trash', 'Not for Other'],
                ['C:\\ACC\\Disk2\\file5.txt', 5000, 'Low Risk', 'Not for TA', 'Not for Other']]
        column_names = ['FITS_File_Path', 'FITS_Size_KB', 'NARA_Risk Level', 'Technical_Appraisal', 'Other_Risk']
        df_results = pd.DataFrame(rows, columns=column_names)

        # Runs the function being tested and converts the resulting dataframe to a list.
        # Uses reset_index() to include the index value in the dataframe, which is the media name.
        df_media_subtotal = media_subtotal(df_results, accession_folder='C:\\ACC')
        result = df_media_subtotal.reset_index().values.tolist()

        # Creates a list with the expected result.
        expected = [['Disk1', 3, 6, 0, 0, 3, 0, 0, 0],
                    ['Disk2', 2, 9, 0, 0, 2, 0, 0, 0]]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with technical appraisal, trash')

    def test_ta_none(self):
        """
        Test for technical appraisal subtotal when all are 'Not for TA'.
        Result for testing is the media subtotal dataframe, converted to a list for easier comparison.
        """
        # Creates test input.
        rows = [['C:\\ACC\\Disk1\\file1.txt', 1000, 'Low Risk', 'Not for TA', 'Not for Other'],
                ['C:\\ACC\\Disk1\\file2.txt', 2000, 'Low Risk', 'Not for TA', 'Not for Other'],
                ['C:\\ACC\\Disk1\\file3.txt', 3000, 'Low Risk', 'Not for TA', 'Not for Other'],
                ['C:\\ACC\\Disk2\\file4.txt', 4000, 'Low Risk', 'Not for TA', 'Not for Other'],
                ['C:\\ACC\\Disk2\\file5.txt', 5000, 'Low Risk', 'Not for TA', 'Not for Other']]
        column_names = ['FITS_File_Path', 'FITS_Size_KB', 'NARA_Risk Level', 'Technical_Appraisal', 'Other_Risk']
        df_results = pd.DataFrame(rows, columns=column_names)

        # Runs the function being tested and converts the resulting dataframe to a list.
        # Uses reset_index() to include the index value in the dataframe, which is the media name.
        df_media_subtotal = media_subtotal(df_results, accession_folder='C:\\ACC')
        result = df_media_subtotal.reset_index().values.tolist()

        # Creates a list with the expected result.
        expected = [['Disk1', 3, 6, 0, 0, 3, 0, 0, 0],
                    ['Disk2', 2, 9, 0, 0, 2, 0, 0, 0]]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with technical appraisal, none are TA')

    def test_other_all(self):
        """
        Test for other risk subtotal when all meet an other risk criteria.
        Result for testing is the media subtotal dataframe, converted to a list for easier comparison.
        """
        # Creates test input.
        rows = [['C:\\ACC\\Disk1\\backup1.gz', 1000, 'Low Risk', 'Not for TA', 'Archive format'],
                ['C:\\ACC\\Disk1\\backup2.gz', 2000, 'Low Risk', 'Not for TA', 'Archive format'],
                ['C:\\ACC\\Disk1\\database.db', 3000, 'Low Risk', 'Not for TA', 'NARA Low/Transform'],
                ['C:\\ACC\\Disk2\\database.db', 4000, 'Low Risk', 'Not for TA', 'NARA Low/Transform'],
                ['C:\\ACC\\Disk2\\backup3.gz', 5000, 'Low Risk', 'Not for TA', 'Archive format']]
        column_names = ['FITS_File_Path', 'FITS_Size_KB', 'NARA_Risk Level', 'Technical_Appraisal', 'Other_Risk']
        df_results = pd.DataFrame(rows, columns=column_names)

        # Runs the function being tested and converts the resulting dataframe to a list.
        # Uses reset_index() to include the index value in the dataframe, which is the media name.
        df_media_subtotal = media_subtotal(df_results, accession_folder='C:\\ACC')
        result = df_media_subtotal.reset_index().values.tolist()

        # Creates a list with the expected result.
        expected = [['Disk1', 3, 6, 0, 0, 3, 0, 0, 3],
                    ['Disk2', 2, 9, 0, 0, 2, 0, 0, 2]]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with other risk, all have a risk')

    def test_other_some(self):
        """
        Test for other risk subtotal when some have a risk and others do not.
        Result for testing is the media subtotal dataframe, converted to a list for easier comparison.
        """
        # Creates test input.
        rows = [['C:\\ACC\\Disk1\\file1.txt', 1000, 'Low Risk', 'Not for TA', 'Not for Other'],
                ['C:\\ACC\\Disk1\\file2.txt', 2000, 'Low Risk', 'Not for TA', 'Not for Other'],
                ['C:\\ACC\\Disk1\\graphic.cdr', 3000, 'High Risk', 'Not for TA', 'Layered image file'],
                ['C:\\ACC\\Disk2\\file.txt', 4000, 'Low Risk', 'Not for TA', 'Not for Other'],
                ['C:\\ACC\\Disk2\\theme.css', 5000, 'Low Risk', 'Not for TA', 'Possible saved web page']]
        column_names = ['FITS_File_Path', 'FITS_Size_KB', 'NARA_Risk Level', 'Technical_Appraisal', 'Other_Risk']
        df_results = pd.DataFrame(rows, columns=column_names)

        # Runs the function being tested and converts the resulting dataframe to a list.
        # Uses reset_index() to include the index value in the dataframe, which is the media name.
        df_media_subtotal = media_subtotal(df_results, accession_folder='C:\\ACC')
        result = df_media_subtotal.reset_index().values.tolist()

        # Creates a list with the expected result.
        expected = [['Disk1', 3, 6, 1, 0, 2, 0, 0, 1],
                    ['Disk2', 2, 9, 0, 0, 2, 0, 0, 1]]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with other risk, some have a risk')

    def test_other_none(self):
        """
        Test for other risk subtotal when none have a risk.
        Result for testing is the media subtotal dataframe, converted to a list for easier comparison.
        """
        # Creates test input.
        rows = [['C:\\ACC\\Disk1\\file1.txt', 1000, 'Low Risk', 'Not for TA', 'Not for Other'],
                ['C:\\ACC\\Disk1\\file2.txt', 2000, 'Low Risk', 'Not for TA', 'Not for Other'],
                ['C:\\ACC\\Disk1\\file3.txt', 3000, 'Low Risk', 'Not for TA', 'Not for Other'],
                ['C:\\ACC\\Disk2\\file4.txt', 4000, 'Low Risk', 'Not for TA', 'Not for Other'],
                ['C:\\ACC\\Disk2\\file5.txt', 5000, 'Low Risk', 'Not for TA', 'Not for Other']]
        column_names = ['FITS_File_Path', 'FITS_Size_KB', 'NARA_Risk Level', 'Technical_Appraisal', 'Other_Risk']
        df_results = pd.DataFrame(rows, columns=column_names)

        # Runs the function being tested and converts the resulting dataframe to a list.
        # Uses reset_index() to include the index value in the dataframe, which is the media name.
        df_media_subtotal = media_subtotal(df_results, accession_folder='C:\\ACC')
        result = df_media_subtotal.reset_index().values.tolist()

        # Creates a list with the expected result.
        expected = [['Disk1', 3, 6, 0, 0, 3, 0, 0, 0],
                    ['Disk2', 2, 9, 0, 0, 2, 0, 0, 0]]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with other risk, none have risk')

    def test_files(self):
        """
        Test for subtotal when some files are not in a media folder.
        Result for testing is the media subtotal dataframe, converted to a list for easier comparison.
        """
        # Creates test input.
        rows = [['C:\\ACC\\Disk1\\file1.txt', 1000, 'Low Risk', 'Not for TA', 'Not for Other'],
                ['C:\\ACC\\Disk1\\file2.txt', 2000, 'Low Risk', 'Not for TA', 'Not for Other'],
                ['C:\\ACC\\Disk2\\file3.txt', 4000, 'Low Risk', 'Not for TA', 'Not for Other'],
                ['C:\\ACC\\file4.txt', 3000, 'Low Risk', 'Not for TA', 'Not for Other'],
                ['C:\\ACC\\file5.txt', 5000, 'Low Risk', 'Not for TA', 'Not for Other']]
        column_names = ['FITS_File_Path', 'FITS_Size_KB', 'NARA_Risk Level', 'Technical_Appraisal', 'Other_Risk']
        df_results = pd.DataFrame(rows, columns=column_names)

        # Runs the function being tested and converts the resulting dataframe to a list.
        # Uses reset_index() to include the index value in the dataframe, which is the media name.
        df_media_subtotal = media_subtotal(df_results, accession_folder='C:\\ACC')
        result = df_media_subtotal.reset_index().values.tolist()

        # Creates a list with the expected result.
        expected = [['Disk1', 2, 3, 0, 0, 2, 0, 0, 0],
                    ['Disk2', 1, 4, 0, 0, 1, 0, 0, 0]]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with files')

    def test_rounding(self):
        """
        Test for subtotal when file sizes result in more than 3 decimal places for the subtotal.
        Result for testing is the media subtotal dataframe, converted to a list for easier comparison.
        """
        # Creates test input.
        rows = [['C:\\ACC\\Disk1\\file1.txt', 0.2, 'Low Risk', 'Not for TA', 'Not for Other'],
                ['C:\\ACC\\Disk1\\file2.txt', 0.3, 'Low Risk', 'Not for TA', 'Not for Other'],
                ['C:\\ACC\\Disk1\\file3.txt', 0.4, 'Low Risk', 'Not for TA', 'Not for Other'],
                ['C:\\ACC\\Disk2\\file4.txt', 4.123, 'Low Risk', 'Not for TA', 'Not for Other'],
                ['C:\\ACC\\Disk2\\file5.txt', 5.456, 'Low Risk', 'Not for TA', 'Not for Other']]
        column_names = ['FITS_File_Path', 'FITS_Size_KB', 'NARA_Risk Level', 'Technical_Appraisal', 'Other_Risk']
        df_results = pd.DataFrame(rows, columns=column_names)

        # Runs the function being tested and converts the resulting dataframe to a list.
        # Uses reset_index() to include the index value in the dataframe, which is the media name.
        df_media_subtotal = media_subtotal(df_results, accession_folder='C:\\ACC')
        result = df_media_subtotal.reset_index().values.tolist()

        # Creates a list with the expected result.
        expected = [['Disk1', 3, 0.001, 0, 0, 3, 0, 0, 0],
                    ['Disk2', 2, 0.01, 0, 0, 2, 0, 0, 0]]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with rounding')

    def test_fill_zero(self):
        """
        Test for filling columns with 0 if there were no file of that type.
        This is identical to other risk, none have risk.
        It is repeated as a test for 0 to highlight when the zero fill might be a problem.
        Result for testing is the media subtotal dataframe, converted to a list for easier comparison.
        """
        # Creates test input.
        rows = [['C:\\ACC\\Disk1\\file1.txt', 1000, 'Low Risk', 'Not for TA', 'Not for Other'],
                ['C:\\ACC\\Disk1\\file2.txt', 2000, 'Low Risk', 'Not for TA', 'Not for Other'],
                ['C:\\ACC\\Disk1\\file3.txt', 3000, 'Low Risk', 'Not for TA', 'Not for Other'],
                ['C:\\ACC\\Disk2\\file4.txt', 4000, 'Low Risk', 'Not for TA', 'Not for Other'],
                ['C:\\ACC\\Disk2\\file5.txt', 5000, 'Low Risk', 'Not for TA', 'Not for Other']]
        column_names = ['FITS_File_Path', 'FITS_Size_KB', 'NARA_Risk Level', 'Technical_Appraisal', 'Other_Risk']
        df_results = pd.DataFrame(rows, columns=column_names)

        # Runs the function being tested and converts the resulting dataframe to a list.
        # Uses reset_index() to include the index value in the dataframe, which is the media name.
        df_media_subtotal = media_subtotal(df_results, accession_folder='C:\\ACC')
        result = df_media_subtotal.reset_index().values.tolist()

        # Creates a list with the expected result.
        expected = [['Disk1', 3, 6, 0, 0, 3, 0, 0, 0],
                    ['Disk2', 2, 9, 0, 0, 2, 0, 0, 0]]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with fill zero')


if __name__ == '__main__':
    unittest.main()
