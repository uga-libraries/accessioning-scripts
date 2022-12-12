"""Tests the command for making FITS files when there is not already a folder of FITs XML from a previous script
iteration. Tests the error handling for FITS when it is in a different directory than the source files.
For this test to work, the fits.bat file must be in the specified location. """
# TODO: this code isn't in functions.

import os
import pandas as pd
import shutil
import subprocess
import unittest
import configuration as c


class MyTestCase(unittest.TestCase):
    def test_make_fits(self):
        """Tests the command for making FITS files when there is not already a folder of FITs XML
            from a previous script iteration."""

        # Makes an accession folder with files to use for testing.
        os.makedirs(os.path.join('accession', 'folder'))
        for file_path in ("file.txt", r"folder\file.txt", r"folder\other.txt"):
            with open(fr"accession\{file_path}", "w") as file:
                file.write("Text")

        # RUNS THE CODE BEING TESTED.
        # Makes the directory for FITS files and calls FITS to make the FITS XML files.
        # In format_analysis.py, this is done in the main body of the script after testing that the folder doesn't exist
        # and also exits the script if there is an error.
        os.mkdir('accession_FITS')
        subprocess.run(f'"{c.FITS}" -r -i "{os.path.join("accession", "folder")}" -o "accession_FITS"', shell=True, stderr=subprocess.PIPE)

        # Makes a dataframe with the files that should be in the accession_FITS folder.
        df_expected = pd.DataFrame(["file.txt.fits.xml", "file.txt-1.fits.xml", "other.txt.fits.xml"],
                                   columns=["Files"])

        # Makes a dataframe with the files that are actually in the accession_fits folder after running the test.
        fits_files = []
        for root, dirs, files in os.walk("accession_FITS"):
            fits_files.extend(files)
        df_fits_files = pd.DataFrame(fits_files, columns=["Files"])

        # Deletes the test files.
        shutil.rmtree("accession")
        shutil.rmtree("accession_FITS")

        # Compares the contents of the FITS folder to the expected values.
        self.assertEqual(df_fits_files, df_expected, 'Problem with make fits')

    def test_fits_class_error(self):
        """Tests the error handling for FITS when it is in a different directory than the source files.
            For this test to work, the fits.bat file must be in the specified location."""

        # Makes an accession folder with files to use for testing.
        os.mkdir('accession')
        with open(fr"accession\file.txt", "w") as file:
            file.write("Text")

        # Makes a variable with a FITS file path in a different directory from the accession folder.
        # In format_analysis.py, the FITS path is taken from the configuration.py file.
        fits_path = r"X:\test\fits.bat"

        # RUNS THE CODE BEING TESTED.
        # Makes the directory for FITS files and calls FITS to make the FITS XML files.
        # In format_analysis.py, this is done in the main body of the script after testing that the folder doesn't exist.
        os.mkdir("accession_FITS")
        fits_result = subprocess.run(f'"{fits_path}" -r -i "accession" -o ""accession_FITS""',
                                     shell=True, stderr=subprocess.PIPE)

        # Deletes the test files.
        shutil.rmtree("accession")
        shutil.rmtree("accession_FITS")

        # Compares the error message generated by the script to the expected value.
        result = fits_result.stderr.decode("utf-8")
        expected = "Error: Could not find or load main class edu.harvard.hul.ois.fits.Fits\r\n"
        self.assertEqual(result, expected, 'Problem with fits class error')


if __name__ == '__main__':
    unittest.main()