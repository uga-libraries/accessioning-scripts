"""Tests adding technical appraisal categories to df_results, which already has information from FITS and NARA."""
# TODO: not tested

import pandas as pd
import unittest
from format_analysis_functions import csv_to_dataframe, match_technical_appraisal
import configuration as c


class MyTestCase(unittest.TestCase):
    def test_match_technical_appraisal(self):
        # Makes a dataframe to use as input.
        # Data variation: examples that match both, one, or neither of the technical appraisal categories,
        #                 with identical cases and different cases (match is case-insensitive),
        #                 and a folder that contains the word trash but shouldn't be identified for technical appraisal.
        rows = [[r'C:\CD1\Flower.JPG', 'JPEG EXIF'],
                [r'C:\CD1\Trashes\Flower1.JPG', 'JPEG EXIF'],
                [r'C:\CD2\Script\config.pyc', 'unknown binary'],
                [r'C:\CD2\Trash Data\data.zip', 'ZIP Format'],
                [r'C:\CD2\trash\New Document.txt', 'Plain text'],
                [r'C:\CD2\Trash\New Text.txt', 'Plain text'],
                [r'C:\FD1\empty.txt', 'empty'],
                [r'C:\FD1\trashes\program.dll', 'PE32 executable']]
        column_names = ['FITS_File_Path', 'FITS_Format_Name']
        df_results = pd.DataFrame(rows, columns=column_names)

        # Reads the technical appraisal CSV into a dataframe and runs the function being tested.
        df_ita = csv_to_dataframe(c.ITA)
        df_results = match_technical_appraisal(df_results, df_ita)

        # Makes a dataframe with the expected values.
        rows = [[r'C:\CD1\Flower.JPG', 'JPEG EXIF', 'Not for TA'],
                [r'C:\CD1\Trashes\Flower1.JPG', 'JPEG EXIF', 'Trash'],
                [r'C:\CD2\Script\config.pyc', 'unknown binary', 'Format'],
                [r'C:\CD2\Trash Data\data.zip', 'ZIP Format', 'Not for TA'],
                [r'C:\CD2\trash\New Document.txt', 'Plain text', 'Trash'],
                [r'C:\CD2\Trash\New Text.txt', 'Plain text', 'Trash'],
                [r'C:\FD1\empty.txt', 'empty', 'Format'],
                [r'C:\FD1\trashes\program.dll', 'PE32 executable', 'Trash']]
        column_names = ['FITS_File_Path', 'FITS_Format_Name', 'Technical Appraisal']
        df_expected = pd.DataFrame(rows, columns=column_names)

        # Compares the script output to the expected values.
        self.assertEqual(df_results, df_expected, 'Problem with match technical appraisal')


if __name__ == '__main__':
    unittest.main()
