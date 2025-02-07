"""Tests the function match_nara_risk, which combines FITS format identifications with NARA risk information
to produce df_results.

To simplify the testing, df_fits only has the file path, format name, format version, and PUID,
the only columns used by match_nara_risk."""

import numpy as np
import os
import unittest
from format_analysis_functions import csv_to_dataframe, match_nara_risk
import configuration as c


class MyTestCase(unittest.TestCase):

    def test_extension_and_version(self):
        """
        Test for files that match a single file extension and version combination in the NARA spreadsheet.
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """
        # Creates test input.
        df_fits = csv_to_dataframe(os.path.join('test_combined_fits', 'extension_and_version_fits.csv'))
        df_nara = csv_to_dataframe(c.NARA)

        # Runs the function being tested and converts the resulting dataframe to a list, including the column headers.
        df_results = match_nara_risk(df_fits, df_nara)
        result = [df_results.columns.to_list()] + df_results.values.tolist()

        # Creates a list with the expected result.
        expected = [['FITS_File_Path', 'FITS_Format_Name', 'FITS_Format_Version', 'FITS_PUID', 'NARA_Format Name',
                     'NARA_File Extension(s)', 'NARA_PRONOM URL', 'NARA_Risk Level', 'NARA_Proposed Preservation Plan',
                     'NARA_Match_Type'],
                    ['C:\\ext\\File.rtf', 'Rich Text', '1.2', np.nan, 'Rich Text Format 1.2', 'rtf',
                     'https://www.nationalarchives.gov.uk/pronom/fmt/45',
                     'Moderate Risk', 'Transform to PDF', 'File Extension and Version'],
                    ['C:\\ext\\File.accdb', 'MS Access', '2019', np.nan, 'Microsoft Access 2019', 'accdb',
                     np.nan, 'Moderate Risk', 'Transform to CSV', 'File Extension and Version']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with extension and version match')

    def test_extension_and_version_not_puid_template(self):
        """
        Test for files that match a single file extension and version combination in the NARA spreadsheet.
        FITS has a PUID that doesn't match any in NARA, and NARA match has no PUID.
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """
        # # Creates test input.
        df_fits = csv_to_dataframe(os.path.join('test_combined_fits', 'extension_and_version_not_puid_fits.csv'))
        df_nara = csv_to_dataframe(c.NARA)

        # Runs the function being tested and converts the resulting dataframe to a list, including the column headers.
        df_results = match_nara_risk(df_fits, df_nara)
        result = [df_results.columns.to_list()] + df_results.values.tolist()

        # Creates a list with the expected result.
        expected = [['FITS_File_Path', 'FITS_Format_Name', 'FITS_Format_Version', 'FITS_PUID', 'NARA_Format Name',
                     'NARA_File Extension(s)', 'NARA_PRONOM URL', 'NARA_Risk Level', 'NARA_Proposed Preservation Plan',
                     'NARA_Match_Type'],
                    ['C:\\ext\\File.accdb', 'MS Access', '2010',
                     'https://www.nationalarchives.gov.uk/pronom/fmt/000',
                     'Microsoft Access 2010', 'accdb', np.nan,
                     'Moderate Risk', 'Transform to CSV', 'File Extension and Version'],
                    ['C:\\ext\\File.doc', 'MS Word for Mac', '5.1',
                     'https://www.nationalarchives.gov.uk/pronom/fmt/000', 'Microsoft Word for Macintosh 5.1',
                     'doc', np.nan, 'Moderate Risk', 'Transform to PDF', 'File Extension and Version']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with extension and version, NARA no PUID')

    def test_extension_multiple(self):
        """
        Test for files that match more than one extension in the NARA spreadsheet.
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """
        # Creates test input.
        df_fits = csv_to_dataframe(os.path.join('test_combined_fits', 'extension_multiple_fits.csv'))
        df_nara = csv_to_dataframe(c.NARA)

        # Runs the function being tested and converts the resulting dataframe to a list, including the column headers.
        df_results = match_nara_risk(df_fits, df_nara)
        result = [df_results.columns.to_list()] + df_results.values.tolist()

        # Creates a list with the expected result.
        expected = [['FITS_File_Path', 'FITS_Format_Name', 'FITS_Format_Version', 'FITS_PUID', 'NARA_Format Name',
                     'NARA_File Extension(s)', 'NARA_PRONOM URL', 'NARA_Risk Level', 'NARA_Proposed Preservation Plan',
                     'NARA_Match_Type'],
                    ['C:\\ext\\file.aac', 'MPEG-4', np.nan, np.nan, 'Advanced Audio Coding (AAC) MPEG-2 Audio', 'aac',
                     np.nan, 'Low Risk', 'Transform to BWF or MP3 as appropriate', 'File Extension'],
                    ['C:\\ext\\file.aac', 'MPEG-4', np.nan, np.nan, 'Advanced Audio Coding MPEG-4 Low Complexity Object',
                     'aac|mp4|m4a', np.nan, 'Low Risk', 'Transform to BWF or MP3 as appropriate', 'File Extension'],
                    ['C:\\ext\\file.aac', 'MPEG-4', np.nan, np.nan, 'MPEG-4 File Format, V.2, with Advanced Audio Coding',
                     'aac', np.nan, 'Low Risk', 'Transform to BWF or MP3 as appropriate', 'File Extension'],
                    ['C:\\ext\\file.aac', 'MPEG-4', np.nan, np.nan,
                     'QuickTime Audio with AAC codec', 'qta|aac|m4p|mp3', np.nan,
                     'Moderate Risk', 'Transform to BWF or MP3 as appropriate', 'File Extension'],
                    ['C:\\ext\\file.CIN', 'Kodak', np.nan, np.nan, 'Kodak Cineon', 'cin', np.nan, 'High Risk',
                     'Transform to TIFF if possible', 'File Extension'],
                    ['C:\\ext\\file.CIN', 'Kodak', np.nan, np.nan, 'OS/2 Change Control File', 'cin',
                     'https://www.nationalarchives.gov.uk/pronom/x-fmt/143', 'Moderate Risk', 'Retain', 'File Extension']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with extension, multiple matches')

    def test_extension_multiple_not_puid(self):
        """
        Test for files that match more than one extension in the NARA spreadsheet.
        FITS has a PUID that doesn't match any in NARA, and NARA match has no PUID.
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """
        # Creates test input.
        df_fits = csv_to_dataframe(os.path.join('test_combined_fits', 'extension_multiple_not_puid_fits.csv'))
        df_nara = csv_to_dataframe(c.NARA)

        # Runs the function being tested and converts the resulting dataframe to a list, including the column headers.
        df_results = match_nara_risk(df_fits, df_nara)
        result = [df_results.columns.to_list()] + df_results.values.tolist()

        # Creates a list with the expected result.
        expected = [['FITS_File_Path', 'FITS_Format_Name', 'FITS_Format_Version', 'FITS_PUID', 'NARA_Format Name',
                     'NARA_File Extension(s)', 'NARA_PRONOM URL', 'NARA_Risk Level', 'NARA_Proposed Preservation Plan',
                     'NARA_Match_Type'],
                    ['C:\\ext\\file.bmp', 'OS/2 Bitmap', np.nan, 'https://www.nationalarchives.gov.uk/pronom/fmt/000',
                     'OS/2 Bitmap unspecified version', 'bmp', np.nan, 'Moderate Risk', 'Transform to TIFF',
                     'File Extension'],
                    ['C:\\ext\\file.bmp', 'OS/2 Bitmap', np.nan, 'https://www.nationalarchives.gov.uk/pronom/fmt/000',
                     'Windows Bitmap unspecified version', 'bmp', np.nan, 'Moderate Risk', 'Transform to TIFF',
                     'File Extension'],
                    ['C:\\ext\\file.cdf', 'Mathematica Doc', np.nan,
                     'https://www.nationalarchives.gov.uk/pronom/fmt/000', 'Common Data Format Toolkit', 'cdf',
                     np.nan, 'Moderate Risk', 'Retain', 'File Extension'],
                    ['C:\\ext\\file.cdf', 'Mathematica Doc', np.nan,
                     'https://www.nationalarchives.gov.uk/pronom/fmt/000', 'Mathematica Computable Document Format',
                     'cdf', np.nan, 'Moderate Risk', 'Transform to PDF', 'File Extension']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with extension, multiple matches, NARA no PUID')

    def test_extension_one_case(self):
        """
        Test for files that match one extension in the NARA spreadsheet, with the same case.
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """
        # Creates test input.
        df_fits = csv_to_dataframe(os.path.join('test_combined_fits', 'extension_one_case_fits.csv'))
        df_nara = csv_to_dataframe(c.NARA)

        # Runs the function being tested and converts the resulting dataframe to a list, including the column headers.
        df_results = match_nara_risk(df_fits, df_nara)
        result = [df_results.columns.to_list()] + df_results.values.tolist()

        # Creates a list with the expected result.
        expected = [['FITS_File_Path', 'FITS_Format_Name', 'FITS_Format_Version', 'FITS_PUID', 'NARA_Format Name',
                     'NARA_File Extension(s)', 'NARA_PRONOM URL', 'NARA_Risk Level', 'NARA_Proposed Preservation Plan',
                     'NARA_Match_Type'],
                    ['C:\\ext\\file.mxf', 'MXF', np.nan, np.nan, 'Material Exchange Format', 'mxf',
                     'https://www.nationalarchives.gov.uk/pronom/fmt/200', 'Low Risk', 'Retain', 'File Extension'],
                    ['C:\\ext\\file.crl', 'Raster', np.nan, np.nan, 'Intergraph Raster Format', 'crl',
                     'https://www.nationalarchives.gov.uk/pronom/x-fmt/229', 'Moderate Risk', 'Transform to TIFF',
                     'File Extension'],
                    ['C:\\ext\\file.px', 'Pixel File', np.nan, np.nan, 'Pixel Image File', 'px', np.nan,
                     'High Risk', 'Further research is required', 'File Extension']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with extension, case match')

    def test_extension_one_no_case(self):
        """
        Test for files that match one extension in the NARA spreadsheet, case doesn't match.
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """
        # Creates test input.
        df_fits = csv_to_dataframe(os.path.join('test_combined_fits', 'extension_one_no_case_fits.csv'))
        df_nara = csv_to_dataframe(c.NARA)

        # Runs the function being tested and converts the resulting dataframe to a list, including the column headers.
        df_results = match_nara_risk(df_fits, df_nara)
        result = [df_results.columns.to_list()] + df_results.values.tolist()

        # Creates a list with the expected result.
        expected = [['FITS_File_Path', 'FITS_Format_Name', 'FITS_Format_Version', 'FITS_PUID', 'NARA_Format Name',
                     'NARA_File Extension(s)', 'NARA_PRONOM URL', 'NARA_Risk Level', 'NARA_Proposed Preservation Plan',
                     'NARA_Match_Type'],
                    ['C:\\ext\\file.MXF', 'MXF', np.nan, np.nan, 'Material Exchange Format', 'mxf',
                     'https://www.nationalarchives.gov.uk/pronom/fmt/200', 'Low Risk', 'Retain', 'File Extension'],
                    ['C:\\ext\\file.CRL', 'Raster', np.nan, np.nan, 'Intergraph Raster Format', 'crl',
                     'https://www.nationalarchives.gov.uk/pronom/x-fmt/229', 'Moderate Risk', 'Transform to TIFF',
                     'File Extension']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with extension, case does not match')

    def test_extension_one_not_puid(self):
        """
        Test for files that match one extension in the NARA spreadsheet.
        FITS has a PUID that doesn't match any in NARA, and NARA match has no PUID.
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """
        # # Creates test input.
        df_fits = csv_to_dataframe(os.path.join('test_combined_fits', 'extension_one_not_puid_fits.csv'))
        df_nara = csv_to_dataframe(c.NARA)

        # Runs the function being tested and converts the resulting dataframe to a list, including the column headers.
        df_results = match_nara_risk(df_fits, df_nara)
        result = [df_results.columns.to_list()] + df_results.values.tolist()

        # Creates a list with the expected result.
        expected = [['FITS_File_Path', 'FITS_Format_Name', 'FITS_Format_Version', 'FITS_PUID', 'NARA_Format Name',
                     'NARA_File Extension(s)', 'NARA_PRONOM URL', 'NARA_Risk Level', 'NARA_Proposed Preservation Plan',
                     'NARA_Match_Type'],
                    ['C:\\ext\\file.cst', 'Adobe Cast File', np.nan,
                     'https://www.nationalarchives.gov.uk/pronom/fmt/000',
                     'Adobe Director cast file', 'cst', np.nan,
                     'Moderate Risk', 'Transform to a TBD Format', 'File Extension'],
                    ['C:\\ext\\file.fcp', 'Final Cut Pro', np.nan,
                     'https://www.nationalarchives.gov.uk/pronom/fmt/000',
                     'Apple Final Cut Pro Project', 'fcp', np.nan, 'High Risk',
                     'Transform to Final Cut Pro XML Interchange Format (FCPXML) if possible', 'File Extension']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with extension, NARA no PUID')

    def test_extension_pipe_case(self):
        """
        Test for files that match one extension in a piped string in the NARA spreadsheet, case match.
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """
        # Creates test input.
        df_fits = csv_to_dataframe(os.path.join('test_combined_fits', 'extension_pipe_case_fits.csv'))
        df_nara = csv_to_dataframe(c.NARA)

        # Runs the function being tested and converts the resulting dataframe to a list, including the column headers.
        df_results = match_nara_risk(df_fits, df_nara)
        result = [df_results.columns.to_list()] + df_results.values.tolist()

        # Creates a list with the expected result.
        expected = [['FITS_File_Path', 'FITS_Format_Name', 'FITS_Format_Version', 'FITS_PUID', 'NARA_Format Name',
                     'NARA_File Extension(s)', 'NARA_PRONOM URL', 'NARA_Risk Level', 'NARA_Proposed Preservation Plan',
                     'NARA_Match_Type'],
                    ['C:\\ext\\file.gz', 'g-zip', np.nan, np.nan, 'GZIP', 'gz|tgz',
                     'https://www.nationalarchives.gov.uk/pronom/x-fmt/266', 'Low Risk',
                     'Retain but extract files from the container', 'File Extension'],
                    ['C:\\ext\\file.bat', 'script', np.nan, np.nan, 'Batch Script', 'bat|cmd|btm',
                     'https://www.nationalarchives.gov.uk/pronom/x-fmt/413', 'Moderate Risk', 'Retain',
                     'File Extension'],
                    ['C:\\ext\\file.sami', 'SAMI', np.nan, np.nan, 'Synchronized Accessible Media Interchange',
                     'smi|sami', np.nan, 'Low Risk', 'Retain', 'File Extension']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with extension (piped), case match')

    def test_extension_pipe_no_case(self):
        """
        Test for files that match one extension in a piped string in the NARA spreadsheet, case doesn't match.
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """
        # Creates test input.
        df_fits = csv_to_dataframe(os.path.join('test_combined_fits', 'extension_pipe_no_case_fits.csv'))
        df_nara = csv_to_dataframe(c.NARA)

        # Runs the function being tested and converts the resulting dataframe to a list, including the column headers.
        df_results = match_nara_risk(df_fits, df_nara)
        result = [df_results.columns.to_list()] + df_results.values.tolist()

        # Creates a list with the expected result.
        expected = [['FITS_File_Path', 'FITS_Format_Name', 'FITS_Format_Version', 'FITS_PUID', 'NARA_Format Name',
                     'NARA_File Extension(s)', 'NARA_PRONOM URL', 'NARA_Risk Level', 'NARA_Proposed Preservation Plan',
                     'NARA_Match_Type'],
                    ['C:\\ext\\file.GZ', 'g-zip', np.nan, np.nan, 'GZIP', 'gz|tgz',
                     'https://www.nationalarchives.gov.uk/pronom/x-fmt/266', 'Low Risk',
                     'Retain but extract files from the container', 'File Extension'],
                    ['C:\\ext\\file.BAT', 'script', np.nan, np.nan, 'Batch Script', 'bat|cmd|btm',
                     'https://www.nationalarchives.gov.uk/pronom/x-fmt/413', 'Moderate Risk', 'Retain',
                     'File Extension']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with extension (piped), case does not match')

    def test_extension_pipe_not_puid(self):
        """
        Test for files that match one extension in the NARA spreadsheet.
        FITS has a PUID that doesn't match any in NARA, and NARA match has no PUID.
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """
        # # Creates test input.
        df_fits = csv_to_dataframe(os.path.join('test_combined_fits', 'extension_pipe_not_puid_fits.csv'))
        df_nara = csv_to_dataframe(c.NARA)

        # Runs the function being tested and converts the resulting dataframe to a list, including the column headers.
        df_results = match_nara_risk(df_fits, df_nara)
        result = [df_results.columns.to_list()] + df_results.values.tolist()

        # Creates a list with the expected result.
        expected = [['FITS_File_Path', 'FITS_Format_Name', 'FITS_Format_Version', 'FITS_PUID', 'NARA_Format Name',
                     'NARA_File Extension(s)', 'NARA_PRONOM URL', 'NARA_Risk Level', 'NARA_Proposed Preservation Plan',
                     'NARA_Match_Type'],
                    ['C:\\ext\\file.heic', 'HEIC with compression', np.nan,
                     'https://www.nationalarchives.gov.uk/pronom/fmt/000',
                     'High Efficiency Image File Format with HEVC compression (HEIC)', 'heic|heics', np.nan,
                     'Moderate Risk', 'Retain', 'File Extension'],
                    ['C:\\ext\\file.toc', 'Raster', np.nan,
                     'https://www.nationalarchives.gov.uk/pronom/fmt/000',
                     'Raster Product Format', 'toc|ovr|l41', np.nan,
                     'Moderate Risk', 'Retain', 'File Extension']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with extension (piped), NARA no PUID')

    def test_name_case(self):
        """
        Test for files that match one name (no version) in the NARA spreadsheet, with the same case.
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """
        # Creates test input.
        df_fits = csv_to_dataframe(os.path.join('test_combined_fits', 'name_case_fits.csv'))
        df_nara = csv_to_dataframe(c.NARA)

        # Runs the function being tested and converts the resulting dataframe to a list, including the column headers.
        df_results = match_nara_risk(df_fits, df_nara)
        result = [df_results.columns.to_list()] + df_results.values.tolist()

        # Creates a list with the expected result.
        expected = [['FITS_File_Path', 'FITS_Format_Name', 'FITS_Format_Version', 'FITS_PUID', 'NARA_Format Name',
                     'NARA_File Extension(s)', 'NARA_PRONOM URL', 'NARA_Risk Level', 'NARA_Proposed Preservation Plan',
                     'NARA_Match_Type'],
                    ['C:\\Name\\file.bat', 'Batch Script', np.nan, np.nan, 'Batch Script', 'bat|cmd|btm',
                     'https://www.nationalarchives.gov.uk/pronom/x-fmt/413', 'Moderate Risk', 'Retain', 'Format Name'],
                    ['C:\\Name\\file.eml', 'Electronic Mail Format', np.nan, np.nan, 'Electronic Mail Format', 'eml',
                     'https://www.nationalarchives.gov.uk/pronom/fmt/278', 'Low Risk', 'Retain', 'Format Name'],
                    ['C:\\Name\\file.rom', 'ROM Image', np.nan, np.nan, 'ROM Image', 'rom', np.nan,
                     'Moderate Risk', 'Retain', 'Format Name']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with name, case match')

    def test_name_not_case(self):
        """
        Test for files that match one name (no version) in the NARA spreadsheet, case doesn't match.
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """
        # Creates test input.
        df_fits = csv_to_dataframe(os.path.join('test_combined_fits', 'name_not_case_fits.csv'))
        df_nara = csv_to_dataframe(c.NARA)

        # Runs the function being tested and converts the resulting dataframe to a list, including the column headers.
        df_results = match_nara_risk(df_fits, df_nara)
        result = [df_results.columns.to_list()] + df_results.values.tolist()

        # Creates a list with the expected result.
        expected = [['FITS_File_Path', 'FITS_Format_Name', 'FITS_Format_Version', 'FITS_PUID', 'NARA_Format Name',
                     'NARA_File Extension(s)', 'NARA_PRONOM URL', 'NARA_Risk Level', 'NARA_Proposed Preservation Plan',
                     'NARA_Match_Type'],
                    ['C:\\Name\\file.bat', 'batch script', np.nan, np.nan, 'Batch Script', 'bat|cmd|btm',
                     'https://www.nationalarchives.gov.uk/pronom/x-fmt/413', 'Moderate Risk', 'Retain', 'Format Name'],
                    ['C:\\Name\\file.eml', 'electronic mail format', np.nan, np.nan, 'Electronic Mail Format', 'eml',
                     'https://www.nationalarchives.gov.uk/pronom/fmt/278', 'Low Risk', 'Retain', 'Format Name']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with name, case does not match')

    def test_name_not_puid(self):
        """
        Test for files that match one name (no version) in the NARA spreadsheet.
        FITS has a PUID that doesn't match any in NARA, and NARA match has no PUID.
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """
        # Creates test input.
        df_fits = csv_to_dataframe(os.path.join('test_combined_fits', 'name_not_puid_fits.csv'))
        df_nara = csv_to_dataframe(c.NARA)

        # Runs the function being tested and converts the resulting dataframe to a list, including the column headers.
        df_results = match_nara_risk(df_fits, df_nara)
        result = [df_results.columns.to_list()] + df_results.values.tolist()

        # Creates a list with the expected result.
        expected = [['FITS_File_Path', 'FITS_Format_Name', 'FITS_Format_Version', 'FITS_PUID', 'NARA_Format Name',
                     'NARA_File Extension(s)', 'NARA_PRONOM URL', 'NARA_Risk Level', 'NARA_Proposed Preservation Plan',
                     'NARA_Match_Type'],
                    ['C:\\Name\\file.cod', 'BlackBerry Binary Executable', np.nan,
                     'https://www.nationalarchives.gov.uk/pronom/fmt/000', 'BlackBerry Binary Executable',
                     'cod', np.nan, 'High Risk', 'Retain', 'Format Name'],
                    ['C:\\Name\\file.dat', 'Data File', np.nan, 'https://www.nationalarchives.gov.uk/pronom/fmt/000',
                     'Data File', 'dat', np.nan, 'Moderate Risk', 'Retain', 'Format Name']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with name, NARA no PUID')

    def test_name_version_case(self):
        """
        Test for files that match one name/version combination in the NARA spreadsheet, with the same case.
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """
        # Creates test input.
        df_fits = csv_to_dataframe(os.path.join('test_combined_fits', 'name_version_case_fits.csv'))
        df_nara = csv_to_dataframe(c.NARA)

        # Runs the function being tested and converts the resulting dataframe to a list, including the column headers.
        df_results = match_nara_risk(df_fits, df_nara)
        result = [df_results.columns.to_list()] + df_results.values.tolist()

        # Creates a list with the expected result.
        expected = [['FITS_File_Path', 'FITS_Format_Name', 'FITS_Format_Version', 'FITS_PUID', 'NARA_Format Name',
                     'NARA_File Extension(s)', 'NARA_PRONOM URL', 'NARA_Risk Level', 'NARA_Proposed Preservation Plan',
                     'NARA_Match_Type'],
                    ['C:\\Name\\file.wk3', 'Lotus 1-2-3 Worksheet', '3.0', np.nan, 'Lotus 1-2-3 Worksheet 3.0',
                     'wk3', 'https://www.nationalarchives.gov.uk/pronom/x-fmt/115', 'Moderate Risk',
                     'Transform to CSV or XLSX', 'Format Name'],
                    ['C:\\Name\\file.css', 'Cascading Style Sheets', '2.1', np.nan, 'Cascading Style Sheets 2.1',
                     'css', 'https://www.nationalarchives.gov.uk/pronom/x-fmt/224', 'Low Risk',
                     'Retain', 'Format Name'],
                    ['C:\\Name\\file.swf', 'Macromedia Flash', '7', np.nan, 'Macromedia Flash 7', 'swf',
                     'https://www.nationalarchives.gov.uk/pronom/fmt/110', 'Moderate Risk',
                     'Transform to MP4 if possible, otherwise retain', 'Format Name'],
                    ['C:\\fail\\File.pts', 'Avid Pro Tools Session', '5.1-6.9', np.nan,
                     'Avid Pro Tools Session 5.1-6.9', 'pts', np.nan,
                     'High Risk', 'Transform to WAV if possible', 'Format Name']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with name and version, case match')

    def test_name_version_not_case(self):
        """
        Test for files that match one name/version combination in the NARA spreadsheet, case doesn't match.
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """
        # Creates test input.
        df_fits = csv_to_dataframe(os.path.join('test_combined_fits', 'name_version_not_case_fits.csv'))
        df_nara = csv_to_dataframe(c.NARA)

        # Runs the function being tested and converts the resulting dataframe to a list, including the column headers.
        df_results = match_nara_risk(df_fits, df_nara)
        result = [df_results.columns.to_list()] + df_results.values.tolist()

        # Creates a list with the expected result.
        expected = [['FITS_File_Path', 'FITS_Format_Name', 'FITS_Format_Version', 'FITS_PUID', 'NARA_Format Name',
                     'NARA_File Extension(s)', 'NARA_PRONOM URL', 'NARA_Risk Level', 'NARA_Proposed Preservation Plan',
                     'NARA_Match_Type'],
                    ['C:\\Name\\file.wk3', 'lotus 1-2-3 worksheet', '3.0', np.nan, 'Lotus 1-2-3 Worksheet 3.0',
                     'wk3', 'https://www.nationalarchives.gov.uk/pronom/x-fmt/115', 'Moderate Risk',
                     'Transform to CSV or XLSX', 'Format Name'],
                    ['C:\\Name\\file.css', 'cascading style sheets', '2.1', np.nan, 'Cascading Style Sheets 2.1',
                     'css', 'https://www.nationalarchives.gov.uk/pronom/x-fmt/224', 'Low Risk',
                     'Retain', 'Format Name']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with name and version, case does not match')

    def test_name_version_not_puid(self):
        """
        Test for files that match one name/version combination in the NARA spreadsheet.
        FITS has a PUID that doesn't match any in NARA, and NARA match has no PUID.
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """
        # # Creates test input.
        df_fits = csv_to_dataframe(os.path.join('test_combined_fits', 'name_version_not_puid_fits.csv'))
        df_nara = csv_to_dataframe(c.NARA)

        # Runs the function being tested and converts the resulting dataframe to a list, including the column headers.
        df_results = match_nara_risk(df_fits, df_nara)
        result = [df_results.columns.to_list()] + df_results.values.tolist()

        # Creates a list with the expected result.
        expected = [['FITS_File_Path', 'FITS_Format_Name', 'FITS_Format_Version', 'FITS_PUID', 'NARA_Format Name',
                     'NARA_File Extension(s)', 'NARA_PRONOM URL', 'NARA_Risk Level', 'NARA_Proposed Preservation Plan',
                     'NARA_Match_Type'],
                    ['C:\\Name\\file.btr', 'Btrieve', '6.0', 'https://www.nationalarchives.gov.uk/pronom/fmt/000',
                     'Btrieve 6.0', 'btr', np.nan, 'Moderate Risk', 'Transform to CSV', 'Format Name'],
                    ['C:\\Name\\file.accdb', 'Microsoft Access', '2013',
                     'https://www.nationalarchives.gov.uk/pronom/fmt/000',
                     'Microsoft Access 2013', 'accdb', np.nan,
                     'Moderate Risk', 'Transform to CSV', 'Format Name']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with name and version, NARA no PUID')

    def test_no_match(self):
        """
        Test for files that do not match any formats in the NARA spreadsheet.
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """
        # Creates test input.
        df_fits = csv_to_dataframe(os.path.join('test_combined_fits', 'no_match_fits.csv'))
        df_nara = csv_to_dataframe(c.NARA)

        # Runs the function being tested and converts the resulting dataframe to a list, including the column headers.
        df_results = match_nara_risk(df_fits, df_nara)
        result = [df_results.columns.to_list()] + df_results.values.tolist()

        # Creates a list with the expected result.
        expected = [['FITS_File_Path', 'FITS_Format_Name', 'FITS_Format_Version', 'FITS_PUID', 'NARA_Format Name',
                     'NARA_File Extension(s)', 'NARA_PRONOM URL', 'NARA_Risk Level',
                     'NARA_Proposed Preservation Plan', 'NARA_Match_Type'],
                    ['C:\\None\\file.css', 'Cascading Style Sheets', '2.0',
                     'https://www.nationalarchives.gov.uk/pronom/fmt/000',
                     'No Match', np.nan, np.nan, 'No Match', np.nan, 'No NARA Match'],
                    ['C:\\None\\file.csv', 'Comma Separated Values', np.nan,
                     'https://www.nationalarchives.gov.uk/pronom/fmt/000',
                     'No Match', np.nan, np.nan, 'No Match', np.nan, 'No NARA Match'],
                    ['C:\\None\\file.cdr', 'Corel Drawing', '8.0',
                     'https://www.nationalarchives.gov.uk/pronom/fmt/000',
                     'No Match', np.nan, np.nan, 'No Match', np.nan, 'No NARA Match'],
                    ['C:\\None\\file.exe', 'Executable', np.nan,
                     'https://www.nationalarchives.gov.uk/pronom/fmt/000',
                     'No Match', np.nan, np.nan, 'No Match', np.nan, 'No NARA Match'],
                    ['C:\\None\\file.abc', 'New Format', np.nan, np.nan, 'No Match', np.nan, np.nan,
                     'No Match', np.nan, 'No NARA Match'],
                    ['C:\\None\\file', 'Unknown Binary', np.nan, np.nan, 'No Match', np.nan, np.nan,
                     'No Match', np.nan, 'No NARA Match']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with no matches')

    def test_puid_multiple(self):
        """
        Test for files that match multiple PUIDs in the NARA spreadsheet.
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """
        # # Creates test input.
        df_fits = csv_to_dataframe(os.path.join('test_combined_fits', 'puid_multiple_fits.csv'))
        df_nara = csv_to_dataframe(c.NARA)

        # Runs the function being tested and converts the resulting dataframe to a list, including the column headers.
        df_results = match_nara_risk(df_fits, df_nara)
        result = [df_results.columns.to_list()] + df_results.values.tolist()

        # Creates a list with the expected result.
        expected = [['FITS_File_Path', 'FITS_Format_Name', 'FITS_Format_Version', 'FITS_PUID', 'NARA_Format Name',
                     'NARA_File Extension(s)', 'NARA_PRONOM URL', 'NARA_Risk Level', 'NARA_Proposed Preservation Plan',
                     'NARA_Match_Type'],
                    ['C:\\PUID\\file.xhtml', 'XHTML', '1.1', 'https://www.nationalarchives.gov.uk/pronom/fmt/103',
                     'eXtensible Hypertext Markup Language 1.1', 'xhtm|xhtml',
                     'https://www.nationalarchives.gov.uk/pronom/fmt/103',
                     'Low Risk', 'Retain', 'PRONOM and Version'],
                    ['C:\\PUID\\file.xhtml', 'XHTML', '1.1', 'https://www.nationalarchives.gov.uk/pronom/fmt/103',
                     'Hypertext Markup Language 1.1', 'htm|html', 'https://www.nationalarchives.gov.uk/pronom/fmt/103',
                     'Low Risk', 'Retain', 'PRONOM and Version'],
                    ['C:\\PUID\\file.oxps', 'Open XML Paper', np.nan,
                     'https://www.nationalarchives.gov.uk/pronom/fmt/657',
                     'Microsoft XML Paper Specification 1.0', 'xps',
                     'https://www.nationalarchives.gov.uk/pronom/fmt/657',
                     'Moderate Risk', 'Transform to PDF or possibly OXPS', 'PRONOM'],
                    ['C:\\PUID\\file.oxps', 'Open XML Paper', np.nan,
                     'https://www.nationalarchives.gov.uk/pronom/fmt/657',
                     'Open XML Paper Specification', 'oxps', 'https://www.nationalarchives.gov.uk/pronom/fmt/657',
                     'Low Risk', 'Further research is required, possibly transform to PDF, or retain as OXPS',
                     'PRONOM']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with PUID, multiple matches')

    def test_puid_name(self):
        """
        Test for files that match a single PUID and format name combination in the NARA spreadsheet.
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """
        # Creates test input.
        df_fits = csv_to_dataframe(os.path.join('test_combined_fits', 'puid_name_fits.csv'))
        df_nara = csv_to_dataframe(c.NARA)

        # Runs the function being tested and converts the resulting dataframe to a list, including the column headers.
        df_results = match_nara_risk(df_fits, df_nara)
        result = [df_results.columns.to_list()] + df_results.values.tolist()

        # Creates a list with the expected result.
        expected = [['FITS_File_Path', 'FITS_Format_Name', 'FITS_Format_Version', 'FITS_PUID', 'NARA_Format Name',
                     'NARA_File Extension(s)', 'NARA_PRONOM URL', 'NARA_Risk Level', 'NARA_Proposed Preservation Plan',
                     'NARA_Match_Type'],
                    ['C:\\PUID\\file.e00', 'ESRI ArcInfo Interchange File Format', np.nan,
                     'https://www.nationalarchives.gov.uk/pronom/x-fmt/235',
                     'ESRI ArcInfo Interchange File Format', 'e00',
                     'https://www.nationalarchives.gov.uk/pronom/x-fmt/235',
                     'Moderate Risk', 'Transform to KML, ESRI Shapefile, and/or GML as appropriate', 'PRONOM and Name'],
                    ['C:\\PUID\\file.m2p', 'MPEG-2 Program Stream', np.nan,
                     'https://www.nationalarchives.gov.uk/pronom/x-fmt/386',
                     'MPEG-2 Program Stream', 'm2p|mpg|mpeg', 'https://www.nationalarchives.gov.uk/pronom/x-fmt/386',
                     'Low Risk', 'Retain', 'PRONOM and Name']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with PUID and Name')

    def test_puid_single(self):
        """
        Test for files that match a single PUID, but not format name or version, in the NARA spreadsheet.
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """
        # Creates test input.
        df_fits = csv_to_dataframe(os.path.join('test_combined_fits', 'puid_single_fits.csv'))
        df_nara = csv_to_dataframe(c.NARA)

        # Runs the function being tested and converts the resulting dataframe to a list, including the column headers.
        df_results = match_nara_risk(df_fits, df_nara)
        result = [df_results.columns.to_list()] + df_results.values.tolist()

        # Creates a list with the expected result.
        expected = [['FITS_File_Path', 'FITS_Format_Name', 'FITS_Format_Version', 'FITS_PUID', 'NARA_Format Name',
                     'NARA_File Extension(s)', 'NARA_PRONOM URL', 'NARA_Risk Level', 'NARA_Proposed Preservation Plan',
                     'NARA_Match_Type'],
                    ['C:\\PUID\\file.cdx', 'CorelDraw', np.nan, 'https://www.nationalarchives.gov.uk/pronom/x-fmt/31',
                     'CorelDraw Compressed Drawing', 'cdx', 'https://www.nationalarchives.gov.uk/pronom/x-fmt/31',
                     'High Risk', 'Transform to a TBD format, possibly PDF or TIFF', 'PRONOM'],
                    ['C:\\PUID\\file.dng', 'Digital Negative 1.0', np.nan,
                     'https://www.nationalarchives.gov.uk/pronom/fmt/436',
                     'Digital Negative Format 1.0', 'dng', 'https://www.nationalarchives.gov.uk/pronom/fmt/436',
                     'Low Risk', 'Retain', 'PRONOM']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with PUID, single match')

    def test_puid_version(self):
        """
        Test for files that match a single PUID and format version combination in the NARA spreadsheet.
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """
        # Creates test input.
        df_fits = csv_to_dataframe(os.path.join('test_combined_fits', 'puid_version_fits.csv'))
        df_nara = csv_to_dataframe(c.NARA)

        # Runs the function being tested and converts the resulting dataframe to a list, including the column headers.
        df_results = match_nara_risk(df_fits, df_nara)
        result = [df_results.columns.to_list()] + df_results.values.tolist()

        # Creates a list with the expected result.
        expected = [['FITS_File_Path', 'FITS_Format_Name', 'FITS_Format_Version', 'FITS_PUID', 'NARA_Format Name',
                     'NARA_File Extension(s)', 'NARA_PRONOM URL', 'NARA_Risk Level', 'NARA_Proposed Preservation Plan',
                     'NARA_Match_Type'],
                    ['C:\\PUID\\file.css', 'CSS', '2.0', 'https://www.nationalarchives.gov.uk/pronom/x-fmt/224',
                     'Cascading Style Sheets 2.0', 'css', 'https://www.nationalarchives.gov.uk/pronom/x-fmt/224',
                     'Low Risk', 'Retain', 'PRONOM and Version'],
                    ['C:\\PUID\\file.html', 'HTML', '5.1', 'https://www.nationalarchives.gov.uk/pronom/fmt/96',
                     'Hypertext Markup Language 5.1', 'htm|html', 'https://www.nationalarchives.gov.uk/pronom/fmt/96',
                     'Low Risk', 'Retain', 'PRONOM and Version']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with PUID and Version')

    def test_unspecified_extension_version(self):
        """
        Test for files that match a file extension and version combination in the NARA spreadsheet.
        The FITS version is blank and the NARA version is "unspecified version".
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """
        # Creates test input.
        df_fits = csv_to_dataframe(os.path.join('test_combined_fits', 'unspecified_extension_version_fits.csv'))
        df_nara = csv_to_dataframe(c.NARA)

        # Runs the function being tested and converts the resulting dataframe to a list, including the column headers.
        df_results = match_nara_risk(df_fits, df_nara)
        result = [df_results.columns.to_list()] + df_results.values.tolist()

        # Creates a list with the expected result.
        expected = [['FITS_File_Path', 'FITS_Format_Name', 'FITS_Format_Version', 'FITS_PUID', 'NARA_Format Name',
                     'NARA_File Extension(s)', 'NARA_PRONOM URL', 'NARA_Risk Level', 'NARA_Proposed Preservation Plan',
                     'NARA_Match_Type'],
                    ['C:\\unspecified\\file.swf', 'Flash', np.nan, 'https://www.nationalarchives.gov.uk/pronom/fmt/000',
                     'Macromedia Flash unspecified version', 'swf', np.nan, 'Moderate Risk',
                     'Transform to MP4 if possible, otherwise retain', 'File Extension'],
                    ['C:\\unspecified\\file.rtf', 'RTF', np.nan, 'https://www.nationalarchives.gov.uk/pronom/fmt/000',
                     'Rich Text Format unspecified version', 'rtf', np.nan, 'Moderate Risk',
                     'Transform to PDF', 'File Extension'],
                    ['C:\\unspecified\\file.css', 'CSS', np.nan, np.nan,
                     'Cascading Style Sheets unspecified version', 'css',
                     'https://www.nationalarchives.gov.uk/pronom/x-fmt/224', 'Low Risk', 'Retain', 'File Extension'],
                    ['C:\\unspecified\\file.gif', 'GIF', np.nan, np.nan,
                     'Graphics Interchange Format unspecified version', 'gif', np.nan, 'Moderate Risk', 'Retain',
                     'File Extension'],
                    ['C:\\unspecified\\file.pdf', 'PDF', np.nan, np.nan,
                     'Adobe Illustrator unspecified version', 'ai|pdf', np.nan, 'Moderate Risk',
                     'Transform to PDF', 'File Extension'],
                    ['C:\\unspecified\\file.pdf', 'PDF', np.nan, np.nan,
                     'Portable Document Format (PDF) unspecified version', 'pdf', np.nan, 'Moderate Risk',
                     'Depends on version, see specific version plan', 'File Extension'],
                    ['C:\\unspecified\\file.pdf', 'PDF', np.nan, np.nan,
                     'Portable Document Format/Archiving (PDF/A) unspecified version', 'pdf', np.nan, 'Low Risk',
                     'Retain', 'File Extension']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with unspecified version, extension and version')

    def test_unspecified_name_version(self):
        """
        Test for files that match a single format name and version combination in the NARA spreadsheet.
        The FITS version is blank and the NARA version is "unspecified version".
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """
        # Creates test input.
        df_fits = csv_to_dataframe(os.path.join('test_combined_fits', 'unspecified_name_version_fits.csv'))
        df_nara = csv_to_dataframe(c.NARA)

        # Runs the function being tested and converts the resulting dataframe to a list, including the column headers.
        df_results = match_nara_risk(df_fits, df_nara)
        result = [df_results.columns.to_list()] + df_results.values.tolist()

        # Creates a list with the expected result.
        expected = [['FITS_File_Path', 'FITS_Format_Name', 'FITS_Format_Version', 'FITS_PUID', 'NARA_Format Name',
                     'NARA_File Extension(s)', 'NARA_PRONOM URL', 'NARA_Risk Level', 'NARA_Proposed Preservation Plan',
                     'NARA_Match_Type'],
                    ['C:\\unspecified\\file.swf', 'Macromedia Flash unspecified version', np.nan,
                     'https://www.nationalarchives.gov.uk/pronom/fmt/000', 'Macromedia Flash unspecified version',
                     'swf', np.nan, 'Moderate Risk', 'Transform to MP4 if possible, otherwise retain',
                     'Format Name'],
                    ['C:\\unspecified\\file.rtf', 'Rich Text Format unspecified version', np.nan,
                     'https://www.nationalarchives.gov.uk/pronom/fmt/000', 'Rich Text Format unspecified version',
                     'rtf', np.nan, 'Moderate Risk', 'Transform to PDF', 'Format Name'],
                    ['C:\\unspecified\\file.css', 'Cascading Style Sheets unspecified version', np.nan,
                     np.nan,
                     'Cascading Style Sheets unspecified version', 'css',
                     'https://www.nationalarchives.gov.uk/pronom/x-fmt/224', 'Low Risk', 'Retain', 'Format Name'],
                    ['C:\\unspecified\\file.gif', 'Graphics Interchange Format unspecified version', np.nan, np.nan,
                     'Graphics Interchange Format unspecified version', 'gif', np.nan, 'Moderate Risk',
                     'Retain', 'Format Name']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with unspecified version, format name and version')

    def test_unspecified_one_match(self):
        """
        Test for files that match a single row in the NARA spreadsheet, which happens to be unspecified version.
        This verifies it works correctly if unspecified version is present but there is nothing to delete.
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """
        # Creates test input.
        df_fits = csv_to_dataframe(os.path.join('test_combined_fits', 'unspecified_one_match_fits.csv'))
        df_nara = csv_to_dataframe(c.NARA)

        # Runs the function being tested and converts the resulting dataframe to a list, including the column headers.
        df_results = match_nara_risk(df_fits, df_nara)
        result = [df_results.columns.to_list()] + df_results.values.tolist()

        # Creates a list with the expected result.
        expected = [['FITS_File_Path', 'FITS_Format_Name', 'FITS_Format_Version', 'FITS_PUID', 'NARA_Format Name',
                     'NARA_File Extension(s)', 'NARA_PRONOM URL', 'NARA_Risk Level', 'NARA_Proposed Preservation Plan',
                     'NARA_Match_Type'],
                    ['C:\\unspecified\\file.wmv', 'Windows Media Video', np.nan,
                     'https://www.nationalarchives.gov.uk/pronom/fmt/133', 'Windows Media Video unspecified version',
                     'wmv', 'https://www.nationalarchives.gov.uk/pronom/fmt/133', 'Moderate Risk', 'Transform to AVI',
                     'PRONOM'],
                    ['C:\\unspecified\\file.wpd', 'WordPerfect unspecified version', np.nan, np.nan,
                     'WordPerfect unspecified version', 'wpd', np.nan, 'Moderate Risk', 'Transform to PDF',
                     'Format Name'],
                    ['C:\\unspecified\\file.pict', 'Mac PICT', np.nan, np.nan, 'Macintosh PICT unspecified version',
                     'pict|pct|pic', 'https://www.nationalarchives.gov.uk/pronom/x-fmt/80', 'Moderate Risk',
                     'Transform to PNG or JPEG', 'File Extension']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with unspecified version, one match')

    def test_unspecified_puid_version(self):
        """
        Test for files that match a single PUID and version combination in the NARA spreadsheet.
        The FITS version is blank and the NARA version is "unspecified version".
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """
        # Creates test input.
        df_fits = csv_to_dataframe(os.path.join('test_combined_fits', 'unspecified_puid_version_fits.csv'))
        df_nara = csv_to_dataframe(c.NARA)

        # Runs the function being tested and converts the resulting dataframe to a list, including the column headers.
        df_results = match_nara_risk(df_fits, df_nara)
        result = [df_results.columns.to_list()] + df_results.values.tolist()

        # Creates a list with the expected result.
        expected = [['FITS_File_Path', 'FITS_Format_Name', 'FITS_Format_Version', 'FITS_PUID', 'NARA_Format Name',
                     'NARA_File Extension(s)', 'NARA_PRONOM URL', 'NARA_Risk Level', 'NARA_Proposed Preservation Plan',
                     'NARA_Match_Type'],
                    ['C:\\unspecified\\file.css', 'Cascading Style Sheets', np.nan,
                     'https://www.nationalarchives.gov.uk/pronom/x-fmt/224',
                     'Cascading Style Sheets unspecified version', 'css',
                     'https://www.nationalarchives.gov.uk/pronom/x-fmt/224', 'Low Risk', 'Retain', 'PRONOM'],
                    ['C:\\unspecified\\file.html', 'Hypertext Markup Language', np.nan,
                     'https://www.nationalarchives.gov.uk/pronom/fmt/96',
                     'Hypertext Markup Language unspecified version', 'htm|html',
                     'https://www.nationalarchives.gov.uk/pronom/fmt/96', 'Low Risk', 'Retain', 'PRONOM'],
                    ['C:\\unspecified\\file.wmv', 'Windows Media Video', np.nan,
                     'https://www.nationalarchives.gov.uk/pronom/fmt/133', 'Windows Media Video unspecified version',
                     'wmv', 'https://www.nationalarchives.gov.uk/pronom/fmt/133', 'Moderate Risk', 'Transform to AVI',
                     'PRONOM']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with unspecified version, PUID and version')

    def test_unspecified_version_mix(self):
        """
        Test for files that match a single file extension and version in the NARA spreadsheet.
        This includes a format name with a blank version (matches NARA unspecified version), and a numerical version.
        This verifies it does not delete rows for a FITS format name if it has a version number.
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """
        # Creates test input.
        df_fits = csv_to_dataframe(os.path.join('test_combined_fits', 'unspecified_version_mix_fits.csv'))
        df_nara = csv_to_dataframe(c.NARA)

        # Runs the function being tested and converts the resulting dataframe to a list, including the column headers.
        df_results = match_nara_risk(df_fits, df_nara)
        result = [df_results.columns.to_list()] + df_results.values.tolist()

        # Creates a list with the expected result.
        expected = [['FITS_File_Path', 'FITS_Format_Name', 'FITS_Format_Version', 'FITS_PUID', 'NARA_Format Name',
                     'NARA_File Extension(s)', 'NARA_PRONOM URL', 'NARA_Risk Level', 'NARA_Proposed Preservation Plan',
                     'NARA_Match_Type'],
                    ['C:\\unspecified\\file.css', 'Cascading Style Sheets', '2.0',
                     'https://www.nationalarchives.gov.uk/pronom/x-fmt/224', 'Cascading Style Sheets 2.0', 'css',
                     'https://www.nationalarchives.gov.uk/pronom/x-fmt/224', 'Low Risk', 'Retain',
                     'PRONOM and Version'],
                    ['C:\\unspecified\\file.css', 'Cascading Style Sheets', np.nan,
                     'https://www.nationalarchives.gov.uk/pronom/x-fmt/224',
                     'Cascading Style Sheets unspecified version', 'css',
                     'https://www.nationalarchives.gov.uk/pronom/x-fmt/224', 'Low Risk', 'Retain', 'PRONOM'],
                    ['C:\\unspecified\\file.gif', 'Graphics Interchange Format', '87a', np.nan,
                     'Graphics Interchange Format 87a', 'gif', 'https://www.nationalarchives.gov.uk/pronom/fmt/3',
                     'Moderate Risk', 'Retain', 'Format Name'],
                    ['C:\\unspecified\\file.html', 'HTML', '5.1', np.nan, 'Hypertext Markup Language 5.1', 'htm|html',
                     'https://www.nationalarchives.gov.uk/pronom/fmt/96', 'Low Risk', 'Retain',
                     'File Extension and Version'],
                    ['C:\\unspecified\\file.gif', 'Graphics Interchange Format', np.nan, np.nan,
                     'Graphics Interchange Format unspecified version', 'gif', np.nan, 'Moderate Risk', 'Retain',
                     'File Extension'],
                    ['C:\\unspecified\\file.html', 'HTML', np.nan, np.nan,
                     'Hypertext Markup Language unspecified version', 'htm|html',
                     'https://www.nationalarchives.gov.uk/pronom/fmt/96', 'Low Risk', 'Retain', 'File Extension']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with unspecified version and version number')


if __name__ == '__main__':
    unittest.main()
