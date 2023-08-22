"""Tests the function get_row, which extracts desired text from a field in a FITS XML file,
combining text if the field is repeated and returning an empty string if it is not present.
In the main script, it is called by fits_row(), so it is implied to work if tests of that function pass.
These tests make it easier to identify the problem with this specific function.

For input, tests use FITS files that are in the tests folder of this script repo.
The result for testing is the string returned by the function.
"""

import os
import unittest
import xml.etree.ElementTree as ET
from format_analysis_functions import get_text


class MyTestCase(unittest.TestCase):

    def test_none(self):
        """
        Test for FITS without any instances of the element.
        """
        # Reads the FITS XML (fits_row function usually does this) for test input.
        fits_file = os.path.join("test_FITS", "get_text_FITS", "element_none.csv.fits.xml")
        ns = {"fits": "http://hul.harvard.edu/ois/xml/ns/fits/fits_output"}
        tree = ET.parse(fits_file)
        root = tree.getroot()
        parent = root.find("fits:fileinfo", ns)

        # Runs the function being tested and saves the result to a variable.
        # In the fits_row function, this would be added to the file_data list.
        result = get_text(parent, "creatingApplicationName")

        # Creates a string with the expected result.
        expected = None

        # Compares the results. assertEqual prints "OK" or the differences between the two strings.
        self.assertEqual(result, expected, "Problem with no matching element")

    def test_one(self):
        """
        Test for FITS with one instance of the element.
        """
        # Reads the FITS XML (fits_row function usually does this) for test input.
        fits_file = os.path.join("test_FITS", "get_text_FITS", "element_one.csv.fits.xml")
        ns = {"fits": "http://hul.harvard.edu/ois/xml/ns/fits/fits_output"}
        tree = ET.parse(fits_file)
        root = tree.getroot()
        parent = root.find("fits:fileinfo", ns)

        # Runs the function being tested and saves the result to a variable.
        # In the fits_row function, this would be added to the file_data list.
        result = get_text(parent, "filepath")

        # Creates a string with the expected result.
        expected = "C:\\accession\\disk1\\element_one.csv"

        # Compares the results. assertEqual prints "OK" or the differences between the two strings.
        self.assertEqual(result, expected, "Problem with one matching element")

    def test_multi(self):
        """
        Test for FITS with two instances of the element.
        """
        # Reads the FITS XML (fits_row function usually does this) for test input.
        fits_file = os.path.join("test_FITS", "get_text_FITS", "element_multi.csv.fits.xml")
        ns = {"fits": "http://hul.harvard.edu/ois/xml/ns/fits/fits_output"}
        tree = ET.parse(fits_file)
        root = tree.getroot()
        parent = root.find("fits:fileinfo", ns)

        # Runs the function being tested and saves the result to a variable.
        # In the fits_row function, this would be added to the file_data list.
        result = get_text(parent, "creatingApplicationName")

        # Creates a string with the expected result.
        expected = "Creating_Tool_Option_One; Creating_Tool_Option_Two"

        # Compares the results. assertEqual prints "OK" or the differences between the two strings.
        self.assertEqual(result, expected, "Problem with multiple matching elements")

    def test_empty_one(self):
        """
        Test for single FITS element that is empty.
        """
        # Reads the FITS XML (fits_row function usually does this) for test input.
        fits_file = os.path.join("test_FITS", "get_text_FITS", "element_empty_one.zip.fits.xml")
        ns = {"fits": "http://hul.harvard.edu/ois/xml/ns/fits/fits_output"}
        tree = ET.parse(fits_file)
        root = tree.getroot()
        parent = root.find("fits:fileinfo", ns)

        # Runs the function being tested and saves the result to a variable.
        # In the fits_row function, this would be added to the file_data list.
        result = get_text(parent, "size")

        # Creates a string with the expected result.
        expected = None

        # Compares the results. assertEqual prints "OK" or the differences between the two strings.
        self.assertEqual(result, expected, "Problem with empty, one instance of element")

    def test_empty_multiple(self):
        """
        Test for multiple FITS elements that are empty.
        """
        # Reads the FITS XML (fits_row function usually does this) for test input.
        fits_file = os.path.join("test_FITS", "get_text_FITS", "element_empty_multi.zip.fits.xml")
        ns = {"fits": "http://hul.harvard.edu/ois/xml/ns/fits/fits_output"}
        tree = ET.parse(fits_file)
        root = tree.getroot()
        parent = root.find("fits:fileinfo", ns)

        # Runs the function being tested and saves the result to a variable.
        # In the fits_row function, this would be added to the file_data list.
        result = get_text(parent, "size")

        # Creates a string with the expected result.
        expected = None

        # Compares the results. assertEqual prints "OK" or the differences between the two strings.
        self.assertEqual(result, expected, "Problem with empty, multiple instances of element")

    def test_nonetype_mix(self):
        """
        Test for mix of FITS elements that are empty and have a value.
        """
        # Reads the FITS XML (fits_row function usually does this) for test input.
        fits_file = os.path.join("test_FITS", "get_text_FITS", "element_empty_mix.zip.fits.xml")
        ns = {"fits": "http://hul.harvard.edu/ois/xml/ns/fits/fits_output"}
        tree = ET.parse(fits_file)
        root = tree.getroot()
        parent = root.find("fits:fileinfo", ns)

        # Runs the function being tested and saves the result to a variable.
        # In the fits_row function, this would be added to the file_data list.
        result = get_text(parent, "size")

        # Creates a string with the expected result.
        expected = "58757"

        # Compares the results. assertEqual prints "OK" or the differences between the two strings.
        self.assertEqual(result, expected, "Problem with empty, mix of empty and has value elements")


if __name__ == '__main__':
    unittest.main()
