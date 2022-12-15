"""Tests the function match_nara_risk, which combines FITS format identifications with NARA risk information
to produce df_results.

To simplify the testing, df_fits only has the file path, format name, format version, and PUID,
the only columns used by match_nara_risk."""

import numpy as np
import pandas as pd
import unittest
from format_analysis_functions import csv_to_dataframe, match_nara_risk
import configuration as c


class MyTestCase(unittest.TestCase):

    def test_puid_single(self):
        """
        Test for files that match a single PUID in the NARA spreadsheet.
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """
        # Creates test input.
        rows = [['C:\\PUID\\file.ai', 'Adobe Illustrator', '6', 'https://www.nationalarchives.gov.uk/pronom/fmt/422'],
                ['C:\\PUID\\file.psd', 'Adobe Photoshop', np.NaN, 'https://www.nationalarchives.gov.uk/pronom/x-fmt/92']]
        df_fits = pd.DataFrame(rows, columns=['FITS_File_Path', 'FITS_Format_Name', 'FITS_Format_Version', 'FITS_PUID'])
        df_nara = csv_to_dataframe(c.NARA)

        # Runs the function being tested and converts the resulting dataframe to a list.
        df_results = match_nara_risk(df_fits, df_nara)
        result = df_results.values.tolist()

        # Creates a list with the expected result.
        expected = [['C:\\PUID\\file.ai', 'Adobe Illustrator', '6', 'https://www.nationalarchives.gov.uk/pronom/fmt/422',
                     'Adobe Illustrator 6.0', 'ai', 'https://www.nationalarchives.gov.uk/pronom/fmt/422',
                     'Moderate Risk', 'Transform to PDF', 'PRONOM'],
                    ['C:\\PUID\\file.psd', 'Adobe Photoshop', np.NaN, 'https://www.nationalarchives.gov.uk/pronom/x-fmt/92',
                     'Adobe Photoshop', 'psd', 'https://www.nationalarchives.gov.uk/pronom/x-fmt/92',
                     'Moderate Risk', 'Transform to TIFF or JPEG2000', 'PRONOM']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with PUID, single match')

    def test_puid_multiple(self):
        """
        Test for files that match multiple PUIDs in the NARA spreadsheet.
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """
        # Creates test input.
        rows = [['C:\\PUID\\file.html', 'HTML', '1.0', 'https://www.nationalarchives.gov.uk/pronom/fmt/102'],
                ['C:\\PUID\\file.wpd', 'WordPerfect 5.1 for DOS', np.NaN,
                 'https://www.nationalarchives.gov.uk/pronom/x-fmt/394']]
        df_fits = pd.DataFrame(rows, columns=['FITS_File_Path', 'FITS_Format_Name', 'FITS_Format_Version', 'FITS_PUID'])
        df_nara = csv_to_dataframe(c.NARA)

        # Runs the function being tested and converts the resulting dataframe to a list.
        df_results = match_nara_risk(df_fits, df_nara)
        result = df_results.values.tolist()

        # Creates a list with the expected result.
        expected = [['C:\\PUID\\file.html', 'HTML', '1.0', 'https://www.nationalarchives.gov.uk/pronom/fmt/102',
                     'eXtensible Hypertext Markup Language 1.0', 'xhtm|xhtml',
                     'https://www.nationalarchives.gov.uk/pronom/fmt/102', 'Low Risk', 'Retain', 'PRONOM'],
                    ['C:\\PUID\\file.html', 'HTML', '1.0', 'https://www.nationalarchives.gov.uk/pronom/fmt/102',
                     'Hypertext Markup Language 1.0', 'htm|html',
                     'https://www.nationalarchives.gov.uk/pronom/fmt/102', 'Low Risk', 'Retain', 'PRONOM'],
                    ['C:\\PUID\\file.wpd', 'WordPerfect 5.1 for DOS', np.NaN,
                     'https://www.nationalarchives.gov.uk/pronom/x-fmt/394', 'WordPerfect 5.1 for DOS', 'wpd|wp5',
                     'https://www.nationalarchives.gov.uk/pronom/x-fmt/394', 'Moderate Risk', 'Transform to PDF', 'PRONOM'],
                    ['C:\\PUID\\file.wpd', 'WordPerfect 5.1 for DOS', np.NaN,
                     'https://www.nationalarchives.gov.uk/pronom/x-fmt/394', 'WordPerfect 5.1 for Windows',
                     'wpd|wp5', 'https://www.nationalarchives.gov.uk/pronom/x-fmt/394', 'Moderate Risk',
                     'Transform to PDF', 'PRONOM']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with PUID, multiple matches')

    def test_name_version_case(self):
        """
        Test for files that match one name/version combination in the NARA spreadsheet, with the same case.
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """
        # Creates test input.
        rows = [['C:\\NameVer\\file.wk3', 'Lotus 1-2-3 Worksheet', '3.0', ''],
                ['C:\\NameVer\\file.swf', 'Macromedia Flash', '7', '']]
        df_fits = pd.DataFrame(rows, columns=['FITS_File_Path', 'FITS_Format_Name', 'FITS_Format_Version', 'FITS_PUID'])
        df_nara = csv_to_dataframe(c.NARA)

        # Runs the function being tested and converts the resulting dataframe to a list.
        df_results = match_nara_risk(df_fits, df_nara)
        result = df_results.values.tolist()

        # Creates a list with the expected result.
        expected = [['C:\\NameVer\\file.wk3', 'Lotus 1-2-3 Worksheet', '3.0', '', 'Lotus 1-2-3 Worksheet 3.0',
                     'wk3', 'https://www.nationalarchives.gov.uk/pronom/x-fmt/115', 'Moderate Risk',
                     'Transform to CSV or XLSX', 'Format Name'],
                    ['C:\\NameVer\\file.swf', 'Macromedia Flash', '7', '', 'Macromedia Flash 7', 'swf',
                     'https://www.nationalarchives.gov.uk/pronom/fmt/110', 'Moderate Risk', 'Retain', 'Format Name']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with name and version, case match')

    def test_name_version_not_case(self):
        """
        Test for files that match one name/version combination in the NARA spreadsheet, case doesn't match.
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """
        # Creates test input.
        rows = [['C:\\NameVer\\file.wk3', 'lotus 1-2-3 worksheet', '3.0', ''],
                ['C:\\NameVer\\file.swf', 'macromedia flash', '7', '']]
        df_fits = pd.DataFrame(rows, columns=['FITS_File_Path', 'FITS_Format_Name', 'FITS_Format_Version', 'FITS_PUID'])
        df_nara = csv_to_dataframe(c.NARA)

        # Runs the function being tested and converts the resulting dataframe to a list.
        df_results = match_nara_risk(df_fits, df_nara)
        result = df_results.values.tolist()

        # Creates a list with the expected result.
        expected = [['C:\\NameVer\\file.wk3', 'lotus 1-2-3 worksheet', '3.0', '', 'Lotus 1-2-3 Worksheet 3.0',
                     'wk3', 'https://www.nationalarchives.gov.uk/pronom/x-fmt/115', 'Moderate Risk',
                     'Transform to CSV or XLSX', 'Format Name'],
                    ['C:\\NameVer\\file.swf', 'macromedia flash', '7', '', 'Macromedia Flash 7', 'swf',
                     'https://www.nationalarchives.gov.uk/pronom/fmt/110', 'Moderate Risk', 'Retain', 'Format Name']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with name and version, case does not match')

    def test_name_case(self):
        """
        Test for files that match one name (no version) in the NARA spreadsheet, with the same case.
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """
        # Creates test input.
        rows = [['C:\\Name\\file.bat', 'Batch Script', '', ''],
                ['C:\\Name\\file.eml', 'Electronic Mail Format', '', '']]
        df_fits = pd.DataFrame(rows, columns=['FITS_File_Path', 'FITS_Format_Name', 'FITS_Format_Version', 'FITS_PUID'])
        df_nara = csv_to_dataframe(c.NARA)

        # Runs the function being tested and converts the resulting dataframe to a list.
        df_results = match_nara_risk(df_fits, df_nara)
        result = df_results.values.tolist()

        # Creates a list with the expected result.
        expected = [['C:\\Name\\file.bat', 'Batch Script', '', '', 'Batch Script', 'bat|cmd|btm',
                     'https://www.nationalarchives.gov.uk/pronom/x-fmt/413', 'Moderate Risk', 'Retain', 'Format Name'],
                    ['C:\\Name\\file.eml', 'Electronic Mail Format', '', '', 'Electronic Mail Format', 'eml',
                     'https://www.nationalarchives.gov.uk/pronom/fmt/278', 'Low Risk', 'Retain', 'Format Name']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with name, case match')

    def test_name_not_case(self):
        """
        Test for files that match one name (no version) in the NARA spreadsheet, case doesn't match.
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """
        # Creates test input.
        rows = [['C:\\Name\\file.bat', 'batch script', '', ''],
                ['C:\\Name\\file.eml', 'electronic mail format', '', '']]
        df_fits = pd.DataFrame(rows, columns=['FITS_File_Path', 'FITS_Format_Name', 'FITS_Format_Version', 'FITS_PUID'])
        df_nara = csv_to_dataframe(c.NARA)

        # Runs the function being tested and converts the resulting dataframe to a list.
        df_results = match_nara_risk(df_fits, df_nara)
        result = df_results.values.tolist()

        # Creates a list with the expected result.
        expected = [['C:\\Name\\file.bat', 'batch script', '', '', 'Batch Script', 'bat|cmd|btm',
                     'https://www.nationalarchives.gov.uk/pronom/x-fmt/413', 'Moderate Risk', 'Retain', 'Format Name'],
                    ['C:\\Name\\file.eml', 'electronic mail format', '', '', 'Electronic Mail Format', 'eml',
                     'https://www.nationalarchives.gov.uk/pronom/fmt/278', 'Low Risk', 'Retain', 'Format Name']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with name, case does not match')

    def test_name_multiple(self):
        """
        Test for files that match more than one name (no version) in the NARA spreadsheet.
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """
        # Creates test input.
        rows = [['C:\\Name\\file.smil', 'Synchronized Multimedia Integration Language', '', '']]
        df_fits = pd.DataFrame(rows, columns=['FITS_File_Path', 'FITS_Format_Name', 'FITS_Format_Version', 'FITS_PUID'])
        df_nara = csv_to_dataframe(c.NARA)

        # Runs the function being tested and converts the resulting dataframe to a list.
        df_results = match_nara_risk(df_fits, df_nara)
        result = df_results.values.tolist()

        # Creates a list with the expected result.
        expected = [['C:\\Name\\file.smil', 'Synchronized Multimedia Integration Language', '', '',
                     'Synchronized Multimedia Integration Language', 'smi|sami',
                     'https://www.nationalarchives.gov.uk/pronom/fmt/205', 'Low Risk', 'Retain', 'Format Name'],
                    ['C:\\Name\\file.smil', 'Synchronized Multimedia Integration Language', '', '',
                     'Synchronized Multimedia Integration Language', 'smil',
                     'https://www.nationalarchives.gov.uk/pronom/fmt/205', 'Low Risk', 'Retain', 'Format Name']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with name, multiple matches')

    def test_extension_case(self):
        """
        Test for files that match one extension in the NARA spreadsheet, with the same case.
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """
        # Creates test input.
        rows = [['C:\\ext\\file.mxf', 'MXF', '', ''],
                ['C:\\ext\\file.crl', 'Raster', '', '']]
        df_fits = pd.DataFrame(rows, columns=['FITS_File_Path', 'FITS_Format_Name', 'FITS_Format_Version', 'FITS_PUID'])
        df_nara = csv_to_dataframe(c.NARA)

        # Runs the function being tested and converts the resulting dataframe to a list.
        df_results = match_nara_risk(df_fits, df_nara)
        result = df_results.values.tolist()

        # Creates a list with the expected result.
        expected = [['C:\\ext\\file.mxf', 'MXF', '', '', 'Material Exchange Format', 'mxf',
                     'https://www.nationalarchives.gov.uk/pronom/fmt/200', 'Low Risk', 'Retain', 'File Extension'],
                    ['C:\\ext\\file.crl', 'Raster', '', '', 'Intergraph Raster Format', 'crl',
                     'https://www.nationalarchives.gov.uk/pronom/x-fmt/229', 'Moderate Risk', 'Transform to TIFF',
                     'File Extension']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with extension, case match')

    def test_extension_no_case(self):
        """
        Test for files that match one extension in the NARA spreadsheet, case doesn't match.
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """
        # Creates test input.
        rows = [['C:\\ext\\file.MXF', 'MXF', '', ''],
                ['C:\\ext\\file.CRL', 'Raster', '', '']]
        df_fits = pd.DataFrame(rows, columns=['FITS_File_Path', 'FITS_Format_Name', 'FITS_Format_Version', 'FITS_PUID'])
        df_nara = csv_to_dataframe(c.NARA)

        # Runs the function being tested and converts the resulting dataframe to a list.
        df_results = match_nara_risk(df_fits, df_nara)
        result = df_results.values.tolist()

        # Creates a list with the expected result.
        expected = [['C:\\ext\\file.MXF', 'MXF', '', '', 'Material Exchange Format', 'mxf',
                     'https://www.nationalarchives.gov.uk/pronom/fmt/200', 'Low Risk', 'Retain', 'File Extension'],
                    ['C:\\ext\\file.CRL', 'Raster', '', '', 'Intergraph Raster Format', 'crl',
                     'https://www.nationalarchives.gov.uk/pronom/x-fmt/229', 'Moderate Risk', 'Transform to TIFF',
                     'File Extension']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with extension, case does not match')

    def test_extension_pipe_case(self):
        """
        Test for files that match one extension in a piped string in the NARA spreadsheet, case match.
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """
        # Creates test input.
        rows = [['C:\\Ext\\file.gz', 'g-zip', '', ''],
                ['C:\\Ext\\file.fods', 'OpenDocument Spreadsheet', '', '']]
        df_fits = pd.DataFrame(rows, columns=['FITS_File_Path', 'FITS_Format_Name', 'FITS_Format_Version', 'FITS_PUID'])
        df_nara = csv_to_dataframe(c.NARA)

        # Runs the function being tested and converts the resulting dataframe to a list.
        df_results = match_nara_risk(df_fits, df_nara)
        result = df_results.values.tolist()

        # Creates a list with the expected result.
        expected = [['C:\\Ext\\file.gz', 'g-zip', '', '', 'GZIP', 'gz|tgz',
                     'https://www.nationalarchives.gov.uk/pronom/x-fmt/266', 'Low Risk',
                     'Retain but extract files from the container', 'File Extension'],
                    ['C:\\Ext\\file.fods', 'OpenDocument Spreadsheet', '', '', 'OpenDocument Spreadsheet 1.0',
                     'ods|fods', 'https://www.nationalarchives.gov.uk/pronom/fmt/137', 'Low Risk', 'Retain',
                     'File Extension']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with extension (piped), case match')

    def test_extension_pipe_no_case(self):
        """
        Test for files that match one extension in a piped string in the NARA spreadsheet, case doesn't match.
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """
        # Creates test input.
        rows = [['C:\\Ext\\file.GZ', 'g-zip', '', ''],
                ['C:\\Ext\\file.FODS', 'OpenDocument Spreadsheet', '', '']]
        df_fits = pd.DataFrame(rows, columns=['FITS_File_Path', 'FITS_Format_Name', 'FITS_Format_Version', 'FITS_PUID'])
        df_nara = csv_to_dataframe(c.NARA)

        # Runs the function being tested and converts the resulting dataframe to a list.
        df_results = match_nara_risk(df_fits, df_nara)
        result = df_results.values.tolist()

        # Creates a list with the expected result.
        expected = [['C:\\Ext\\file.GZ', 'g-zip', '', '', 'GZIP', 'gz|tgz',
                     'https://www.nationalarchives.gov.uk/pronom/x-fmt/266', 'Low Risk',
                     'Retain but extract files from the container', 'File Extension'],
                    ['C:\\Ext\\file.FODS', 'OpenDocument Spreadsheet', '', '', 'OpenDocument Spreadsheet 1.0',
                     'ods|fods', 'https://www.nationalarchives.gov.uk/pronom/fmt/137', 'Low Risk', 'Retain',
                     'File Extension']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with extension (piped), case does not match')

    def test_extension_multiple(self):
        """
        Test for files that match more than one extension in the NARA spreadsheet.
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """
        # Creates test input.
        rows = [['C:\\Ext\\file.aac', 'MPEG-4', '', ''],
                ['C:\\Ext\\file.CIN', 'Kodak', '', '']]
        df_fits = pd.DataFrame(rows, columns=['FITS_File_Path', 'FITS_Format_Name', 'FITS_Format_Version', 'FITS_PUID'])
        df_nara = csv_to_dataframe(c.NARA)

        # Runs the function being tested and converts the resulting dataframe to a list.
        df_results = match_nara_risk(df_fits, df_nara)
        result = df_results.values.tolist()

        # Creates a list with the expected result.
        expected = [['C:\\Ext\\file.aac', 'MPEG-4', '', '', 'Advanced Audio Coding (AAC) MPEG-2 Audio', 'aac',
                     np.NaN, 'Low Risk', 'Transform to BWF or MP3 as appropriate', 'File Extension'],
                    ['C:\\Ext\\file.aac', 'MPEG-4', '', '', 'Advanced Audio Coding MPEG-4 Low Complexity Object',
                     'aac|mp4|m4a', np.NaN, 'Low Risk', 'Transform to BWF or MP3 as appropriate', 'File Extension'],
                    ['C:\\Ext\\file.aac', 'MPEG-4', '', '', 'MPEG-4 File Format, V.2, with Advanced Audio Coding',
                     'aac', np.NaN, 'Low Risk', 'Transform to BWF or MP3 as appropriate', 'File Extension'],
                    ['C:\\Ext\\file.aac', 'MPEG-4', '', '',
                     'QuickTime [version 6.0 and higher] file with AAC Encoding (qta, aac)', 'qta|aac|m4p', np.NaN,
                     'Moderate Risk', 'Transform to BWF or MP3 as appropriate', 'File Extension'],
                    ['C:\\Ext\\file.CIN', 'Kodak', '', '', 'Kodak Cineon', 'cin', np.NaN, 'High Risk',
                     'Transform to TIFF if possible', 'File Extension'],
                    ['C:\\Ext\\file.CIN', 'Kodak', '', '', 'OS/2 Change Control File', 'cin',
                     'https://www.nationalarchives.gov.uk/pronom/x-fmt/143', 'Moderate Risk', 'Retain', 'File Extension']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with extension, multiple matches')

    def test_no_match(self):
        """
        Test for files that do not match any formats in the NARA spreadsheet.
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """
        # Creates test input.
        rows = [['C:\\None\\file.abc', 'New Format', '', ''],
                ['C:\\None\\file', 'Unknown Binary', '', '']]
        df_fits = pd.DataFrame(rows, columns=['FITS_File_Path', 'FITS_Format_Name', 'FITS_Format_Version', 'FITS_PUID'])
        df_nara = csv_to_dataframe(c.NARA)

        # Runs the function being tested and converts the resulting dataframe to a list.
        df_results = match_nara_risk(df_fits, df_nara)
        result = df_results.values.tolist()

        # Creates a list with the expected result.
        expected = [['C:\\None\\file.abc', 'New Format', '', '', np.NaN, np.NaN, np.NaN, 'No Match', np.NaN,
                     'No NARA Match'],
                    ['C:\\None\\file', 'Unknown Binary', '', '', np.NaN, np.NaN, np.NaN, 'No Match', np.NaN,
                     'No NARA Match']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with no matches')


if __name__ == '__main__':
    unittest.main()
