"""Tests the function match_technical_appraisal, which adds the technical appraisal category to df_results,
based on the filenames, folder names, and ITAfileformats.csv.

To simplify the testing, df_results only has the file path and the format name,
the columns used by match_technical_appraisal."""

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

    def test_not_ta_trash_partial(self):
        """
        Test for files that do not meet any technical appraisal criteria.
        The files are in a folder that contains "trash", but trash is not the entire folder name.
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """
        # Creates test input.
        rows = [['C:\\CD_Trash\\File.txt', 'Plain text'],
                ['C:\\CD_Trash_2\\File.txt', 'Plain text'],
                ['C:\\Trash Pickup\\File2.txt', 'Plain text']]
        df_results = pd.DataFrame(rows, columns=['FITS_File_Path', 'FITS_Format_Name'])
        df_ita = csv_to_dataframe(c.ITA)

        # Runs the function being tested and converts the resulting dataframe to a list, including the column headers.
        df_results = match_technical_appraisal(df_results, df_ita)
        result = [df_results.columns.to_list()] + df_results.values.tolist()

        # Creates a list with the expected result.
        expected = [['FITS_File_Path', 'FITS_Format_Name', 'Technical_Appraisal'],
                    ['C:\\CD_Trash\\File.txt', 'Plain text', 'Not for TA'],
                    ['C:\\CD_Trash_2\\File.txt', 'Plain text', 'Not for TA'],
                    ['C:\\Trash Pickup\\File2.txt', 'Plain text', 'Not for TA']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with not technical appraisal, trash is partial folder name')

    def test_not_ta_period_not_first(self):
        """
        Test for files that do not meet any technical appraisal criteria.
        The filename includes a period but it is not the first character.
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """
        # Creates test input.
        rows = [['C:\\FD1\\file.name.txt', 'Plain text'],
                ['C:\\FD1\\new.txt', 'Plain text']]
        df_results = pd.DataFrame(rows, columns=['FITS_File_Path', 'FITS_Format_Name'])
        df_ita = csv_to_dataframe(c.ITA)

        # Runs the function being tested and converts the resulting dataframe to a list, including the column headers.
        df_results = match_technical_appraisal(df_results, df_ita)
        result = [df_results.columns.to_list()] + df_results.values.tolist()

        # Creates a list with the expected result.
        expected = [['FITS_File_Path', 'FITS_Format_Name', 'Technical_Appraisal'],
                    ['C:\\FD1\\file.name.txt', 'Plain text', 'Not for TA'],
                    ['C:\\FD1\\new.txt', 'Plain text', 'Not for TA']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with not technical appraisal, period is not first character')

    def test_not_ta_tilde_not_first(self):
        """
        Test for files that do not meet any technical appraisal criteria.
        The filename includes a tilde (~) but it is not the first character.
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """
        # Creates test input.
        rows = [['C:\\FD1\\f~ile.txt', 'Plain text'],
                ['C:\\FD1\\new~.txt', 'Plain text']]
        df_results = pd.DataFrame(rows, columns=['FITS_File_Path', 'FITS_Format_Name'])
        df_ita = csv_to_dataframe(c.ITA)

        # Runs the function being tested and converts the resulting dataframe to a list, including the column headers.
        df_results = match_technical_appraisal(df_results, df_ita)
        result = [df_results.columns.to_list()] + df_results.values.tolist()

        # Creates a list with the expected result.
        expected = [['FITS_File_Path', 'FITS_Format_Name', 'Technical_Appraisal'],
                    ['C:\\FD1\\f~ile.txt', 'Plain text', 'Not for TA'],
                    ['C:\\FD1\\new~.txt', 'Plain text', 'Not for TA']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with not technical appraisal, tilde is not first character')

    def test_not_ta_tmp_not_last(self):
        """
        Test for files that do not meet any technical appraisal criteria.
        The filename includes a ".tmp" but they are not the last characters.
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """
        # Creates test input.
        rows = [['C:\\FD1\\file.tmp.txt', 'Plain text'],
                ['C:\\FD1\\new.TMP.txt', 'Plain text']]
        df_results = pd.DataFrame(rows, columns=['FITS_File_Path', 'FITS_Format_Name'])
        df_ita = csv_to_dataframe(c.ITA)

        # Runs the function being tested and converts the resulting dataframe to a list, including the column headers.
        df_results = match_technical_appraisal(df_results, df_ita)
        result = [df_results.columns.to_list()] + df_results.values.tolist()

        # Creates a list with the expected result.
        expected = [['FITS_File_Path', 'FITS_Format_Name', 'Technical_Appraisal'],
                    ['C:\\FD1\\file.tmp.txt', 'Plain text', 'Not for TA'],
                    ['C:\\FD1\\new.TMP.txt', 'Plain text', 'Not for TA']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with not technical appraisal, .tmp are not the last characters')

    def test_not_ta_thumb_partial(self):
        """
        Test for files that do not meet any technical appraisal criteria.
        The filename includes "thumbs.db" but it is not the entire filename.
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """
        # Creates test input.
        rows = [['C:\\FD1\\thumbs.db.txt', 'Plain text'],
                ['C:\\FD1\\all_thumbs.db', 'unknown']]
        df_results = pd.DataFrame(rows, columns=['FITS_File_Path', 'FITS_Format_Name'])
        df_ita = csv_to_dataframe(c.ITA)

        # Runs the function being tested and converts the resulting dataframe to a list, including the column headers.
        df_results = match_technical_appraisal(df_results, df_ita)
        result = [df_results.columns.to_list()] + df_results.values.tolist()

        # Creates a list with the expected result.
        expected = [['FITS_File_Path', 'FITS_Format_Name', 'Technical_Appraisal'],
                    ['C:\\FD1\\thumbs.db.txt', 'Plain text', 'Not for TA'],
                    ['C:\\FD1\\all_thumbs.db', 'unknown', 'Not for TA']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with not technical appraisal, thumbs.db is not the full filename')

    def test_not_ta_format_case(self):
        """
        Test for files that do not meet any technical appraisal criteria.
        The formats are in ITAfileformats.csv, but the case is different and an exact match is required.
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """
        # Creates test input.
        rows = [['C:\\FD1\\doc.txt', 'EMPTY'],
                ['C:\\FD1\\icon.ico', 'ms windows icon resource'],
                ['C:\\FD1\\program.dll', 'PE32 Executable']]
        df_results = pd.DataFrame(rows, columns=['FITS_File_Path', 'FITS_Format_Name'])
        df_ita = csv_to_dataframe(c.ITA)

        # Runs the function being tested and converts the resulting dataframe to a list, including the column headers.
        df_results = match_technical_appraisal(df_results, df_ita)
        result = [df_results.columns.to_list()] + df_results.values.tolist()

        # Creates a list with the expected result.
        expected = [['FITS_File_Path', 'FITS_Format_Name', 'Technical_Appraisal'],
                    ['C:\\FD1\\doc.txt', 'EMPTY', 'Not for TA'],
                    ['C:\\FD1\\icon.ico', 'ms windows icon resource', 'Not for TA'],
                    ['C:\\FD1\\program.dll', 'PE32 Executable', 'Not for TA']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with not technical appraisal, format case does not match')

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

    def test_temp_period(self):
        """
        Test for files that start with a period, which is one criteria for a temp file.
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """
        # Creates test input.
        rows = [['C:\\FD1\\.doc.txt', 'Plain text'],
                ['C:\\FD1\\folder\\.file.txt', 'Plain text']]
        df_results = pd.DataFrame(rows, columns=['FITS_File_Path', 'FITS_Format_Name'])
        df_ita = csv_to_dataframe(c.ITA)

        # Runs the function being tested and converts the resulting dataframe to a list, including the column headers.
        df_results = match_technical_appraisal(df_results, df_ita)
        result = [df_results.columns.to_list()] + df_results.values.tolist()

        # Creates a list with the expected result.
        expected = [['FITS_File_Path', 'FITS_Format_Name', 'Technical_Appraisal'],
                    ['C:\\FD1\\.doc.txt', 'Plain text', 'Temp File'],
                    ['C:\\FD1\\folder\\.file.txt', 'Plain text', 'Temp File']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with temp file: starts with period')

    def test_temp_tilde(self):
        """
        Test for files that start with a tilde (~), which is one criteria for a temp file.
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """
        # Creates test input.
        rows = [['C:\\FD1\\~doc.txt', 'Plain text'],
                ['C:\\FD1\\folder\\~file.txt', 'Plain text']]
        df_results = pd.DataFrame(rows, columns=['FITS_File_Path', 'FITS_Format_Name'])
        df_ita = csv_to_dataframe(c.ITA)

        # Runs the function being tested and converts the resulting dataframe to a list, including the column headers.
        df_results = match_technical_appraisal(df_results, df_ita)
        result = [df_results.columns.to_list()] + df_results.values.tolist()

        # Creates a list with the expected result.
        expected = [['FITS_File_Path', 'FITS_Format_Name', 'Technical_Appraisal'],
                    ['C:\\FD1\\~doc.txt', 'Plain text', 'Temp File'],
                    ['C:\\FD1\\folder\\~file.txt', 'Plain text', 'Temp File']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with temp file: starts with tilde')

    def test_temp_tmp(self):
        """
        Test for files that has a ".tmp" or ".TMP" file extension, which is one criteria for a temp file.
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """
        # Creates test input.
        rows = [['C:\\FD1\\doc.tmp', 'Plain text'],
                ['C:\\FD1\\folder\\file.TMP', 'Plain text']]
        df_results = pd.DataFrame(rows, columns=['FITS_File_Path', 'FITS_Format_Name'])
        df_ita = csv_to_dataframe(c.ITA)

        # Runs the function being tested and converts the resulting dataframe to a list, including the column headers.
        df_results = match_technical_appraisal(df_results, df_ita)
        result = [df_results.columns.to_list()] + df_results.values.tolist()

        # Creates a list with the expected result.
        expected = [['FITS_File_Path', 'FITS_Format_Name', 'Technical_Appraisal'],
                    ['C:\\FD1\\doc.tmp', 'Plain text', 'Temp File'],
                    ['C:\\FD1\\folder\\file.TMP', 'Plain text', 'Temp File']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with temp file: .tmp file extension')

    def test_temp_thumb(self):
        """
        Test for files that are Thumbs.db or thumbs.db, which is one criteria for a temp file.
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """
        # Creates test input.
        rows = [['C:\\FD1\\Thumbs.db', 'unknown'],
                ['C:\\FD1\\folder\\thumbs.db', 'unknown']]
        df_results = pd.DataFrame(rows, columns=['FITS_File_Path', 'FITS_Format_Name'])
        df_ita = csv_to_dataframe(c.ITA)

        # Runs the function being tested and converts the resulting dataframe to a list, including the column headers.
        df_results = match_technical_appraisal(df_results, df_ita)
        result = [df_results.columns.to_list()] + df_results.values.tolist()

        # Creates a list with the expected result.
        expected = [['FITS_File_Path', 'FITS_Format_Name', 'Technical_Appraisal'],
                    ['C:\\FD1\\Thumbs.db', 'unknown', 'Temp File'],
                    ['C:\\FD1\\folder\\thumbs.db', 'unknown', 'Temp File']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with temp file: thumbs.db')

    def test_format(self):
        """
        Test for files that match a format for technical appraisal.
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
        self.assertEqual(result, expected, 'Problem with format')

    def test_temp_and_format(self):
        """
        Test for files that meet criteria for Temp File and Format.
        When a file matches both of these categories, Temp File is applied.
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """
        # Creates test input.
        rows = [['C:\\FD1\\.doc.txt', 'empty'],
                ['C:\\FD1\\folder\\.file.txt', 'empty']]
        df_results = pd.DataFrame(rows, columns=['FITS_File_Path', 'FITS_Format_Name'])
        df_ita = csv_to_dataframe(c.ITA)

        # Runs the function being tested and converts the resulting dataframe to a list, including the column headers.
        df_results = match_technical_appraisal(df_results, df_ita)
        result = [df_results.columns.to_list()] + df_results.values.tolist()

        # Creates a list with the expected result.
        expected = [['FITS_File_Path', 'FITS_Format_Name', 'Technical_Appraisal'],
                    ['C:\\FD1\\.doc.txt', 'empty', 'Temp File'],
                    ['C:\\FD1\\folder\\.file.txt', 'empty', 'Temp File']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with temp file and format')

    def test_trash_and_temp(self):
        """
        Test for files that meet criteria for Trash and Temp File.
        When a file matches both categories, Trash is applied.
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """
        # Creates test input.
        rows = [['C:\\FD1\\trash\\.doc.txt', 'Plain text'],
                ['C:\\FD1\\Trashes\\.file.txt', 'Plain text']]
        df_results = pd.DataFrame(rows, columns=['FITS_File_Path', 'FITS_Format_Name'])
        df_ita = csv_to_dataframe(c.ITA)

        # Runs the function being tested and converts the resulting dataframe to a list, including the column headers.
        df_results = match_technical_appraisal(df_results, df_ita)
        result = [df_results.columns.to_list()] + df_results.values.tolist()

        # Creates a list with the expected result.
        expected = [['FITS_File_Path', 'FITS_Format_Name', 'Technical_Appraisal'],
                    ['C:\\FD1\\trash\\.doc.txt', 'Plain text', 'Trash'],
                    ['C:\\FD1\\Trashes\\.file.txt', 'Plain text', 'Trash']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with trash and temp file')

    def test_trash_and_format(self):
        """
        Test for files that meet criteria for Trash and Format.
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
        self.assertEqual(result, expected, 'Problem with trash and format')

    def test_trash_and_temp_and_format(self):
        """
        Test for files that meet criteria for Trash, Temp File, and Format.
        When a file matches all three categories, Trash is applied.
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """
        # Creates test input.
        rows = [['C:\\FD1\\trash\\.doc.txt', 'empty'],
                ['C:\\FD1\\Trashes\\folder\\.file.txt', 'empty']]
        df_results = pd.DataFrame(rows, columns=['FITS_File_Path', 'FITS_Format_Name'])
        df_ita = csv_to_dataframe(c.ITA)

        # Runs the function being tested and converts the resulting dataframe to a list, including the column headers.
        df_results = match_technical_appraisal(df_results, df_ita)
        result = [df_results.columns.to_list()] + df_results.values.tolist()

        # Creates a list with the expected result.
        expected = [['FITS_File_Path', 'FITS_Format_Name', 'Technical_Appraisal'],
                    ['C:\\FD1\\trash\\.doc.txt', 'empty', 'Trash'],
                    ['C:\\FD1\\Trashes\\folder\\.file.txt', 'empty', 'Trash']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with trash and temp file and format')


if __name__ == '__main__':
    unittest.main()
