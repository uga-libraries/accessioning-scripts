"""Tests the function csv_to_dataframe, which reads the 4 CSVs with data needed for the analysis into dataframes,
handles encoding errors if encountered, and edits column names for 2 of them."""

import csv
import numpy as np
import os
import unittest
from format_analysis_functions import csv_to_dataframe
import configuration as c


class MyTestCase(unittest.TestCase):

    def tearDown(self):
        """Deletes the test file accession_fits.csv, if it is present."""
        if os.path.exists('accession_fits.csv'):
            os.remove('accession_fits.csv')

    def test_fits(self):
        """
        Test for reading the FITS spreadsheet (different for each accession).
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """

        # Makes an abbreviated FITS CSV (fewer columns) with no special characters to use for testing.
        with open('accession_fits.csv', 'w', newline='') as file:
            file_write = csv.writer(file)
            file_write.writerow(['File_Path', 'Format_Name', 'Format_Version', 'Multiple_IDs'])
            file_write.writerow(['C:\\Coll\\accession\\CD1_Images\\IMG1.JPG', 'JPEG EXIF', '1.01', False])
            file_write.writerow(['C:\\Coll\\accession\\CD2_Web\\index.html', 'Hypertext Markup Language', '4.01', True])
            file_write.writerow(['C:\\Coll\\accession\\CD2_Web\\index.html', 'HTML Transitional', 'HTML 4.01', True])

        # Runs the function being tested and makes a list of lists from the dataframe.
        # The first list is the column headers and the rest are one list per row.
        df = csv_to_dataframe('accession_fits.csv')
        results = [df.columns.to_list()] + df.values.tolist()

        # Creates a list with the expected results.
        expected = [['FITS_File_Path', 'FITS_Format_Name', 'FITS_Format_Version', 'FITS_Multiple_IDs'],
                    ['C:\\Coll\\accession\\CD1_Images\\IMG1.JPG', 'JPEG EXIF', '1.01', False],
                    ['C:\\Coll\\accession\\CD2_Web\\index.html', 'Hypertext Markup Language', '4.01', True],
                    ['C:\\Coll\\accession\\CD2_Web\\index.html', 'HTML Transitional', 'HTML 4.01', True]]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(results, expected, 'Problem with FITS')

    def test_ita(self):
        """
        Test for reading the technical appraisal spreadsheet (ITAfileformats.csv).
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """

        # Runs the function being tested and makes a list from the dataframe.
        df = csv_to_dataframe(c.ITA)
        results = [df.columns.to_list()] + df.values.tolist()

        # Creates a list with the expected results.
        # NOTE: this must be when new things are added to the spreadsheet.
        expected = [['FITS_FORMAT', 'NOTES'],
                    ['Adobe Font Metric', np.NaN],
                    ['DOS batch file', np.NaN],
                    ['DOS/Windows Executable', 'Also high risk'],
                    ['empty', np.NaN],
                    ['Microsoft Windows Autorun', np.NaN],
                    ['MS Windows icon resource', 'Also high risk'],
                    ['PE32 executable', 'Also high risk'],
                    ['TFF/TrueType Font', np.NaN],
                    ['Unknown Binary', np.NaN],
                    ['x86 boot sector', 'Also high risk']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(results, expected, 'Problem with ITA')

    def test_other_risk(self):
        """
        Test for reading the other risks spreadsheet (Riskfileformats.csv).
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """

        # Runs the function being tested and makes a list from the dataframe.
        df = csv_to_dataframe(c.RISK)
        results = [df.columns.to_list()] + df.values.tolist()

        # Creates a list with the expected results.
        # NOTE: this must be when new things are added to the spreadsheet.
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
        self.assertEqual(results, expected, 'Problem with other risk')

    def test_nara(self):
        """
        Tests for reading the NARA risk spreadsheet (NARA_PreservationActionPlan_FileFormats.csv).
        Result for testing is that the dataframe isn't empty and the column names are correct.
        The test can't check the data in the spreadsheet since it is very large and updated frequently.
        """

        # Runs the function being tested.
        df = csv_to_dataframe(c.NARA)

        # First test is that the dataframe is not empty.
        results_empty = len(df) != 0
        expected_empty = True

        # Second test is the columns in the dataframe, which were renamed by the function.
        results_columns = df.columns.to_list()
        expected_columns = ['NARA_Format Name', 'NARA_File Extension(s)', 'NARA_Category/Plan(s)',
                            'NARA_NARA Format ID', 'NARA_MIME type(s)', 'NARA_Specification/Standard URL',
                            'NARA_PRONOM URL', 'NARA_LOC URL', 'NARA_British Library URL', 'NARA_WikiData URL',
                            'NARA_ArchiveTeam URL', 'NARA_ForensicsWiki URL', 'NARA_Wikipedia URL',
                            'NARA_docs.fileformat.com', 'NARA_Other URL', 'NARA_Notes', 'NARA_Risk Level',
                            'NARA_Preservation Action', 'NARA_Proposed Preservation Plan',
                            'NARA_Description and Justification', 'NARA_Preferred Processing and Transformation Tool(s)']

        self.assertEqual(results_empty, expected_empty, 'Problem with nara - dataframe empty')
        self.assertEqual(results_columns, expected_columns, 'Problem with nara - dataframe columns')

    def test_encoding_error(self):
        """
        Test for reading a spreadsheet with an encoding error, using FITS for the test data.
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """

        # Makes an abbreviated FITS CSV (fewer columns) with special characters to use for testing.
        # Characters are the copyright symbol and an accented e.
        with open('accession_fits.csv', 'w', newline='') as file:
            file_write = csv.writer(file)
            file_write.writerow(['File_Path', 'Format_Name', 'Format_Version', 'Multiple_IDs'])
            file_write.writerow(['C:\\Coll\\accession\\CD1_Images\\©Image.JPG', 'JPEG EXIF', '1.01', False])
            file_write.writerow(['C:\\Coll\\accession\\CD2_Web\\indexé.html', 'Hypertext Markup Language', '4.01', True])
            file_write.writerow(['C:\\Coll\\accession\\CD2_Web\\indexé.html', 'HTML Transitional', 'HTML 4.01', True])

        # Runs the function being tested and makes a list of lists from the dataframe.
        # The first list is the column headers and the rest are one list per row.
        # NOTE: the function does print an error message to the terminal if it is working correctly.
        df = csv_to_dataframe('accession_fits.csv')
        results = [df.columns.to_list()] + df.values.tolist()

        # Creates a list with the expected results after the CSV is read with encoding_errors="ignore".
        # This causes characters to be skipped if they can't be read.
        expected = [['FITS_File_Path', 'FITS_Format_Name', 'FITS_Format_Version', 'FITS_Multiple_IDs'],
                    ['C:\\Coll\\accession\\CD1_Images\\Image.JPG', 'JPEG EXIF', '1.01', False],
                    ['C:\\Coll\\accession\\CD2_Web\\index.html', 'Hypertext Markup Language', '4.01', True],
                    ['C:\\Coll\\accession\\CD2_Web\\index.html', 'HTML Transitional', 'HTML 4.01', True]]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(results, expected, 'Problem with encoding error')


if __name__ == '__main__':
    unittest.main()
