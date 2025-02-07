"""Tests the function csv_to_dataframe, which reads the 4 CSVs with data needed for the analysis into dataframes,
handles encoding errors if encountered, and edits column names for two of them."""

import csv
import numpy as np
import os
import unittest
from format_analysis_functions import csv_to_dataframe
import configuration as c


class MyTestCase(unittest.TestCase):

    def tearDown(self):
        """
        Deletes the test file accession_fits.csv, if it is present.
        """
        if os.path.exists('accession_fits.csv'):
            os.remove('accession_fits.csv')

    def test_fits(self):
        """
        Test for reading the FITS spreadsheet (different for each accession).
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """
        # Creates an abbreviated FITS CSV (fewer columns) with no special characters to use for test input.
        with open('accession_fits.csv', 'w', newline='') as file:
            file_write = csv.writer(file)
            file_write.writerow(['FITS_File_Path', 'FITS_Format_Name', 'FITS_Format_Version', 'FITS_Multiple_IDs'])
            file_write.writerow(['C:\\Coll\\accession\\CD1_Images\\IMG1.JPG', 'JPEG EXIF', '1.01', False])
            file_write.writerow(['C:\\Coll\\accession\\CD2_Web\\index.html', 'Hypertext Markup Language', '4.01', True])
            file_write.writerow(['C:\\Coll\\accession\\CD2_Web\\index.html', 'HTML Transitional', 'HTML 4.01', True])

        # Runs the function being tested and converts the resulting dataframe into a list (including the column names).
        df = csv_to_dataframe('accession_fits.csv')
        result = [df.columns.to_list()] + df.values.tolist()

        # Creates a list with the expected result.
        expected = [['FITS_File_Path', 'FITS_Format_Name', 'FITS_Format_Version', 'FITS_Multiple_IDs'],
                    ['C:\\Coll\\accession\\CD1_Images\\IMG1.JPG', 'JPEG EXIF', '1.01', 'False'],
                    ['C:\\Coll\\accession\\CD2_Web\\index.html', 'Hypertext Markup Language', '4.01', 'True'],
                    ['C:\\Coll\\accession\\CD2_Web\\index.html', 'HTML Transitional', 'HTML 4.01', 'True']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with FITS')

    def test_ita(self):
        """
        Test for reading the technical appraisal spreadsheet (ITAfileformats.csv).
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """
        # Runs the function being tested and converts the resulting dataframe into a list (including the column names).
        df = csv_to_dataframe(c.ITA)
        result = [df.columns.to_list()] + df.values.tolist()

        # Creates a list with the expected result.
        # NOTE: this must be updated when new things are added to the spreadsheet.
        expected = [['FITS_FORMAT', 'NOTES'],
                    ['Adobe Font Metric', np.nan],
                    ['DOS batch file', np.nan],
                    ['DOS/Windows Executable', 'Also high risk'],
                    ['empty', np.nan],
                    ['Microsoft Windows Autorun', np.nan],
                    ['MS Windows icon resource', 'Also high risk'],
                    ['PE32 executable', 'Also high risk'],
                    ['TFF/TrueType Font', np.nan],
                    ['Unknown Binary', np.nan],
                    ['x86 boot sector', 'Also high risk']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with ITA')

    def test_other_risk(self):
        """
        Test for reading the other risks spreadsheet (Riskfileformats.csv).
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """
        # Runs the function being tested and converts the resulting dataframe into a list (including the column names).
        df = csv_to_dataframe(c.RISK)
        result = [df.columns.to_list()] + df.values.tolist()

        # Creates a list with the expected result.
        # NOTE: this must be updated when new things are added to the spreadsheet.
        expected = [['FITS_FORMAT', 'RISK_CRITERIA'],
                    ['Adobe Photoshop file', 'Layered image file'],
                    ['Cascading Style Sheet', 'Possible saved web page'],
                    ['CorelDraw Drawing', 'Layered image file'],
                    ['Encapsulated Postscript File', 'Layered image file'],
                    ['GZIP', 'Archive format'],
                    ['Microsoft Cabinet Archive Data', 'Archive format'],
                    ['StuffIt Archive', 'Archive format'],
                    ['ZIP', 'Archive format'],
                    ['ZIP Format', 'Archive format']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with other risk')

    def test_nara(self):
        """
        Tests for reading the NARA risk spreadsheet (NARA_PreservationActionPlan_FileFormats.csv).
        Result for testing is that the dataframe isn't empty and the column names are correct.
        The test can't check the data in the spreadsheet since it is very large and updated frequently.
        """
        # Runs the function being tested.
        df = csv_to_dataframe(c.NARA)

        # First test is that the dataframe is not empty.
        result_empty = len(df) != 0
        expected_empty = True

        # Second test is the columns in the dataframe, which were renamed by the function.
        result_columns = df.columns.to_list()
        expected_columns = ['NARA_Format_Name', 'NARA_File_Extensions', 'Category/Plan(s)', 'NARA Format ID',
                            'MIME type(s)', 'Specification/Standard URL', 'NARA_PRONOM_URL', 'LOC URL',
                            'British Library URL', 'WikiData URL', 'ArchiveTeam URL', 'ForensicsWiki URL',
                            'Wikipedia URL', 'docs.fileformat.com', 'Other URL', 'Notes', 'NARA_Risk_Level',
                            'NARA Preservation Action', 'NARA_Proposed_Preservation_Plan',
                            'Description and Justification', 'NARA Preferred Processing and Transformation Tool(s)']

        # Compares both results. assertEqual prints "OK" or the differences between the result and expected result.
        self.assertEqual(result_empty, expected_empty, 'Problem with nara - dataframe empty')
        self.assertEqual(result_columns, expected_columns, 'Problem with nara - dataframe columns')

    def test_encoding_error(self):
        """
        Test for reading a spreadsheet with an encoding error, using FITS for the test data.
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """
        # Creates an abbreviated FITS CSV (fewer columns) with special characters to use for test input.
        # Characters are the copyright symbol and an accented e.
        with open('accession_fits.csv', 'w', newline='') as file:
            file_write = csv.writer(file)
            file_write.writerow(['FITS_File_Path', 'FITS_Format_Name', 'FITS_Format_Version', 'FITS_Multiple_IDs'])
            file_write.writerow(['C:\\Coll\\accession\\CD1_Images\\©Image.JPG', 'JPEG EXIF', '1.01', False])
            file_write.writerow(['C:\\Coll\\accession\\CD2_Web\\indexé.html', 'Hypertext Markup Language', '4.01', True])
            file_write.writerow(['C:\\Coll\\accession\\CD2_Web\\indexé.html', 'HTML Transitional', 'HTML 4.01', True])

        # Runs the function being tested and converts the resulting dataframe into a list (including the column names).
        # NOTE: the function prints an error message to the terminal if it is working correctly.
        df = csv_to_dataframe('accession_fits.csv')
        result = [df.columns.to_list()] + df.values.tolist()

        # Creates a list with the expected result.
        expected = [['FITS_File_Path', 'FITS_Format_Name', 'FITS_Format_Version', 'FITS_Multiple_IDs'],
                    ['C:\\Coll\\accession\\CD1_Images\\Image.JPG', 'JPEG EXIF', '1.01', 'False'],
                    ['C:\\Coll\\accession\\CD2_Web\\index.html', 'Hypertext Markup Language', '4.01', 'True'],
                    ['C:\\Coll\\accession\\CD2_Web\\index.html', 'HTML Transitional', 'HTML 4.01', 'True']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with encoding error')


if __name__ == '__main__':
    unittest.main()
