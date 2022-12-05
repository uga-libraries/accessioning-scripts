"""Tests making subsets of the dataframe.
This is not a function, but instead a series of pandas filters in the main body of the code."""
# TODO: dataframe comparisons don't work because of index differences
# TODO: Might work better if use one dataframe as input for all the tests.

import numpy as np
import pandas as pd
import unittest


class MyTestCase(unittest.TestCase):

    def test_nara_risk_subset(self):
        """Tests the NARA risk subset, which is based on the NARA_Risk Level column."""

        # Makes a dataframe to use as input.
        # Data variation: all 4 risk levels and all columns to be dropped.
        rows = [[r'C:\Disk1\file.txt', 'Plain text', 'Low Risk', 'drop', 'drop', 'drop', 'drop', 'drop', 'drop'],
                [r'C:\Disk1\photo.jpg', 'JPEG EXIF', 'Low Risk', 'drop', 'drop', 'drop', 'drop', 'drop', 'drop'],
                [r'C:\Disk1\file.psd', 'Adobe Photoshop file', 'Moderate Risk', 'drop', 'drop', 'drop', 'drop', 'drop',
                 'drop'],
                [r'C:\Disk1\file.bak', 'Backup File', 'High Risk', 'drop', 'drop', 'drop', 'drop', 'drop', 'drop'],
                [r'C:\Disk1\new.txt', 'empty', 'No Match', 'drop', 'drop', 'drop', 'drop', 'drop', 'drop']]
        column_names = ['FITS_File_Path', 'FITS_Format_Name', 'NARA_Risk Level', 'FITS_PUID',
                        'FITS_Identifying_Tool(s)',
                        'FITS_Creating_Application', 'FITS_Valid', 'FITS_Well-Formed', 'FITS_Status_Message']
        df_results = pd.DataFrame(rows, columns=column_names)

        # Runs the code being tested (from the main body of the script).
        df_nara_risk = df_results[df_results['NARA_Risk Level'] != 'Low Risk'].copy()
        df_nara_risk.drop(['FITS_PUID', 'FITS_Identifying_Tool(s)', 'FITS_Creating_Application',
                           'FITS_Valid', 'FITS_Well-Formed', 'FITS_Status_Message'], inplace=True, axis=1)

        # Makes a dataframe with the expected values.
        rows = [[r'C:\Disk1\file.psd', 'Adobe Photoshop file', 'Moderate Risk'],
                [r'C:\Disk1\file.bak', 'Backup File', 'High Risk'],
                [r'C:\Disk1\new.txt', 'empty', 'No Match']]
        column_names = ['FITS_File_Path', 'FITS_Format_Name', 'NARA_Risk Level']
        df_expected = pd.DataFrame(rows, columns=column_names)

        # Compares the code output to the expected values.
        # Using pandas test functionality because unittest assertEqual is unable to compare dataframes.
        pd.testing.assert_frame_equal(df_nara_risk, df_expected)

    def test_multiple_ids_subset(self):
        """Tests the files with multiple FITs format ids subset, which is based on the FITS_File_Path column."""

        # Makes a dataframe to use as input.
        # Data variation: files with multiple ids and files without; all columns to be dropped.
        rows = [[r'C:\Disk1\file1.txt', 'Plain text', False, 'drop', 'drop', 'drop'],
                [r'C:\Disk1\file2.html', 'Hypertext Markup Language', True, 'drop', 'drop', 'drop'],
                [r'C:\Disk1\file2.html', 'HTML Transitional', True, 'drop', 'drop', 'drop'],
                [r'C:\Disk1\file3.xlsx', 'Open Office XML Document', True, 'drop', 'drop', 'drop'],
                [r'C:\Disk1\file3.xlsx', 'Open Office XML Workbook', True, 'drop', 'drop', 'drop'],
                [r'C:\Disk1\file3.xlsx', 'XLSX', True, 'drop', 'drop', 'drop'],
                [r'C:\Disk1\photo.jpg', 'JPEG EXIF', False, 'drop', 'drop', 'drop']]
        column_names = ['FITS_File_Path', 'FITS_Format_Name', 'FITS_Multiple_IDs',
                        'FITS_Valid', 'FITS_Well-Formed', 'FITS_Status_Message']
        df_results = pd.DataFrame(rows, columns=column_names)

        # Runs the code being tested (from the main body of the script).
        df_multiple = df_results[df_results.duplicated('FITS_File_Path', keep=False) == True].copy()
        df_multiple.drop(['FITS_Valid', 'FITS_Well-Formed', 'FITS_Status_Message'], inplace=True, axis=1)

        # Makes a dataframe with the expected values.
        rows = [[r'C:\Disk1\file2.html', 'Hypertext Markup Language', True],
                [r'C:\Disk1\file2.html', 'HTML Transitional', True],
                [r'C:\Disk1\file3.xlsx', 'Open Office XML Document', True],
                [r'C:\Disk1\file3.xlsx', 'Open Office XML Workbook', True],
                [r'C:\Disk1\file3.xlsx', 'XLSX', True]]
        column_names = ['FITS_File_Path', 'FITS_Format_Name', 'FITS_Multiple_IDs']
        df_expected = pd.DataFrame(rows, columns=column_names)

        # Compares the code output to the expected values.
        # Using pandas test functionality because unittest assertEqual is unable to compare dataframes.
        pd.testing.assert_frame_equal(df_multiple, df_expected)

    def test_validation_subset(self):
        """Tests the FITS validation subset, which is based on the FITS_Valid, FITS_Well-Formed,
        and FITS_Status_Message columns."""

        # Makes a dataframe to use as input.
        # Data variation: values in 0, 1, 2, or 3 columns will include the file in the validation subset.
        # Some of these combinations probably wouldn't happen in real data, but want to be thorough.
        rows = [[r'C:\Disk1\file1.txt', 'Plain text', True, True, np.NaN],
                [r'C:\Disk1\file2.html', 'Hypertext Markup Language', np.NaN, np.NaN, np.NaN],
                [r'C:\Disk1\file2.html', 'HTML Transitional', False, True, np.NaN],
                [r'C:\Disk1\file3.xlsx', 'Open Office XML Document', True, False, np.NaN],
                [r'C:\Disk1\file3.xlsx', 'Open Office XML Workbook', True, True, 'Validation Error'],
                [r'C:\Disk1\file3.xlsx', 'XLSX', False, False, np.NaN],
                [r'C:\Disk1\photo.jpg', 'JPEG EXIF', True, False, 'Validation Error'],
                [r'C:\Disk1\photo1.jpg', 'JPEG EXIF', False, True, 'Validation Error'],
                [r'C:\Disk1\photo2.jpg', 'JPEG EXIF', False, False, 'Validation Error']]
        column_names = ['FITS_File_Path', 'FITS_Format_Name', 'FITS_Valid', 'FITS_Well-Formed', 'FITS_Status_Message']
        df_results = pd.DataFrame(rows, columns=column_names)

        # Runs the code being tested (from the main body of the script).
        df_validation = df_results[(df_results['FITS_Valid'] == False) | (df_results['FITS_Well-Formed'] == False) |
                                   (df_results['FITS_Status_Message'].notnull())].copy()

        # Makes a dataframe with the expected values.
        rows = [[r'C:\Disk1\file2.html', 'HTML Transitional', False, True, np.NaN],
                [r'C:\Disk1\file3.xlsx', 'Open Office XML Document', True, False, np.NaN],
                [r'C:\Disk1\file3.xlsx', 'Open Office XML Workbook', True, True, 'Validation Error'],
                [r'C:\Disk1\file3.xlsx', 'XLSX', False, False, np.NaN],
                [r'C:\Disk1\photo.jpg', 'JPEG EXIF', True, False, 'Validation Error'],
                [r'C:\Disk1\photo1.jpg', 'JPEG EXIF', False, True, 'Validation Error'],
                [r'C:\Disk1\photo2.jpg', 'JPEG EXIF', False, False, 'Validation Error']]
        column_names = ['FITS_File_Path', 'FITS_Format_Name', 'FITS_Valid', 'FITS_Well-Formed', 'FITS_Status_Message']
        df_expected = pd.DataFrame(rows, columns=column_names)

        # Compares the code output to the expected values.
        # Using pandas test functionality because unittest assertEqual is unable to compare dataframes.
        pd.testing.assert_frame_equal(df_validation, df_expected)

    def test_tech_appraisal_subset(self):
        """Tests the technical appraisal subset, which is based on the Technical_Appraisal column."""

        # Makes a dataframe to use as input.
        # Data variation: all 3 technical appraisal categories and all columns to drop.
        rows = [['DOS/Windows Executable', 'Format', 'drop', 'drop', 'drop', 'drop', 'drop', 'drop'],
                ['JPEG EXIF', 'Not for TA', 'drop', 'drop', 'drop', 'drop', 'drop', 'drop'],
                ['Unknown Binary', 'Format', 'drop', 'drop', 'drop', 'drop', 'drop', 'drop'],
                ['Plain text', 'Not for TA', 'drop', 'drop', 'drop', 'drop', 'drop', 'drop'],
                ['JPEG EXIF', 'Trash', 'drop', 'drop', 'drop', 'drop', 'drop', 'drop'],
                ['Open Office XML Workbook', 'Trash', 'drop', 'drop', 'drop', 'drop', 'drop', 'drop']]
        column_names = ['FITS_Format_Name', 'Technical_Appraisal', 'FITS_PUID', 'FITS_Date_Last_Modified',
                        'FITS_MD5', 'FITS_Valid', 'FITS_Well-Formed', 'FITS_Status_Message']
        df_results = pd.DataFrame(rows, columns=column_names)

        # Runs the code being tested (from the main body of the script).
        df_tech_appraisal = df_results[df_results['Technical_Appraisal'] != 'Not for TA'].copy()
        df_tech_appraisal.drop(['FITS_PUID', 'FITS_Date_Last_Modified', 'FITS_MD5', 'FITS_Valid', 'FITS_Well-Formed',
                                'FITS_Status_Message'], inplace=True, axis=1)

        # Makes a dataframe with the expected values.
        rows = [['DOS/Windows Executable', 'Format'],
                ['Unknown Binary', 'Format'],
                ['JPEG EXIF', 'Trash'],
                ['Open Office XML Workbook', 'Trash']]
        column_names = ['FITS_Format_Name', 'Technical_Appraisal']
        df_expected = pd.DataFrame(rows, columns=column_names)

        # Compares the code output to the expected values.
        # Using pandas test functionality because unittest assertEqual is unable to compare dataframes.
        pd.testing.assert_frame_equal(df_tech_appraisal, df_expected)

    def test_other_risk_subset(self):
        """Tests the other risk subset, which is based on the Other_Risk column."""

        # Makes a dataframe to use as input.
        # Data variation: all other risk categories and all columns to drop.
        rows = [['DOS/Windows Executable', 'Not for Other', 'drop', 'drop', 'drop', 'drop', 'drop', 'drop', 'drop'],
                ['Adobe Photoshop file', 'Layered image file', 'drop', 'drop', 'drop', 'drop', 'drop', 'drop', 'drop'],
                ['JPEG EXIF', 'Not for Other', 'drop', 'drop', 'drop', 'drop', 'drop', 'drop', 'drop'],
                ['Cascading Style Sheet', 'Possible saved web page', 'drop', 'drop', 'drop', 'drop', 'drop', 'drop',
                 'drop'],
                ['iCalendar', 'NARA Low/Transform', 'drop', 'drop', 'drop', 'drop', 'drop', 'drop', 'drop'],
                ['Zip Format', 'Archive format', 'drop', 'drop', 'drop', 'drop', 'drop', 'drop', 'drop']]
        column_names = ['FITS_Format_Name', 'Other_Risk', 'FITS_PUID', 'FITS_Date_Last_Modified', 'FITS_MD5',
                        'FITS_Creating_Application', 'FITS_Valid', 'FITS_Well-Formed', 'FITS_Status_Message']
        df_results = pd.DataFrame(rows, columns=column_names)

        # Runs the code being tested (from the main body of the script).
        df_other_risk = df_results[df_results['Other_Risk'] != 'Not for Other'].copy()
        df_other_risk.drop(
            ['FITS_PUID', 'FITS_Date_Last_Modified', 'FITS_MD5', 'FITS_Creating_Application', 'FITS_Valid',
             'FITS_Well-Formed', 'FITS_Status_Message'], inplace=True, axis=1)

        # Makes a dataframe with the expected values.
        rows = [['Adobe Photoshop file', 'Layered image file'],
                ['Cascading Style Sheet', 'Possible saved web page'],
                ['iCalendar', 'NARA Low/Transform'],
                ['Zip Format', 'Archive format']]
        column_names = ['FITS_Format_Name', 'Other_Risk']
        df_expected = pd.DataFrame(rows, columns=column_names)

        # Compares the code output to the expected values.
        # Using pandas test functionality because unittest assertEqual is unable to compare dataframes.
        pd.testing.assert_frame_equal(df_other_risk, df_expected)

    def test_duplicates_subset(self):
        """Tests the duplicates subset, which is based on the FITS_File_Path and FITS_MD5 columns."""

        # Makes a dataframe to use as input.
        # Data variation: unique files, files duplicate because of multiple FITs file ids, and real duplicate files.
        rows = [[r'C:\Disk1\file1.txt', 'Plain text', 0.004, '098f6bcd4621d373cade4e832627b4f6'],
                [r'C:\Disk1\file3.xlsx', 'Open Office XML Document', 19.316, 'b66e2fa385872d1a16d31b00f4b5f035'],
                [r'C:\Disk1\file3.xlsx', 'Open Office XML Workbook', 19.316, 'b66e2fa385872d1a16d31b00f4b5f035'],
                [r'C:\Disk1\file3.xlsx', 'XLSX', 19.316, 'b66e2fa385872d1a16d31b00f4b5f035'],
                [r'C:\Disk1\photo.jpg', 'JPEG EXIF', 13.563, '686779fae835aadff6474898f5781e99'],
                [r'C:\Disk2\file1.txt', 'Plain text', 0.004, '098f6bcd4621d373cade4e832627b4f6'],
                [r'C:\Disk3\file1.txt', 'Plain text', 0.004, '098f6bcd4621d373cade4e832627b4f6']]
        column_names = ['FITS_File_Path', 'FITS_Format_Name', 'FITS_Size_KB', 'FITS_MD5']
        df_results = pd.DataFrame(rows, columns=column_names)

        # Runs the code being tested (from the main body of the script).
        df_duplicates = df_results[['FITS_File_Path', 'FITS_Size_KB', 'FITS_MD5']].copy()
        df_duplicates = df_duplicates.drop_duplicates(subset=['FITS_File_Path'], keep=False)
        df_duplicates = df_duplicates.loc[df_duplicates.duplicated(subset='FITS_MD5', keep=False)]

        # Makes a dataframe with the expected values.
        rows = [[r'C:\Disk1\file1.txt', 0.004, '098f6bcd4621d373cade4e832627b4f6'],
                [r'C:\Disk2\file1.txt', 0.004, '098f6bcd4621d373cade4e832627b4f6'],
                [r'C:\Disk3\file1.txt', 0.004, '098f6bcd4621d373cade4e832627b4f6']]
        column_names = ['FITS_File_Path', 'FITS_Size_KB', 'FITS_MD5']
        df_expected = pd.DataFrame(rows, columns=column_names)

        # Compares the code output to the expected values.
        # Using pandas test functionality because unittest assertEqual is unable to compare dataframes.
        pd.testing.assert_frame_equal(df_duplicates, df_expected)

    def test_empty_subset(self):
        """Tests handling of an empty subset, which can happen with any subset.
        Using the file with multiple format ids and duplicate MD5s subsets for testing."""
        # TODO: split into 2 tests, or does every subset needs an empty test?

        # Makes a dataframe to use as input where all files have a unique identification and unique MD5.
        rows = [[r'C:\Disk1\file1.txt', 'Plain text', 0.004, '098f6bcd4621d373cade4e832627b4f6'],
                [r'C:\Disk1\file2.txt', 'Plain text', 5.347, 'c9f6d785a33cfac2cc1f51ab4704b8a1'],
                [r'C:\Disk2\file3.pdf', 'Portable Document Format', 187.972, '6dfeecf4e4200a0ad147a7271a094e68'],
                [r'c:\Disk2\file4.txt', 'Plain text', 0.178, '97e4f6e6f35e5606855d0917e22740b9']]
        column_names = ['FITS_File_Path', 'FITS_Format_Name', 'FITS_Size_KB', 'FITS_MD5']
        df_results = pd.DataFrame(rows, columns=column_names)

        # Runs the code being tested (from the main body of the script).
        df_multiple_ids = df_results[df_results.duplicated('FITS_File_Path', keep=False) == True].copy()
        df_duplicates = df_results[['FITS_File_Path', 'FITS_Size_KB', 'FITS_MD5']].copy()
        df_duplicates = df_duplicates.drop_duplicates(subset=['FITS_File_Path'], keep=False)
        df_duplicates = df_duplicates.loc[df_duplicates.duplicated(subset='FITS_MD5', keep=False)]
        for df in (df_multiple_ids, df_duplicates):
            if len(df) == 0:
                df.loc[len(df)] = ['No data of this type'] + [np.NaN] * (len(df.columns) - 1)

        # Makes dataframes with the expected values for each subset.
        rows = [['No data of this type', np.NaN, np.NaN, np.NaN]]
        column_names = ['FITS_File_Path', 'FITS_Format_Name', 'FITS_Size_KB', 'FITS_MD5']
        df_multiple_ids_expected = pd.DataFrame(rows, columns=column_names)

        rows = [['No data of this type', np.NaN, np.NaN]]
        column_names = ['FITS_File_Path', 'FITS_Size_KB', 'FITS_MD5']
        df_duplicates_expected = pd.DataFrame(rows, columns=column_names)

        # Compares the code outputs to the expected values.
        # Using pandas test functionality because unittest assertEqual is unable to compare dataframes.
        pd.testing.assert_frame_equal(df_multiple_ids, df_multiple_ids_expected)
        pd.testing.assert_frame_equal(df_duplicates, df_duplicates_expected)


if __name__ == '__main__':
    unittest.main()
