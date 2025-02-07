"""Tests the function fits_row, which extracts desired fields from a FITS XML file, reformatting when necessary,
for each format identification. In the main script, it is called by make_fits_csv(), so it is implied to work
if tests of that function pass. These tests make it easier to identify the problem with this specific function.

For input, tests use FITS files that are in the tests folder of this script repo.
"""

import datetime
import os
import unittest
from format_analysis_functions import fits_row


class MyTestCase(unittest.TestCase):

    def test_empty_version(self):
        """
        Test for FITS for a file with an empty version.
        Requires catching the TypeError from concat when making the dictionary key.
        Result for testing is the list returned by the function.
        """
        # Runs the function being tested.
        fits_output = os.path.join('test_FITS', 'fits_row_FITS')
        fits_xml = 'empty_version.csv.fits.xml'
        result = fits_row(os.path.join(fits_output, fits_xml))

        # Creates a list with the expected result.
        expected = [['C:\\accession\\disk1\\empty_version.csv', 'Comma-Separated Values (CSV)', None,
                     'https://www.nationalarchives.gov.uk/PRONOM/x-fmt/18',
                     'Droid version 6.4', False, datetime.date(2022, 12, 14), 6002.01,
                     'f95a4c954014342e4bf03f51fcefaecd', None, None, None, None]]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with empty version')

    def test_puid(self):
        """
        Test for FITS with a PUID, which is reformatted.
        Result for testing is the list returned by the function.
        """
        # Runs the function being tested.
        fits_output = os.path.join('test_FITS', 'fits_row_FITS')
        fits_xml = 'puid.csv.fits.xml'
        result = fits_row(os.path.join(fits_output, fits_xml))

        # Creates a list with the expected result.
        expected = [['C:\\accession\\disk1\\puid.csv', 'Comma-Separated Values (CSV)', None,
                     'https://www.nationalarchives.gov.uk/PRONOM/x-fmt/18', 'Droid version 6.4', False,
                     datetime.date(2022, 12, 14), 6002.01, 'f95a4c954014342e4bf03f51fcefaecd',
                     None, None, None, None]]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with PUID')

    def test_multiple_tools(self):
        """
        Test for FITS with more than one tool, which are combined into a single string.
        Result for testing is the list returned by the function.
        """
        # Runs the function being tested.
        fits_output = os.path.join('test_FITS', 'fits_row_FITS')
        fits_xml = 'tools.txt.fits.xml'
        result = fits_row(os.path.join(fits_output, fits_xml))

        # Creates a list with the expected result.
        expected = [['C:\\accession\\disk1\\tools.txt', 'Plain text', None,
                     'https://www.nationalarchives.gov.uk/PRONOM/x-fmt/111',
                     'Droid version 6.4; Jhove version 1.20.1; file utility version 5.03', False,
                     datetime.date(2022, 12, 14), 2, '7b71af3fdf4a2f72a378e3e77815e497',
                     None, 'true', 'true', None]]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with multiple tools')

    def test_multi_keep_all(self):
        """
        Test for FITS with multiple format identifications, where all should be included.
        Result for testing is the list returned by the function.
        """
        # Runs the function being tested.
        fits_output = os.path.join('test_FITS', 'fits_row_FITS')
        fits_xml = 'multi_keep_all.xlsx.fits.xml'
        result = fits_row(os.path.join(fits_output, fits_xml))

        # Creates a list with the expected result.
        expected = [['C:\\accession\\disk1\\multi_keep_all.xlsx', 'ZIP Format', '2.0',
                     'https://www.nationalarchives.gov.uk/PRONOM/x-fmt/263',
                     'Droid version 6.4; file utility version 5.03; ffident version 0.2', True,
                     datetime.date(2022, 12, 14), 20.56, 'db4c3079e3805469c1b47c4864234e66', 'Microsoft Excel',
                     None, None, None],
                    ['C:\\accession\\disk1\\multi_keep_all.xlsx', 'XLSX', None, None, 'Exiftool version 11.54',
                     True, datetime.date(2022, 12, 14), 20.56, 'db4c3079e3805469c1b47c4864234e66',
                     'Microsoft Excel', None, None, None],
                    ['C:\\accession\\disk1\\multi_keep_all.xlsx', 'Office Open XML Workbook', None, None,
                     'Tika version 1.21', True, datetime.date(2022, 12, 14), 20.56,
                     'db4c3079e3805469c1b47c4864234e66', 'Microsoft Excel', None, None, None]]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with multiple format ids - keep all')

    def test_multi_keep_empty(self):
        """
        Test for FITS with multiple format identifications, where just the empty id should be included.
        Result for testing is the list returned by the function.
        """
        # Runs the function being tested.
        fits_output = os.path.join('test_FITS', 'fits_row_FITS')
        fits_xml = 'multi_keep_empty.txt.fits.xml'
        result = fits_row(os.path.join(fits_output, fits_xml))

        # Creates a list with the expected result.
        expected = [['C:\\accession\\disk2\\multi_keep_empty.txt', 'empty', None, None,
                     'file utility version 5.03', False, datetime.date(2022, 12, 14), 0,
                     'd41d8cd98f00b204e9800998ecf8427e', None, None, None, None]]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with multiple format ids - keep empty')

    def test_multi_keep_puid(self):
        """
        Test for FITS with multiple format identifications, where just the one with a PUID should be included.
        Result for testing is the list returned by the function.
        """
        # Runs the function being tested.
        fits_output = os.path.join('test_FITS', 'fits_row_FITS')
        fits_xml = 'multi_keep_puid.gz.fits.xml'
        result = fits_row(os.path.join(fits_output, fits_xml))

        # Creates a list with the expected result.
        expected = [['C:\\accession\\disk2\\multi_keep_puid.gz', 'GZIP Format', None,
                     'https://www.nationalarchives.gov.uk/PRONOM/x-fmt/266',
                     'Droid version 6.4; Tika version 1.21', False, datetime.date(2022, 12, 14), 1.993,
                     '6749b0ec1fbc96faab1a1f98dd7b8a74', None, None, None, None]]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with multiple format ids - keep PUID')

    def test_size_less(self):
        """
        Test for FITS for a file with a size that is too small to round (less than 0.001).
        Result for testing is the list returned by the function.
        """
        # Runs the function being tested.
        fits_output = os.path.join('test_FITS', 'fits_row_FITS')
        fits_xml = 'size_less.txt.fits.xml'
        result = fits_row(os.path.join(fits_output, fits_xml))

        # Creates a list with the expected result.
        expected = [['C:\\accession\\disk2\\size_less.txt', 'Plain text', None,
                     'https://www.nationalarchives.gov.uk/PRONOM/x-fmt/111',
                     'Droid version 6.4; Jhove version 1.20.1; file utility version 5.03', False,
                     datetime.date(2022, 12, 14), .000345, 'e700d0871d44af1a217f0bf32320f25c',
                     None, 'true', 'true', None]]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with size less than rounding threshold')

    def test_size_equal(self):
        """
        Test for FITS for a file with a size that is too small to round (equal to 0.001).
        Result for testing is the list returned by the function.
        """
        # Runs the function being tested.
        fits_output = os.path.join('test_FITS', 'fits_row_FITS')
        fits_xml = 'size_equal.html.fits.xml'
        result = fits_row(os.path.join(fits_output, fits_xml))

        # Creates a list with the expected result.
        expected = [['C:\\accession\\disk2\\size_equal.html', 'Extensible Markup Language', '1.0',
                     None, 'Jhove version 1.20.1', False, datetime.date(2022, 12, 14), .001,
                     'e080b3394eaeba6b118ed15453e49a34', None, 'true', 'true',
                     'Not able to determine type of end of line severity=info']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with size equal to rounding threshold')

    def test_size_greater(self):
        """
        Test for FITS for a file with a size large enough to round.
        Result for testing is the list returned by the function.
        """
        # Runs the function being tested.
        fits_output = os.path.join('test_FITS', 'fits_row_FITS')
        fits_xml = 'size_greater.csv.fits.xml'
        result = fits_row(os.path.join(fits_output, fits_xml))

        # Creates a list with the expected result.
        expected = [['C:\\accession\\disk1\\size_greater.csv', 'Comma-Separated Values (CSV)', None,
                     'https://www.nationalarchives.gov.uk/PRONOM/x-fmt/18',
                     'Droid version 6.4', False, datetime.date(2022, 12, 14), 4.404,
                     'd5e857a4bd33d2b5a2f96b78ccffe1f3', None, None, None, None]]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with size large enough to round')


if __name__ == '__main__':
    unittest.main()
