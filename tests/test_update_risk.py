"""Tests the update_risk function, which updates the acc_full_risk_data.csv
to remove files deleted from the accession folder since the last time this script ran.

To simplify testing, the fits and risk dataframes only have a few of the columns.
Only the FITS_Path column is needed for testing."""

import os
import pandas as pd
import unittest
from format_analysis_functions import update_risk


class MyTestCase(unittest.TestCase):

    def setUp(self):
        """
        Creates the risk dataframe used for most of the tests
        and saves it to a csv as additional test input.
        In the real script, this csv would have already existed and been read as df_risk.
        """
        rows = [['C:\\acc\\file.txt', 'Plain text', 'Plain Text', 'Low Risk'],
                ['C:\\acc\\audio.mp4', 'MPEG', 'MPEG 4 (H.264)', 'Low Risk'],
                ['C:\\acc\\audio.mp4', 'MPEG', 'MPEG-4 Media File', 'Low Risk'],
                ['C:\\acc\\spreadsheet.xlsx', 'XLSX', 'Microsoft Excel Office Open XML', 'Low Risk'],
                ['C:\\acc\\spreadsheet.xlsx', 'Office Open XML Workbook', 'Microsoft Excel Office Open XML', 'Low Risk']]
        self.df_risk = pd.DataFrame(rows, columns=['FITS_File_Path', 'FITS_Format_Name', 'NARA_Format Name', 'NARA_Risk Level'])

        self.csv_path = os.path.join(os.getcwd(), 'accession_full_risk_data.csv')
        self.df_risk.to_csv(self.csv_path, index=False)

    def tearDown(self):
        """
        Deletes the risk csv made during each test.
        """
        os.remove(os.path.join(os.getcwd(), 'accession_full_risk_data.csv'))

    def test_no_change(self):
        """
        Test for running the function after no changes were made
        to the files in the accession folder (df_fits) or the risk csv (df_risk).
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """
        # Creates the fits dataframe to use for testing.
        df_fits = pd.DataFrame([['C:\\acc\\file.txt', 'Plain text'],
                                ['C:\\acc\\audio.mp4', 'MPEG'],
                                ['C:\\acc\\spreadsheet.xlsx', 'XLSX'],
                                ['C:\\acc\\spreadsheet.xlsx', 'Office Open XML Workbook']],
                               columns=['FITS_File_Path', 'FITS_Format_Name'])

        # Runs the function being tested and converts the resulting dataframe to a list, including the column headers.
        df_result = update_risk(df_fits, self.df_risk, self.csv_path)
        result = [df_result.columns.to_list()] + df_result.values.tolist()

        # Creates a list of the expected result.
        expected = [['FITS_File_Path', 'FITS_Format_Name', 'NARA_Format Name', 'NARA_Risk Level'],
                    ['C:\\acc\\file.txt', 'Plain text', 'Plain Text', 'Low Risk'],
                    ['C:\\acc\\audio.mp4', 'MPEG', 'MPEG 4 (H.264)', 'Low Risk'],
                    ['C:\\acc\\audio.mp4', 'MPEG', 'MPEG-4 Media File', 'Low Risk'],
                    ['C:\\acc\\spreadsheet.xlsx', 'XLSX', 'Microsoft Excel Office Open XML', 'Low Risk'],
                    ['C:\\acc\\spreadsheet.xlsx', 'Office Open XML Workbook', 'Microsoft Excel Office Open XML', 'Low Risk']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with no change')

    def test_fits_simplified(self):
        """
        Test for running the function after no changes were made to the files in the accession folder (df_fits),
        and the extra FITS ID was removed from the risk csv (df_risk).
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """
        # Creates dataframes to use for testing.
        df_fits = pd.DataFrame([['C:\\acc\\file.txt', 'Plain text'],
                                ['C:\\acc\\audio.mp4', 'MPEG'],
                                ['C:\\acc\\spreadsheet.xlsx', 'XLSX'],
                                ['C:\\acc\\spreadsheet.xlsx', 'Office Open XML Workbook']],
                               columns=['FITS_File_Path', 'FITS_Format_Name'])
        df_risk = pd.DataFrame([['C:\\acc\\file.txt', 'Plain text', 'Plain Text', 'Low Risk'],
                                ['C:\\acc\\audio.mp4', 'MPEG', 'MPEG 4 (H.264)', 'Low Risk'],
                                ['C:\\acc\\audio.mp4', 'MPEG', 'MPEG-4 Media File', 'Low Risk'],
                                ['C:\\acc\\spreadsheet.xlsx', 'XLSX', 'Microsoft Excel Office Open XML', 'Low Risk']],
                               columns=['FITS_File_Path', 'FITS_Format_Name', 'NARA_Format Name', 'NARA_Risk Level'])

        # Creates a risk csv in the script tests folder to use for testing.
        # In the real script, this csv would have already existed and been read as df_risk.
        csv_path = os.path.join(os.getcwd(), 'accession_full_risk_data.csv')
        df_risk.to_csv(csv_path, index=False)

        # Runs the function being tested and converts the resulting dataframe to a list, including the column headers.
        df_result = update_risk(df_fits, df_risk, csv_path)
        result = [df_result.columns.to_list()] + df_result.values.tolist()

        # Creates a list of the expected result.
        expected = [['FITS_File_Path', 'FITS_Format_Name', 'NARA_Format Name', 'NARA_Risk Level'],
                    ['C:\\acc\\file.txt', 'Plain text', 'Plain Text', 'Low Risk'],
                    ['C:\\acc\\audio.mp4', 'MPEG', 'MPEG 4 (H.264)', 'Low Risk'],
                    ['C:\\acc\\audio.mp4', 'MPEG', 'MPEG-4 Media File', 'Low Risk'],
                    ['C:\\acc\\spreadsheet.xlsx', 'XLSX', 'Microsoft Excel Office Open XML', 'Low Risk']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with FITS simplified')

    def test_nara_simplified(self):
        """
        Test for running the function after no changes were made to the files in the accession folder (df_fits),
        and the extra NARA match were removed from the risk csv (df_risk).
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """
        # Creates dataframes to use for testing.
        df_fits = pd.DataFrame([['C:\\acc\\file.txt', 'Plain text'],
                                ['C:\\acc\\audio.mp4', 'MPEG'],
                                ['C:\\acc\\spreadsheet.xlsx', 'XLSX'],
                                ['C:\\acc\\spreadsheet.xlsx', 'Office Open XML Workbook']],
                               columns=['FITS_File_Path', 'FITS_Format_Name'])
        df_risk = pd.DataFrame([['C:\\acc\\file.txt', 'Plain text', 'Plain Text', 'Low Risk'],
                                ['C:\\acc\\audio.mp4', 'MPEG', 'MPEG-4 Media File', 'Low Risk'],
                                ['C:\\acc\\spreadsheet.xlsx', 'XLSX', 'Microsoft Excel Office Open XML', 'Low Risk'],
                                ['C:\\acc\\spreadsheet.xlsx', 'Office Open XML Workbook', 'Microsoft Excel Office Open XML', 'Low Risk']],
                               columns=['FITS_File_Path', 'FITS_Format_Name', 'NARA_Format Name', 'NARA_Risk Level'])

        # Creates a risk csv in the script tests folder to use for testing.
        # In the real script, this csv would have already existed and been read as df_risk.
        csv_path = os.path.join(os.getcwd(), 'accession_full_risk_data.csv')
        df_risk.to_csv(csv_path, index=False)

        # Runs the function being tested and converts the resulting dataframe to a list, including the column headers.
        df_result = update_risk(df_fits, df_risk, csv_path)
        result = [df_result.columns.to_list()] + df_result.values.tolist()

        # Creates a list of the expected result.
        expected = [['FITS_File_Path', 'FITS_Format_Name', 'NARA_Format Name', 'NARA_Risk Level'],
                    ['C:\\acc\\file.txt', 'Plain text', 'Plain Text', 'Low Risk'],
                    ['C:\\acc\\audio.mp4', 'MPEG', 'MPEG-4 Media File', 'Low Risk'],
                    ['C:\\acc\\spreadsheet.xlsx', 'XLSX', 'Microsoft Excel Office Open XML', 'Low Risk'],
                    ['C:\\acc\\spreadsheet.xlsx', 'Office Open XML Workbook', 'Microsoft Excel Office Open XML', 'Low Risk']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with NARA simplified')

    def test_one_id_deleted(self):
        """
        Test for running the function after a file with one FITs ID (file.txt in df_fits)
        was deleted from the accession folder, and no changes were made to the risk csv (df_risk).
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """
        # Creates the fits dataframe to use for testing.
        df_fits = pd.DataFrame([['C:\\acc\\audio.mp4', 'MPEG'],
                                ['C:\\acc\\spreadsheet.xlsx', 'XLSX'],
                                ['C:\\acc\\spreadsheet.xlsx', 'Office Open XML Workbook']],
                               columns=['FITS_File_Path', 'FITS_Format_Name'])

        # Runs the function being tested and converts the resulting dataframe to a list, including the column headers.
        df_result = update_risk(df_fits, self.df_risk, self.csv_path)
        result = [df_result.columns.to_list()] + df_result.values.tolist()

        # Creates a list of the expected result.
        expected = [['FITS_File_Path', 'FITS_Format_Name', 'NARA_Format Name', 'NARA_Risk Level'],
                    ['C:\\acc\\audio.mp4', 'MPEG', 'MPEG 4 (H.264)', 'Low Risk'],
                    ['C:\\acc\\audio.mp4', 'MPEG', 'MPEG-4 Media File', 'Low Risk'],
                    ['C:\\acc\\spreadsheet.xlsx', 'XLSX', 'Microsoft Excel Office Open XML', 'Low Risk'],
                    ['C:\\acc\\spreadsheet.xlsx', 'Office Open XML Workbook', 'Microsoft Excel Office Open XML', 'Low Risk']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with a file with one FITS ID deleted')

    def test_two_id_deleted(self):
        """
        Test for running the function after a file with two FITS IDs (spreadsheet.xlsx in df_fits)
        is deleted from the accession folder, and no changes were made to the risk csv (df_risk).
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """
        # Creates the fits dataframe to use for testing.
        df_fits = pd.DataFrame([['C:\\acc\\file.txt', 'Plain text'],
                                ['C:\\acc\\audio.mp4', 'MPEG']],
                               columns=['FITS_File_Path', 'FITS_Format_Name'])

        # Runs the function being tested and converts the resulting dataframe to a list, including the column headers.
        df_result = update_risk(df_fits, self.df_risk, self.csv_path)
        result = [df_result.columns.to_list()] + df_result.values.tolist()

        # Creates a list of the expected result.
        expected = [['FITS_File_Path', 'FITS_Format_Name', 'NARA_Format Name', 'NARA_Risk Level'],
                    ['C:\\acc\\file.txt', 'Plain text', 'Plain Text', 'Low Risk'],
                    ['C:\\acc\\audio.mp4', 'MPEG', 'MPEG 4 (H.264)', 'Low Risk'],
                    ['C:\\acc\\audio.mp4', 'MPEG', 'MPEG-4 Media File', 'Low Risk']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with a file with two FITS IDs deleted')

    def test_two_files_deleted(self):
        """
        Test for running the function after two files (file.txt and audio.mp4)
        were deleted from the accession folder (df_fits) and no changes were made to the risk csv (df_risk).
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """
        # Creates the fits dataframe to use for testing.
        df_fits = pd.DataFrame([['C:\\acc\\spreadsheet.xlsx', 'XLSX'],
                                ['C:\\acc\\spreadsheet.xlsx', 'Office Open XML Workbook']],
                               columns=['FITS_File_Path', 'FITS_Format_Name'])

        # Runs the function being tested and converts the resulting dataframe to a list, including the column headers.
        df_result = update_risk(df_fits, self.df_risk, self.csv_path)
        result = [df_result.columns.to_list()] + df_result.values.tolist()

        # Creates a list of the expected result.
        expected = [['FITS_File_Path', 'FITS_Format_Name', 'NARA_Format Name', 'NARA_Risk Level'],
                    ['C:\\acc\\spreadsheet.xlsx', 'XLSX', 'Microsoft Excel Office Open XML', 'Low Risk'],
                    ['C:\\acc\\spreadsheet.xlsx', 'Office Open XML Workbook', 'Microsoft Excel Office Open XML', 'Low Risk']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with two files deleted')

    def test_file_added(self):
        """
        Test for running the function after a file (new.txt) is added to the accession folder (df_fits)
        and no changes are made to the risk csv (df_risk).
        This change is not currently detected because it is so rare.
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """
        # Creates the fits dataframe to use for testing.
        df_fits = pd.DataFrame([['C:\\acc\\file.txt', 'Plain text'],
                                ['C:\\acc\\new.txt', 'Plain text'],
                                ['C:\\acc\\audio.mp4', 'MPEG'],
                                ['C:\\acc\\spreadsheet.xlsx', 'XLSX'],
                                ['C:\\acc\\spreadsheet.xlsx', 'Office Open XML Workbook']],
                               columns=['FITS_File_Path', 'FITS_Format_Name'])

        # Runs the function being tested and converts the resulting dataframe to a list, including the column headers.
        df_result = update_risk(df_fits, self.df_risk, self.csv_path)
        result = [df_result.columns.to_list()] + df_result.values.tolist()

        # Creates a list of the expected result.
        expected = [['FITS_File_Path', 'FITS_Format_Name', 'NARA_Format Name', 'NARA_Risk Level'],
                    ['C:\\acc\\file.txt', 'Plain text', 'Plain Text', 'Low Risk'],
                    ['C:\\acc\\audio.mp4', 'MPEG', 'MPEG 4 (H.264)', 'Low Risk'],
                    ['C:\\acc\\audio.mp4', 'MPEG', 'MPEG-4 Media File', 'Low Risk'],
                    ['C:\\acc\\spreadsheet.xlsx', 'XLSX', 'Microsoft Excel Office Open XML', 'Low Risk'],
                    ['C:\\acc\\spreadsheet.xlsx', 'Office Open XML Workbook', 'Microsoft Excel Office Open XML', 'Low Risk']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with one file added')


if __name__ == '__main__':
    unittest.main()
