"""Tests the function csv_to_dataframe, which reads the 4 CSVs with data needed for the analysis into dataframes,
handles encoding errors if encountered, and edits column names for 2 of them."""

import csv
import os
import pandas as pd
import unittest
from format_analysis_functions import csv_to_dataframe
from configuration import *


class MyTestCase(unittest.TestCase):

    def tearDown(self):
        """Deletes the test file accession_fits.csv, if it is present."""
        if os.path.exists('accession_fits.csv'):
            os.remove('accession_fits.csv')

    def test_fits(self):
        """Test for reading of accession_fits.csv.
        Result for testing is the contents of the dataframe."""

        # Makes an abbreviated FITS CSV (fewer columns) with no special characters to use for testing.
        with open('accession_fits.csv', 'w', newline='') as file:
            file_write = csv.writer(file)
            file_write.writerow(['File_Path', 'Format_Name', 'Format_Version', 'Multiple_IDs'])
            file_write.writerow([r'C:\Coll\accession\CD001_Images\IMG1.JPG', 'JPEG EXIF', '1.01', False])
            file_write.writerow([r'C:\Coll\accession\CD002_Web\index.html', 'Hypertext Markup Language', '4.01', True])
            file_write.writerow([r'C:\Coll\accession\CD002_Web\index.html', 'HTML Transitional', 'HTML 4.01', True])
        df_result = csv_to_dataframe('accession_fits.csv')

        # Makes a dataframe with the expected values in df_fits after the CSV is read with encoding_errors="ignore".
        # This causes characters to be skipped if they can't be read.
        rows = [[r'C:\Coll\accession\CD001_Images\IMG1.JPG', 'JPEG EXIF', '1.01', False],
                [r'C:\Coll\accession\CD002_Web\index.html', 'Hypertext Markup Language', '4.01', True],
                [r'C:\Coll\accession\CD002_Web\index.html', 'HTML Transitional', 'HTML 4.01', True]]
        column_names = ['FITS_File_Path', 'FITS_Format_Name', 'FITS_Format_Version', 'FITS_Multiple_IDs']
        df_expected = pd.DataFrame(rows, columns=column_names)

        # Compares the contents of the FITS dataframe to the expected values.
        # Using pandas test functionality because unittest assertEqual is unable to compare dataframes.
        pd.testing.assert_frame_equal(df_result, df_expected)

    def test_ita(self):
        """Tests the function worked by verifying the column names and that the dataframe isn't empty.
           The test can't check the data in the dataframe since it uses the real CSVs, which are updated frequently."""
        # TODO: this one actually could be a test of the dataframe contents.

        df = csv_to_dataframe(ITA)

        # First test is that the dataframe is not empty.
        result_empty = len(df) != 0
        expected_empty = True

        # Second test is the columns in the dataframe.
        result_columns = df.columns.to_list()
        expected_columns = ['FITS_FORMAT', 'NOTES']

        self.assertEqual(result_empty, expected_empty, 'Problem with ita - dataframe empty')
        self.assertEqual(result_columns, expected_columns, 'Problem with ita - dataframe columns')

    def test_other_risk(self):
        """Tests the function worked by verifying the column names and that the dataframe isn't empty.
           The test can't check the data in the dataframe since it uses the real CSVs, which are updated frequently."""
        # TODO: this one actually could be a test of the dataframe contents.

        df = csv_to_dataframe(RISK)

        # First test is that the dataframe is not empty.
        result_empty = len(df) != 0
        expected_empty = True

        # Second test is the columns in the dataframe.
        result_columns = df.columns.to_list()
        expected_columns = ['FITS_FORMAT', 'RISK_CRITERIA']

        self.assertEqual(result_empty, expected_empty, 'Problem with other risk - dataframe empty')
        self.assertEqual(result_columns, expected_columns, 'Problem with other risk - dataframe columns')

    def test_nara(self):
        """Tests the function worked by verifying the column names and that the dataframe isn't empty.
           The test can't check the data in the dataframe since it uses the real CSVs, which are updated frequently."""

        df = csv_to_dataframe(NARA)

        # First test is that the dataframe is not empty.
        result_empty = len(df) != 0
        expected_empty = True

        # Second test is the columns in the dataframe.
        result_columns = df.columns.to_list()
        expected_columns = ['NARA_Format Name', 'NARA_File Extension(s)', 'NARA_Category/Plan(s)',
                            'NARA_NARA Format ID', 'NARA_MIME type(s)', 'NARA_Specification/Standard URL',
                            'NARA_PRONOM URL', 'NARA_LOC URL', 'NARA_British Library URL', 'NARA_WikiData URL',
                            'NARA_ArchiveTeam URL', 'NARA_ForensicsWiki URL', 'NARA_Wikipedia URL',
                            'NARA_docs.fileformat.com', 'NARA_Other URL', 'NARA_Notes', 'NARA_Risk Level',
                            'NARA_Preservation Action', 'NARA_Proposed Preservation Plan',
                            'NARA_Description and Justification', 'NARA_Preferred Processing and Transformation Tool(s)']

        self.assertEqual(result_empty, expected_empty, 'Problem with nara - dataframe empty')
        self.assertEqual(result_columns, expected_columns, 'Problem with nara - dataframe columns')

    def test_encoding_error(self):
        """Tests unicode error handling when reading a CSV into a dataframe."""

        # Makes a FITS CSV with special characters (copyright symbol and accented e) to use for testing.
        # In format_analysis.py, this would be made earlier in the script and have more columns.
        with open('accession_fits.csv', 'w', newline='') as file:
            file_write = csv.writer(file)
            file_write.writerow(['File_Path', 'Format_Name', 'Format_Version', 'Multiple_IDs'])
            file_write.writerow([r'C:\Coll\accession\CD001_Images\©Image.JPG', 'JPEG EXIF', '1.01', False])
            file_write.writerow([r'C:\Coll\accession\CD002_Web\indexé.html', 'Hypertext Markup Language', '4.01', True])
            file_write.writerow([r'C:\Coll\accession\CD002_Web\indexé.html', 'HTML Transitional', 'HTML 4.01', True])

        # Runs the function being tested, which will print a message to the terminal if working correctly.
        df_result = csv_to_dataframe('accession_fits.csv')

        # Makes a dataframe with the expected values in df_fits after the CSV is read with encoding_errors="ignore".
        # This causes characters to be skipped if they can't be read.
        rows = [[r'C:\Coll\accession\CD001_Images\Image.JPG', 'JPEG EXIF', '1.01', False],
                [r'C:\Coll\accession\CD002_Web\index.html', 'Hypertext Markup Language', '4.01', True],
                [r'C:\Coll\accession\CD002_Web\index.html', 'HTML Transitional', 'HTML 4.01', True]]
        column_names = ['FITS_File_Path', 'FITS_Format_Name', 'FITS_Format_Version', 'FITS_Multiple_IDs']
        df_expected = pd.DataFrame(rows, columns=column_names)

        # Compares the contents of the FITS dataframe to the expected values.
        # Using pandas test functionality because unittest assertEqual is unable to compare dataframes.
        pd.testing.assert_frame_equal(df_result, df_expected)


if __name__ == '__main__':
    unittest.main()