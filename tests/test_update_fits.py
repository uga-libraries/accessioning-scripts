"""Tests that the FITS folder is correctly updated when files are deleted from and added to the accession folder."""

import os
import shutil
import subprocess
import unittest
import configuration as c
from format_analysis_functions import update_fits


class MyTestCase(unittest.TestCase):

    def setUp(self):
        """
        Makes an accession folder with files and corresponding FITS folder with FITS XML files for testing.
        """
        self.accession_path = os.path.join(os.getcwd(), 'accession')
        self.fits_path = os.path.join(os.getcwd(), 'accession_FITS')

        # Makes an accession folder with files to use for testing.
        os.makedirs('accession\\dir')
        paths = ['double.txt', 'duplicate.txt', 'file.txt', 'dir\\additional.txt', 'dir\\double.txt', 'dir\\duplicate.txt']
        for file_path in paths:
            with open(fr'accession\{file_path}', 'w') as file:
                file.write('Text')

        # Makes FITS XML for the accession to use for testing.
        os.mkdir('accession_FITS')
        subprocess.run(f'"{c.FITS}" -r -i {self.accession_path} -o {self.fits_path}', shell=True)

    def tearDown(self):
        """
        Deletes the accession folder and FITS folder and their contents.
        """
        shutil.rmtree("accession")
        shutil.rmtree("accession_FITS")

    def test_no_change(self):
        """
        Test for running the function after no changes were made.
        Result for testing is the contents of the accession_FITS folder.
        """
        # Runs the function being tested.
        update_fits(self.accession_path, self.fits_path, os.getcwd(), 'accession')

        # Makes lists of the actual results from the test and the expected results.
        results = []
        for root, dirs, files in os.walk("accession_FITS"):
            results.extend(files)
        expected = ['additional.txt.fits.xml', 'double.txt-1.fits.xml', 'double.txt.fits.xml',
                    'duplicate.txt-1.fits.xml', 'duplicate.txt.fits.xml', 'file.txt.fits.xml']

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(results, expected, 'Problem with no change')

    def test_delete_unique(self):
        """
        Test for running the function after deleting files with unique filenames.
        Result for testing is the contents of the accession_FITS folder.
        """
        # Deletes two files from the accession folder and runs the function being tested.
        os.remove(os.path.join('accession', 'file.txt'))
        os.remove(os.path.join('accession', 'dir', 'additional.txt'))
        update_fits(self.accession_path, self.fits_path, os.getcwd(), 'accession')

        # Makes lists of the actual results from the test and the expected results.
        results = []
        for root, dirs, files in os.walk("accession_FITS"):
            results.extend(files)
        expected = ['double.txt-1.fits.xml', 'double.txt.fits.xml', 'duplicate.txt-1.fits.xml', 'duplicate.txt.fits.xml']

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(results, expected, 'Problem with delete unique filenames')

    def test_delete_duplicate(self):
        """
        Test for running the function after deleting files with duplicated filenames (same name, different folders).
        Result for testing is the contents of the accession_FITS folder.
        """
        # Deletes two files from the accession folder and runs the function being tested.
        os.remove(os.path.join('accession', 'double.txt'))
        os.remove(os.path.join('accession', 'dir', 'duplicate.txt'))
        update_fits(self.accession_path, self.fits_path, os.getcwd(), 'accession')

        # Makes lists of the actual results from the test and the expected results.
        results = []
        for root, dirs, files in os.walk("accession_FITS"):
            results.extend(files)
        expected = ['additional.txt.fits.xml', 'double.txt.fits.xml', 'duplicate.txt-1.fits.xml', 'file.txt.fits.xml']

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(results, expected, 'Problem with delete duplicate filenames')

    def test_add_unique(self):
        """
        Test for running the function after adding new files with a name not yet in the accession folder.
        Result for testing is the contents of the accession_FITS folder.
        """
        # Adds one file to the accession folder and runs the function being tested.
        with open(os.path.join('accession', 'new_file.txt'), 'w') as file:
            file.write('New Text')
        with open(os.path.join('accession', 'dir', 'another_new_file.txt'), 'w') as file:
            file.write('New Text')
        update_fits(self.accession_path, self.fits_path, os.getcwd(), 'accession')

        # Makes lists of the actual results from the test and the expected results.
        results = []
        for root, dirs, files in os.walk("accession_FITS"):
            results.extend(files)
        expected = ['additional.txt.fits.xml', 'another_new_file.txt.fits.xml', 'double.txt-1.fits.xml',
                    'double.txt.fits.xml', 'duplicate.txt-1.fits.xml', 'duplicate.txt.fits.xml', 'file.txt.fits.xml',
                    'new_file.txt.fits.xml']

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(results, expected, 'Problem with add unique filenames')


if __name__ == '__main__':
    unittest.main()
