"""Tests that the FITS folder is correctly updated when files are deleted from and added to the accession folder."""

import os
import pandas as pd
import shutil
import subprocess
import unittest
import configuration as c
from format_analysis_functions import update_fits


class MyTestCase(unittest.TestCase):

    def test_update_fits(self):
        """Tests that the FITS folder is correctly updated when files are deleted from and added to the accession folder."""

        # Makes an accession folder with files.
        os.makedirs(r"accession\dir")
        paths = ["file.txt", "delete.txt", r"dir\delete.txt", r"dir\delete2.txt", r"dir\file.txt", r"dir\spare.txt"]
        for file_path in paths:
            with open(fr"accession\{file_path}", "w") as file:
                file.write("Text")

        # Makes FITS XML for the accession to use for testing.
        # In format_analysis.py, this is done in the main body of the script.
        os.mkdir('accession_FITS')
        subprocess.run(f'"{c.FITS}" -r -i {os.path.join(os.getcwd(), "accession")} -o {os.path.join(os.getcwd(), "accession_FITS")}', shell=True)

        # Deletes 2 files and adds 1 file to the accession folder.
        os.remove(r"accession\delete.txt")
        os.remove(r"accession\dir\delete2.txt")
        with open(r"accession\new_file.txt", "w") as file:
            file.write("Text")

        # RUNS THE FUNCTION BEING TESTED.
        update_fits(os.path.join(os.getcwd(), 'accession'), os.path.join(os.getcwd(), 'accession_FITS'), os.getcwd(), 'accession')

        # Makes a dataframe with the files which should be in the FITs folder.
        expected = ["delete.txt-1.fits.xml", "file.txt-1.fits.xml", "file.txt.fits.xml", "new_file.txt.fits.xml",
                    "spare.txt.fits.xml"]
        df_expected = pd.DataFrame(expected, columns=["Files"])

        # Makes a dataframe with the files that are in the FITS folder.
        fits_files = []
        for root, dirs, files in os.walk("accession_FITS"):
            fits_files.extend(files)
        df_fits_files = pd.DataFrame(fits_files, columns=["Files"])

        # Deletes the test files.
        shutil.rmtree("accession")
        shutil.rmtree("accession_FITS")

        # Compares the contents of the FITS folder to the expected values.
        # Using pandas test functionality because unittest assertEqual is unable to compare dataframes.
        pd.testing.assert_frame_equal(df_fits_files, df_expected)


if __name__ == '__main__':
    unittest.main()
