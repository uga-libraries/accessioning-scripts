"""Tests the function match_technical_appraisal, which adds the technical appraisal type to df_results,
based on the folder names and ITAfileformats.csv.

To simplify the testing, df_results only has the file path and the format name,
the only columns used by match_technical_appraisal."""

import pandas as pd
import unittest
from format_analysis_functions import csv_to_dataframe, match_technical_appraisal
import configuration as c


class MyTestCase(unittest.TestCase):

    def test_not_ta(self):
        """
        Test for files that do not meet any technical appraisal criteria.
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """
        # Creates test input.
        rows = [['C:\\CD1\\File.txt', 'Plain text'], 
                ['C:\\CD1\\File2.txt', 'Plain text']]
        df_results = pd.DataFrame(rows, columns=['FITS_File_Path', 'FITS_Format_Name'])
        df_ita = csv_to_dataframe(c.ITA)

        # Runs the function being tested and converts the resulting dataframe to a list, including the column headers.
        df_results = match_technical_appraisal(df_results, df_ita)
        result = [df_results.columns.to_list()] + df_results.values.tolist()

        # Creates a list with the expected result.
        expected = [['FITS_File_Path', 'FITS_Format_Name', 'Technical_Appraisal'],
                    ['C:\\CD1\\File.txt', 'Plain text', 'Not for TA'],
                    ['C:\\CD1\\File2.txt', 'Plain text', 'Not for TA']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with not technical appraisal')

    def test_not_ta_or_trash(self):
        """
        Test for files that do not meet any technical appraisal criteria, including a folder that
        contains the string "Trash" but it is not the entire folder name, so it isn't matched.
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """
        # Creates test input.
        rows = [['C:\\CD_Trash\\File.txt', 'Plain text'],
                ['C:\\CD_Trash_2\\File.txt', 'Plain text'],
                ['C:\\Trash_Pickup\\File2.txt', 'Plain text']]
        df_results = pd.DataFrame(rows, columns=['FITS_File_Path', 'FITS_Format_Name'])
        df_ita = csv_to_dataframe(c.ITA)

        # Runs the function being tested and converts the resulting dataframe to a list, including the column headers.
        df_results = match_technical_appraisal(df_results, df_ita)
        result = [df_results.columns.to_list()] + df_results.values.tolist()

        # Creates a list with the expected result.
        expected = [['FITS_File_Path', 'FITS_Format_Name', 'Technical_Appraisal'],
                    ['C:\\CD_Trash\\File.txt', 'Plain text', 'Not for TA'],
                    ['C:\\CD_Trash_2\\File.txt', 'Plain text', 'Not for TA'],
                    ['C:\\Trash_Pickup\\File2.txt', 'Plain text', 'Not for TA']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with not technical appraisal - trash as partial folder name')

    def test_format_case_match(self):
        """
        Test for files that match a format for technical appraisal criteria,
        including matching the case and the entire format name.
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """
        # Creates test input.
        rows = [['C:\\FD1\\doc.txt', 'empty'],
                ['C:\\FD1\\icon.ico', 'MS Windows icon resource'],
                ['C:\\FD1\\program.dll', 'PE32 executable'],
                ['C:\\FD1\\unknown', 'Unknown Binary']]
        df_results = pd.DataFrame(rows, columns=['FITS_File_Path', 'FITS_Format_Name'])
        df_ita = csv_to_dataframe(c.ITA)

        # Runs the function being tested and converts the resulting dataframe to a list, including the column headers.
        df_results = match_technical_appraisal(df_results, df_ita)
        result = [df_results.columns.to_list()] + df_results.values.tolist()

        # Creates a list with the expected result.
        expected = [['FITS_File_Path', 'FITS_Format_Name', 'Technical_Appraisal'],
                    ['C:\\FD1\\doc.txt', 'empty', 'Format'],
                    ['C:\\FD1\\icon.ico', 'MS Windows icon resource', 'Format'],
                    ['C:\\FD1\\program.dll', 'PE32 executable', 'Format'],
                    ['C:\\FD1\\unknown', 'Unknown Binary', 'Format']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with format, case matches')

    def test_format_case_match_partial(self):
        """
        Test for files that match a format for technical appraisal criteria, where the case matches
        and only partially matching the format string.
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """
        # Creates test input.
        rows = [['C:\\FD1\\new.txt', 'empty file'],
                ['C:\\FD1\\unknown', 'Error/Unknown Binary']]
        df_results = pd.DataFrame(rows, columns=['FITS_File_Path', 'FITS_Format_Name'])
        df_ita = csv_to_dataframe(c.ITA)

        # Runs the function being tested and converts the resulting dataframe to a list, including the column headers.
        df_results = match_technical_appraisal(df_results, df_ita)
        result = [df_results.columns.to_list()] + df_results.values.tolist()

        # Creates a list with the expected result.
        expected = [['FITS_File_Path', 'FITS_Format_Name', 'Technical_Appraisal'],
                    ['C:\\FD1\\new.txt', 'empty file', 'Format'],
                    ['C:\\FD1\\unknown', 'Error/Unknown Binary', 'Format']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with format, case matches, partial string')

    def test_format_case_no_match(self):
        """
        Test for files that match a format for technical appraisal criteria, where case does not match.
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """
        # Creates test input.
        rows = [['C:\\FD1\\doc.txt', 'EMPTY'],
                ['C:\\FD1\\icon.ico', 'ms windows icon resource'],
                ['C:\\FD1\\program.dll', 'PE32 Executable'],
                ['C:\\FD1\\unknown', 'unknown binary']]
        df_results = pd.DataFrame(rows, columns=['FITS_File_Path', 'FITS_Format_Name'])
        df_ita = csv_to_dataframe(c.ITA)

        # Runs the function being tested and converts the resulting dataframe to a list, including the column headers.
        df_results = match_technical_appraisal(df_results, df_ita)
        result = [df_results.columns.to_list()] + df_results.values.tolist()

        # Creates a list with the expected result.
        expected = [['FITS_File_Path', 'FITS_Format_Name', 'Technical_Appraisal'],
                    ['C:\\FD1\\doc.txt', 'EMPTY', 'Format'],
                    ['C:\\FD1\\icon.ico', 'ms windows icon resource', 'Format'],
                    ['C:\\FD1\\program.dll', 'PE32 Executable', 'Format'],
                    ['C:\\FD1\\unknown', 'unknown binary', 'Format']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with format, case does not match')

    def test_format_case_no_match_partial(self):
        """
        Test for files that match a format for technical appraisal criteria, where case does not match
        and only partially matching the format string.
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """
        # Creates test input.
        rows = [['C:\\FD1\\new.txt', 'EMPTYFILE'],
                ['C:\\FD1\\unknown', 'error/unknown binary']]
        df_results = pd.DataFrame(rows, columns=['FITS_File_Path', 'FITS_Format_Name'])
        df_ita = csv_to_dataframe(c.ITA)

        # Runs the function being tested and converts the resulting dataframe to a list, including the column headers.
        df_results = match_technical_appraisal(df_results, df_ita)
        result = [df_results.columns.to_list()] + df_results.values.tolist()

        # Creates a list with the expected result.
        expected = [['FITS_File_Path', 'FITS_Format_Name', 'Technical_Appraisal'],
                    ['C:\\FD1\\new.txt', 'EMPTYFILE', 'Format'],
                    ['C:\\FD1\\unknown', 'error/unknown binary', 'Format']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with format, case does not match, partial string')

    def test_trash(self):
        """
        Test for files that are in a folder named "trash".
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """
        # Creates test input.
        rows = [['C:\\CD1\\trash\\File.txt', 'Plain text'],
                ['C:\\CD1\\trash\\File2.txt', 'Plain text']]
        df_results = pd.DataFrame(rows, columns=['FITS_File_Path', 'FITS_Format_Name'])
        df_ita = csv_to_dataframe(c.ITA)

        # Runs the function being tested and converts the resulting dataframe to a list, including the column headers.
        df_results = match_technical_appraisal(df_results, df_ita)
        result = [df_results.columns.to_list()] + df_results.values.tolist()

        # Creates a list with the expected result.
        expected = [['FITS_File_Path', 'FITS_Format_Name', 'Technical_Appraisal'],
                    ['C:\\CD1\\trash\\File.txt', 'Plain text', 'Trash'],
                    ['C:\\CD1\\trash\\File2.txt', 'Plain text', 'Trash']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with trash folder')

    def test_Trash(self):
        """
        Test for files that are in a folder named "Trash".
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """
        # Creates test input.
        rows = [['C:\\CD1\\Trash\\File.txt', 'Plain text'],
                ['C:\\CD1\\Trash\\File2.txt', 'Plain text']]
        df_results = pd.DataFrame(rows, columns=['FITS_File_Path', 'FITS_Format_Name'])
        df_ita = csv_to_dataframe(c.ITA)

        # Runs the function being tested and converts the resulting dataframe to a list, including the column headers.
        df_results = match_technical_appraisal(df_results, df_ita)
        result = [df_results.columns.to_list()] + df_results.values.tolist()

        # Creates a list with the expected result.
        expected = [['FITS_File_Path', 'FITS_Format_Name', 'Technical_Appraisal'],
                    ['C:\\CD1\\Trash\\File.txt', 'Plain text', 'Trash'],
                    ['C:\\CD1\\Trash\\File2.txt', 'Plain text', 'Trash']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with Trash folder')

    def test_trashes(self):
        """
        Test for files that are in a folder named "trashes".
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """
        # Creates test input.
        rows = [['C:\\CD1\\trashes\\File.txt', 'Plain text'],
                ['C:\\CD1\\trashes\\File2.txt', 'Plain text']]
        df_results = pd.DataFrame(rows, columns=['FITS_File_Path', 'FITS_Format_Name'])
        df_ita = csv_to_dataframe(c.ITA)

        # Runs the function being tested and converts the resulting dataframe to a list, including the column headers.
        df_results = match_technical_appraisal(df_results, df_ita)
        result = [df_results.columns.to_list()] + df_results.values.tolist()

        # Creates a list with the expected result.
        expected = [['FITS_File_Path', 'FITS_Format_Name', 'Technical_Appraisal'],
                    ['C:\\CD1\\trashes\\File.txt', 'Plain text', 'Trash'],
                    ['C:\\CD1\\trashes\\File2.txt', 'Plain text', 'Trash']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with trashes folder')

    def test_Trashes(self):
        """
        Test for files that are in a folder named "Trashes".
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """
        # Creates test input.
        rows = [['C:\\CD1\\Trashes\\File.txt', 'Plain text'],
                ['C:\\CD1\\Trashes\\File2.txt', 'Plain text']]
        df_results = pd.DataFrame(rows, columns=['FITS_File_Path', 'FITS_Format_Name'])
        df_ita = csv_to_dataframe(c.ITA)

        # Runs the function being tested and converts the resulting dataframe to a list, including the column headers.
        df_results = match_technical_appraisal(df_results, df_ita)
        result = [df_results.columns.to_list()] + df_results.values.tolist()

        # Creates a list with the expected result.
        expected = [['FITS_File_Path', 'FITS_Format_Name', 'Technical_Appraisal'],
                    ['C:\\CD1\\Trashes\\File.txt', 'Plain text', 'Trash'],
                    ['C:\\CD1\\Trashes\\File2.txt', 'Plain text', 'Trash']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with Trashes folder')

    def test_format_and_trash(self):
        """
        Test for files that are in a folder named "trash" and the format is in the ITAfileformats.csv spreadsheet.
        When a file matches both categories, Trash is applied.
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """
        # Creates test input.
        rows = [['C:\\CD1\\Trash\\program.bat', 'DOS batch file'],
                ['C:\\CD1\\Trash\\font.ttf', 'TTF/TrueType Font']]
        df_results = pd.DataFrame(rows, columns=['FITS_File_Path', 'FITS_Format_Name'])
        df_ita = csv_to_dataframe(c.ITA)

        # Runs the function being tested and converts the resulting dataframe to a list, including the column headers.
        df_results = match_technical_appraisal(df_results, df_ita)
        result = [df_results.columns.to_list()] + df_results.values.tolist()

        # Creates a list with the expected result.
        expected = [['FITS_File_Path', 'FITS_Format_Name', 'Technical_Appraisal'],
                    ['C:\\CD1\\Trash\\program.bat', 'DOS batch file', 'Trash'],
                    ['C:\\CD1\\Trash\\font.ttf', 'TTF/TrueType Font', 'Trash']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with format and trash')


if __name__ == '__main__':
    unittest.main()
