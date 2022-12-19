"""Tests the code from the main body of the script which makes subsets of the dataframe using pandas filters."""

import numpy as np
import pandas as pd
import unittest


class MyTestCase(unittest.TestCase):

    def test_nara_risk_subset(self):
        """
        Test for the NARA risk subset, which includes any file that is not 'Low Risk'.
        Result for testing is the dataframe created by the filter, converted to a list for an easier comparison.
        """
        # Reads test data into a dataframe (located in the tests folder of the script repo).
        df_results = pd.read_csv('for_subset_tests.csv')

        # Runs the code being tested.
        df_nara_risk = df_results[df_results['NARA_Risk Level'] != 'Low Risk'].copy()
        df_nara_risk.drop(['FITS_PUID', 'FITS_Identifying_Tool(s)', 'FITS_Creating_Application',
                           'FITS_Valid', 'FITS_Well-Formed', 'FITS_Status_Message'], inplace=True, axis=1)
        if len(df_nara_risk) == 0:
            df_nara_risk = pd.DataFrame([['No data of this type']])

        # Converts the resulting dataframe to a list, including the column headers.
        result = [df_nara_risk.columns.to_list()] + df_nara_risk.values.tolist()

        # Creates a list with the expected result. 
        expected = [['FITS_File_Path', 'FITS_Format_Name', 'FITS_Format_Version', 'FITS_Multiple_IDs',
                     'FITS_Date_Last_Modified', 'FITS_Size_KB', 'FITS_MD5', 'NARA_Risk Level',
                     'NARA_Proposed Preservation Plan', 'NARA_Match_Type', 'Technical_Appraisal', 'Other_Risk'],
                    ['C:\\CD1\\file.bak', 'Backup File', np.NaN, False, '5/5/2022', 1.23,
                     'ab1e0b017c8eex694eb379e354571234', 'High Risk', 'Retain', 'Format Name', 'Not for TA', 'Not for Other'],
                    ['C:\\CD1\\file.psd', 'Adobe Photoshop file', np.NaN, True, '5/5/2022', 57.01,
                     'le1b6b058c8rrb684ex370e354572936', 'Moderate Risk', 'Transform to TIFF or JPEG2000', 'PRONOM',
                     'Not for TA', 'Layered image file'],
                    ['C:\\CD1\\file.psd', 'Adobe Photoshop file', '1', True, '5/5/2022', 57.01,
                     'le1b6b058c8rrb684ex370e354572936', 'Moderate Risk', 'Transform to TIFF or JPEG2000', 'PRONOM',
                     'Not for TA', 'Layered image file'],
                    ['C:\\CD1\\file.psd', 'Adobe Photoshop file', '1', True, '5/5/2022', 57.01,
                     'le1b6b058c8rrb684ex370e354572936', 'Moderate Risk', 'Transform to TIFF or JPEG2000',
                     'File Extension', 'Not for TA', 'Layered image file'],
                    ['C:\\FD1\\Worksheets.zip', 'ZIP Format', '2', False, '8/25/2022', 11.374,
                     'b335c9b47034466907b169e04cbbfa', 'Moderate Risk', 'Retain but extract files from the container',
                     'PRONOM', 'Not for TA', 'Archive format'],
                    ['C:\\FD2\\Worksheets.zip', 'ZIP Format', '2', False, '8/25/2022', 11.374,
                     'b335c9b47034466907b169e04cbbfa', 'Moderate Risk', 'Retain but extract files from the container',
                     'PRONOM', 'Not for TA', 'Archive format'],
                    ['C:\\FD3\\file.gif', 'GIF', np.NaN, False, '8/25/2022', 0.345, 'c336c9r47814577018b169e04cxxwf',
                     'Moderate Risk', 'Retain', 'File Extension', 'Not for TA', 'Not for Other']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with NARA risk subset')

    def test_nara_risk_subset_empty(self):
        """
        Test for the NARA risk subset, when there are no files matching the criteria for this subset.
        This happens when all files are 'Low Risk'
        Result for testing is the dataframe created by the filter, converted to a list for an easier comparison.
        """
        # Reads test data into a dataframe (located in the tests folder of the script repo).
        df_results = pd.read_csv('for_subset_empty_tests.csv')

        # Runs the code being tested.
        df_nara_risk = df_results[df_results['NARA_Risk Level'] != 'Low Risk'].copy()
        df_nara_risk.drop(['FITS_PUID', 'FITS_Identifying_Tool(s)', 'FITS_Creating_Application',
                           'FITS_Valid', 'FITS_Well-Formed', 'FITS_Status_Message'], inplace=True, axis=1)
        if len(df_nara_risk) == 0:
            df_nara_risk = pd.DataFrame([['No data of this type']])

        # Converts the resulting dataframe to a list, including the column headers.
        result = [df_nara_risk.columns.to_list()] + df_nara_risk.values.tolist()

        # Creates a list with the expected result.
        expected = [[0], ['No data of this type']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with NARA risk subset when empty')

    def test_multiple_ids_subset(self):
        """
        Test for the multiple ids subset, which includes any file with more than one format identification from FITS.
        Result for testing is the dataframe created by the filter, converted to a list for an easier comparison.
        """
        # Reads test data into a dataframe (located in the tests folder of the script repo).
        df_results = pd.read_csv('for_subset_tests.csv')

        # Runs the code being tested.
        df_multiple = df_results[df_results.duplicated('FITS_File_Path', keep=False) == True].copy()
        df_multiple.drop(['FITS_Valid', 'FITS_Well-Formed', 'FITS_Status_Message', 'NARA_Risk Level',
                          'NARA_Proposed Preservation Plan', 'NARA_Match_Type'], inplace=True, axis=1)
        df_multiple.drop_duplicates(inplace=True)
        if len(df_multiple) == 0:
            df_multiple = pd.DataFrame([['No data of this type']])

        # Converts the resulting dataframe to a list, including the column headers.
        result = [df_multiple.columns.to_list()] + df_multiple.values.tolist()

        # Creates a list with the expected result.
        expected = [['FITS_File_Path', 'FITS_Format_Name', 'FITS_Format_Version', 'FITS_PUID',
                     'FITS_Identifying_Tool(s)', 'FITS_Multiple_IDs', 'FITS_Date_Last_Modified', 'FITS_Size_KB',
                     'FITS_MD5', 'FITS_Creating_Application', 'Technical_Appraisal', 'Other_Risk'],
                    ['C:\\CD1\\file.psd', 'Adobe Photoshop file', np.NaN,
                     'https://www.nationalarchives.gov.uk/pronom/x-fmt/92', 'file utility version 5.03', True,
                     '5/5/2022', 57.01, 'le1b6b058c8rrb684ex370e354572936', np.NaN, 'Not for TA', 'Layered image file'],
                    ['C:\\CD1\\file.psd', 'Adobe Photoshop file', '1',
                     'https://www.nationalarchives.gov.uk/pronom/x-fmt/92', 'Droid version 6.4', True, '5/5/2022',
                     57.01, 'le1b6b058c8rrb684ex370e354572936', np.NaN, 'Not for TA', 'Layered image file'],
                    ['C:\\CD1\\file.psd', 'Adobe Photoshop file', '1', np.NaN, 'Tika version 1.21', True, '5/5/2022',
                     57.01, 'le1b6b058c8rrb684ex370e354572936', np.NaN, 'Not for TA', 'Layered image file'],
                    ['C:\\CD2\\overview-summary.html', 'HTML Transitional', 'HTML 4.01', np.NaN, 'Jhove version 1.20.1',
                     True, '5/5/2022', 7.496, '1fcd29526b78728d69e0b0487223fe43', np.NaN, 'Not for TA', 'Not for Other'],
                    ['C:\\CD2\\overview-summary.html', 'Hypertext Markup Language', '4.01',
                     'https://www.nationalarchives.gov.uk/pronom/fmt/1', 'Droid version 6.4; file utility version 5.03',
                     True, '5/5/2022', 7.496, '1fcd29526b78728d69e0b0487223fe43', np.NaN, 'Not for TA', 'Not for Other'],
                    ['C:\\CD2\\overview-tree.html', 'HTML Transitional', 'HTML 4.01', np.NaN, 'Jhove version 1.20.1',
                     True, '5/5/2022', 28.38, 'fd50cd9e7ab6551cd726b49021f0c439', np.NaN, 'Not for TA', 'Not for Other'],
                    ['C:\\CD2\\overview-tree.html', 'Hypertext Markup Language', '4.01',
                     'https://www.nationalarchives.gov.uk/pronom/fmt/1', 'Droid version 6.4; file utility version 5.03',
                     True, '5/5/2022', 28.38, 'fd50cd9e7ab6551cd726b49021f0c439', np.NaN, 'Not for TA', 'Not for Other'],
                    ['C:\\FD1\\Worksheet Excel Version.xlsx', 'Office Open XML Document', '27 onwards',
                     'https://www.nationalarchives.gov.uk/pronom/fmt/189', 'Droid version 6.4', True, '5/5/2022',
                     15.766, 'e0aeaee6f3046bf5568c8076522d83a5', 'Microsoft Excel', 'Not for TA', 'Not for Other'],
                    ['C:\\FD1\\Worksheet Excel Version.xlsx', 'Office Open XML Workbook', np.NaN, np.NaN,
                     'Tika version 1.21', True, '5/5/2022', 15.766, 'e0aeaee6f3046bf5568c8076522d83a5',
                     'Microsoft Excel', 'Not for TA', 'Not for Other'],
                    ['C:\\FD1\\Worksheet Excel Version.xlsx', 'XLSX', np.NaN, np.NaN, 'Exiftool version 11.54', True,
                     '5/5/2022', 15.766, 'e0aeaee6f3046bf5568c8076522d83a5', 'Microsoft Excel', 'Not for TA', 'Not for Other'],
                    ['C:\\FD3\\file.gif', 'GIF', np.NaN, np.NaN, 'Droid version 6.4; file utility version 5.03', False,
                     '8/25/2022', 0.345, 'c336c9r47814577018b169e04cxxwf', np.NaN, 'Not for TA', 'Not for Other']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with multiple ids subset')

    def test_multiple_ids_subset_empty(self):
        """
        Test for the multiple ids subset, when there are no files matching the criteria for this subset.
        This happens when all files had one format identification from FITS.
        Result for testing is the dataframe created by the filter, converted to a list for an easier comparison.
        """
        # Reads test data into a dataframe (located in the tests folder of the script repo).
        df_results = pd.read_csv('for_subset_empty_tests.csv')

        # Runs the code being tested.
        df_multiple = df_results[df_results.duplicated('FITS_File_Path', keep=False) == True].copy()
        df_multiple.drop(['FITS_Valid', 'FITS_Well-Formed', 'FITS_Status_Message', 'NARA_Risk Level',
                          'NARA_Proposed Preservation Plan', 'NARA_Match_Type'], inplace=True, axis=1)
        df_multiple.drop_duplicates(inplace=True)
        if len(df_multiple) == 0:
            df_multiple = pd.DataFrame([['No data of this type']])

        # Converts the resulting dataframe to a list, including the column headers.
        result = [df_multiple.columns.to_list()] + df_multiple.values.tolist()

        # Creates a list with the expected result.
        expected = [[0], ['No data of this type']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with multiple ids subset when empty')

    def test_validation_subset(self):
        """
        Test for the FITS validation subset, which includes any file where FITS had Valid equal to False,
        Well-Formed equal to False, or any text in the Status Message.
        Result for testing is the dataframe created by the filter, converted to a list for an easier comparison.
        """
        # Reads test data into a dataframe (located in the tests folder of the script repo).
        df_results = pd.read_csv('for_subset_tests.csv')

        # Runs the code being tested.
        df_validation = df_results[(df_results['FITS_Valid'] == False) |
                                   (df_results['FITS_Well-Formed'] == False) |
                                   (df_results['FITS_Status_Message'].notnull())].copy()
        if len(df_validation) == 0:
            df_validation = pd.DataFrame([['No data of this type']])

        # Converts the resulting dataframe to a list, including the column headers.
        result = [df_validation.columns.to_list()] + df_validation.values.tolist()

        # Creates a list with the expected result.
        expected = [['FITS_File_Path', 'FITS_Format_Name', 'FITS_Format_Version', 'FITS_PUID',
                     'FITS_Identifying_Tool(s)', 'FITS_Multiple_IDs', 'FITS_Date_Last_Modified', 'FITS_Size_KB',
                     'FITS_MD5', 'FITS_Creating_Application', 'FITS_Valid', 'FITS_Well-Formed', 'FITS_Status_Message',
                     'NARA_Risk Level', 'NARA_Proposed Preservation Plan', 'NARA_Match_Type', 'Technical_Appraisal',
                     'Other_Risk'],
                    ['C:\\CD1\\file.bak', 'Backup File', np.NaN, np.NaN, 'file utility version 5.03', False,
                     '5/5/2022', 1.23, 'ab1e0b017c8eex694eb379e354571234', np.NaN, False, True, np.NaN, 'High Risk',
                     'Retain', 'Format Name', 'Not for TA', 'Not for Other'],
                    ['C:\\CD1\\file.psd', 'Adobe Photoshop file', np.NaN,
                     'https://www.nationalarchives.gov.uk/pronom/x-fmt/92', 'file utility version 5.03', True,
                     '5/5/2022', 57.01, 'le1b6b058c8rrb684ex370e354572936', np.NaN, True, False, np.NaN, 'Moderate Risk',
                     'Transform to TIFF or JPEG2000', 'PRONOM', 'Not for TA', 'Layered image file'],
                    ['C:\\CD1\\file.psd', 'Adobe Photoshop file', '1',
                     'https://www.nationalarchives.gov.uk/pronom/x-fmt/92', 'Droid version 6.4', True, '5/5/2022',
                     57.01, 'le1b6b058c8rrb684ex370e354572936', np.NaN, True, False, np.NaN, 'Moderate Risk',
                     'Transform to TIFF or JPEG2000', 'PRONOM', 'Not for TA', 'Layered image file'],
                    ['C:\\CD1\\file.psd', 'Adobe Photoshop file', '1', np.NaN, 'Tika version 1.21', True, '5/5/2022',
                     57.01, 'le1b6b058c8rrb684ex370e354572936', np.NaN, True, False, np.NaN, 'Moderate Risk',
                     'Transform to TIFF or JPEG2000', 'File Extension', 'Not for TA', 'Layered image file'],
                    ['C:\\CD1\\Photo.JPG', 'JPEG EXIF', '1.01', np.NaN,
                     'Jhove version 1.20.1; NLNZ Metadata Extractor version 3.6GA', False, '5/5/2022', 47.836,
                     'fe1e6b017c8eeb684eb379e354572936', np.NaN, True, True, 'Unknown TIFF IFD tag', 'Low Risk',
                     'Retain', 'File Extension', 'Not for TA', 'Not for Other'],
                    ['C:\\CD1\\Picture.JPG', 'JPEG EXIF', '1.01', np.NaN,
                     'Jhove version 1.20.1; NLNZ Metadata Extractor version 3.6GA', False, '5/5/2022', 13.563,
                     '686779fae835aadff6474898f5781e99', np.NaN, True, True, 'Unknown TIFF IFD tag', 'Low Risk',
                     'Retain', 'File Extension', 'Not for TA', 'Not for Other'],
                    ['C:\\CD2\\blank.docx', 'empty', np.NaN, np.NaN, 'file utility version 5.03', False, '6/27/2022',
                     0, 'd41d8cd98fb204e98998ecf8427e', np.NaN, np.NaN, np.NaN, 'File is empty', 'Low Risk', 'Retain',
                     'File Extension', 'Format', 'Not for Other'],
                    ['C:\\CD2\\index.html', 'Hypertext Markup Language', '4.01',
                     'https://www.nationalarchives.gov.uk/pronom/fmt/1',
                     'Droid version 6.4; Jhove version 1.20.1; file utility version 5.03', False, '5/5/2022', 2.971,
                     'acff2f63c38dd7a30ca809ef36782d', np.NaN, False, False, 'TokenMgrError', 'Low Risk', 'Retain',
                     'PRONOM', 'Not for TA', 'Not for Other']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with validation subset')

    def test_validation_subset_empty(self):
        """
        Test for the validation subset, when there are no files matching the criteria for this subset.
        This happens when all files have FITS where Valid is True or empty, Well-Formed is true or empty,
        and Status Message is empty.
        Result for testing is the dataframe created by the filter, converted to a list for an easier comparison.
        """
        # Reads test data into a dataframe (located in the tests folder of the script repo).
        df_results = pd.read_csv('for_subset_empty_tests.csv')

        # Runs the code being tested.
        df_validation = df_results[(df_results['FITS_Valid'] == False) |
                                   (df_results['FITS_Well-Formed'] == False) |
                                   (df_results['FITS_Status_Message'].notnull())].copy()
        if len(df_validation) == 0:
            df_validation = pd.DataFrame([['No data of this type']])

        # Converts the resulting dataframe to a list, including the column headers.
        result = [df_validation.columns.to_list()] + df_validation.values.tolist()

        # Creates a list with the expected result.
        expected = [[0], ['No data of this type']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with validation subset when empty')

    def test_tech_appraisal_subset(self):
        """
        Test for the technical appraisal subset, which includes any file that is not 'Not for TA'.
        Result for testing is the dataframe created by the filter, converted to a list for an easier comparison.
        """
        # Reads test data into a dataframe (located in the tests folder of the script repo).
        df_results = pd.read_csv('for_subset_tests.csv')

        # Runs the code being tested.
        df_tech_appraisal = df_results[df_results['Technical_Appraisal'] != 'Not for TA'].copy()
        df_tech_appraisal.drop(['FITS_PUID', 'FITS_Date_Last_Modified', 'FITS_MD5', 'FITS_Valid', 'FITS_Well-Formed',
                                'FITS_Status_Message'], inplace=True, axis=1)
        if len(df_tech_appraisal) == 0:
            df_tech_appraisal = pd.DataFrame([['No data of this type']])

        # Converts the resulting dataframe to a list, including the column headers.
        result = [df_tech_appraisal.columns.to_list()] + df_tech_appraisal.values.tolist()

        # Creates a list with the expected result.
        expected = [['FITS_File_Path', 'FITS_Format_Name', 'FITS_Format_Version', 'FITS_Identifying_Tool(s)',
                     'FITS_Multiple_IDs', 'FITS_Size_KB', 'FITS_Creating_Application', 'NARA_Risk Level',
                     'NARA_Proposed Preservation Plan', 'NARA_Match_Type', 'Technical_Appraisal', 'Other_Risk'],
                    ['C:\\CD2\\blank.docx', 'empty', np.NaN, 'file utility version 5.03', False, 0.0, np.NaN,
                     'Low Risk', 'Retain', 'File Extension', 'Format', 'Not for Other'],
                    ['C:\\CD2\\Trash\\Junk.txt', 'Plain text', np.NaN,
                     'Droid version 6.4; Jhove version 1.20.1; file utility version 5.03', False, 0.4, np.NaN,
                     'Low Risk', 'Retain', 'PRONOM', 'Trash', 'Not for Other']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with tech appraisal subset')

    def test_tech_appraisal_subset_empty(self):
        """
        Test for the technical appraisal subset, when there are no files matching the criteria for this subset.
        This happens when all files are 'Not for TA'.
        Result for testing is the dataframe created by the filter, converted to a list for an easier comparison.
        """
        # Reads test data into a dataframe (located in the tests folder of the script repo).
        df_results = pd.read_csv('for_subset_empty_tests.csv')

        # Runs the code being tested.
        df_tech_appraisal = df_results[df_results['Technical_Appraisal'] != 'Not for TA'].copy()
        df_tech_appraisal.drop(['FITS_PUID', 'FITS_Date_Last_Modified', 'FITS_MD5', 'FITS_Valid', 'FITS_Well-Formed',
                                'FITS_Status_Message'], inplace=True, axis=1)
        if len(df_tech_appraisal) == 0:
            df_tech_appraisal = pd.DataFrame([['No data of this type']])

        # Converts the resulting dataframe to a list, including the column headers.
        result = [df_tech_appraisal.columns.to_list()] + df_tech_appraisal.values.tolist()

        # Creates a list with the expected result.
        expected = [[0], ['No data of this type']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with technical appraisal subset when empty')

    def test_other_risk_subset(self):
        """
        Test for the other risk subset, which includes any file that is not 'Not for Other'.
        Result for testing is the dataframe created by the filter, converted to a list for an easier comparison.
        """
        # Reads test data into a dataframe (located in the tests folder of the script repo).
        df_results = pd.read_csv('for_subset_tests.csv')

        # Runs the code being tested.
        df_other_risk = df_results[df_results['Other_Risk'] != 'Not for Other'].copy()
        df_other_risk.drop(['FITS_PUID', 'FITS_Date_Last_Modified', 'FITS_MD5', 'FITS_Creating_Application',
                            'FITS_Valid', 'FITS_Well-Formed', 'FITS_Status_Message'], inplace=True, axis=1)
        if len(df_other_risk) == 0:
            df_other_risk = pd.DataFrame([['No data of this type']])
        
        # Converts the resulting dataframe to a list, including the column headers.
        result = [df_other_risk.columns.to_list()] + df_other_risk.values.tolist()
        
        # Creates a list with the expected result. 
        expected = [['FITS_File_Path', 'FITS_Format_Name', 'FITS_Format_Version', 'FITS_Identifying_Tool(s)',
                     'FITS_Multiple_IDs', 'FITS_Size_KB', 'NARA_Risk Level', 'NARA_Proposed Preservation Plan',
                     'NARA_Match_Type', 'Technical_Appraisal', 'Other_Risk'],
                    ['C:\\CD1\\file.psd', 'Adobe Photoshop file', np.NaN, 'file utility version 5.03', True, 57.01,
                     'Moderate Risk', 'Transform to TIFF or JPEG2000', 'PRONOM', 'Not for TA', 'Layered image file'],
                    ['C:\\CD1\\file.psd', 'Adobe Photoshop file', '1', 'Droid version 6.4', True, 57.01,
                     'Moderate Risk', 'Transform to TIFF or JPEG2000', 'PRONOM', 'Not for TA', 'Layered image file'],
                    ['C:\\CD1\\file.psd', 'Adobe Photoshop file', '1', 'Tika version 1.21', True, 57.01,
                     'Moderate Risk', 'Transform to TIFF or JPEG2000', 'File Extension', 'Not for TA',
                     'Layered image file'],
                    ['C:\\FD1\\Worksheets.zip', 'ZIP Format', '2', 'Droid version 6.4; file utility version 5.03',
                     False, 11.374, 'Moderate Risk', 'Retain but extract files from the container', 'PRONOM',
                     'Not for TA', 'Archive format'],
                    ['C:\\FD2\\Worksheets.zip', 'ZIP Format', '2', 'Droid version 6.4; file utility version 5.03',
                     False, 11.374, 'Moderate Risk', 'Retain but extract files from the container', 'PRONOM',
                     'Not for TA', 'Archive format']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with other risk subset')

    def test_other_risk_subset_empty(self):
        """
        Test for the other risk subset, when there are no files matching the criteria for this subset.
        This happens when all files are 'Not for Other'.
        Result for testing is the dataframe created by the filter, converted to a list for an easier comparison.
        """
        # Reads test data into a dataframe (located in the tests folder of the script repo).
        df_results = pd.read_csv('for_subset_empty_tests.csv')

        # Runs the code being tested.
        df_other_risk = df_results[df_results['Other_Risk'] != 'Not for Other'].copy()
        df_other_risk.drop(['FITS_PUID', 'FITS_Date_Last_Modified', 'FITS_MD5', 'FITS_Creating_Application',
                            'FITS_Valid', 'FITS_Well-Formed', 'FITS_Status_Message'], inplace=True, axis=1)
        if len(df_other_risk) == 0:
            df_other_risk = pd.DataFrame([['No data of this type']])

        # Converts the resulting dataframe to a list, including the column headers.
        result = [df_other_risk.columns.to_list()] + df_other_risk.values.tolist()
        
        # Creates a list with the expected result. 
        expected = [[0], ['No data of this type']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with other risk subset when empty')

    def test_duplicates_subset(self):
        """
        Test for the duplicates subset, which includes any file which is in the set more than once.
        There will be multiple files with the same MD5 but each will have a different file path.
        It does not include files that were duplicated because they were copied for multiple FITS identifications
        or multiple possible NARA matches.
        Result for testing is the dataframe created by the filter, converted to a list for an easier comparison.
        """
        # Reads test data into a dataframe (located in the tests folder of the script repo).
        df_results = pd.read_csv('for_subset_tests.csv')

        # Runs the code being tested.
        df_duplicates = df_results[['FITS_File_Path', 'FITS_Size_KB', 'FITS_MD5']].copy()
        df_duplicates = df_duplicates.drop_duplicates(subset=['FITS_File_Path'], keep=False)
        df_duplicates = df_duplicates.loc[df_duplicates.duplicated(subset='FITS_MD5', keep=False)]
        if len(df_duplicates) == 0:
            df_duplicates = pd.DataFrame([['No data of this type']])

        # Converts the resulting dataframe to a list, including the column headers.
        result = [df_duplicates.columns.to_list()] + df_duplicates.values.tolist()
        
        # Creates a list with the expected result. 
        expected = [['FITS_File_Path', 'FITS_Size_KB', 'FITS_MD5'],
                    ['C:\\FD1\\Worksheet CSV Version.csv', 0.178, '97e4f6e6f35e5606855d0917e22740b9'],
                    ['C:\\FD1\\Worksheets.zip', 11.374, 'b335c9b47034466907b169e04cbbfa'],
                    ['C:\\FD2\\Worksheet CSV Version.csv', 0.178, '97e4f6e6f35e5606855d0917e22740b9'],
                    ['C:\\FD2\\Worksheets.zip', 11.374, 'b335c9b47034466907b169e04cbbfa']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with duplicates subset')

    def test_duplicates_subset_empty(self):
        """
        Test for the duplicates risk subset, when there are no files matching the criteria for this subset.
        This happens when all files are unique or are only in the dataframe more than once because of
        multiple FITS identifications or multiple possible NARA matches.
        Result for testing is the dataframe created by the filter, converted to a list for an easier comparison.
        """
        # Reads test data into a dataframe (located in the tests folder of the script repo).
        df_results = pd.read_csv('for_subset_empty_tests.csv')

        # Runs the code being tested.
        df_duplicates = df_results[['FITS_File_Path', 'FITS_Size_KB', 'FITS_MD5']].copy()
        df_duplicates = df_duplicates.drop_duplicates(subset=['FITS_File_Path'], keep=False)
        df_duplicates = df_duplicates.loc[df_duplicates.duplicated(subset='FITS_MD5', keep=False)]
        if len(df_duplicates) == 0:
            df_duplicates = pd.DataFrame([['No data of this type']])

        # Converts the resulting dataframe to a list, including the column headers.
        result = [df_duplicates.columns.to_list()] + df_duplicates.values.tolist()
        
        # Creates a list with the expected result. 
        expected = [[0], ['No data of this type']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with duplicates subset when empty')


if __name__ == '__main__':
    unittest.main()
