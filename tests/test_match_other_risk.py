"""Tests the function match_other_risk, which adds the other risk type to df_results
based on the NARA risk level and Riskfileformats.csv.

To simplify the testing, df_results only has the format name, NARA risk level, and NARA plan
the only columns used by match_other_risk."""

import numpy as np
import pandas as pd
import unittest
import configuration as c
from format_analysis_functions import csv_to_dataframe, match_other_risk


class MyTestCase(unittest.TestCase):

    def test_no_risk(self):
        """
        Test for files that do not meet any risk criteria.
        The format isn't in Riskfileformats.csv and the NARA data is not both a risk level of Low and
        a preservation plan other than Retain.
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """
        # Creates test input.
        rows = [['empty', np.NaN, np.NaN],
                ['Advanced Systems Format', 'Moderate Risk', 'Retain']]
        df_results = pd.DataFrame(rows, columns=['FITS_Format_Name', 'NARA_Risk Level', 'NARA_Proposed Preservation Plan'])
        df_other = csv_to_dataframe(c.RISK)

        # Runs the function being tested and converts the resulting dataframe to a list, including the column headers.
        df_results = match_other_risk(df_results, df_other)
        result = [df_results.columns.to_list()] + df_results.values.tolist()

        # Creates a list with the expected result.
        expected = [['FITS_Format_Name', 'NARA_Risk Level', 'NARA_Proposed Preservation Plan', 'Other_Risk'],
                    ['empty', np.NaN, np.NaN, 'Not for Other'],
                    ['Advanced Systems Format', 'Moderate Risk', 'Retain', 'Not for Other']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with no risk')

    def test_no_risk_format_partial(self):
        """
        Test for files that do not meet any risk criteria.
        The format partially matches the Riskfileformats.csv spreadsheet, but an exact match is required.
        It also doesn't have the combination of NARA low risk and a preservation plan other than Retain.
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """
        # Creates test input.
        rows = [['Adobe Photoshop files', 'Moderate Risk', 'Transform to TIFF or JPEG2000'],
                ['A CorelDraw Drawing v1', 'High Risk', 'Transform to a TBD format, possibly PDF or TIFF'],
                ['Style Sheet', 'Low Risk', 'Retain'],
                ['XYZIP Format', 'Low Risk', 'Retain']]
        df_results = pd.DataFrame(rows,
                                  columns=['FITS_Format_Name', 'NARA_Risk Level', 'NARA_Proposed Preservation Plan'])
        df_other = csv_to_dataframe(c.RISK)

        # Runs the function being tested and converts the resulting dataframe to a list, including the column headers.
        df_results = match_other_risk(df_results, df_other)
        result = [df_results.columns.to_list()] + df_results.values.tolist()

        # Creates a list with the expected result.
        expected = [['FITS_Format_Name', 'NARA_Risk Level', 'NARA_Proposed Preservation Plan', 'Other_Risk'],
                    ['Adobe Photoshop files', 'Moderate Risk', 'Transform to TIFF or JPEG2000', 'Not for Other'],
                    ['A CorelDraw Drawing v1', 'High Risk', 'Transform to a TBD format, possibly PDF or TIFF', 'Not for Other'],
                    ['Style Sheet', 'Low Risk', 'Retain', 'Not for Other'],
                    ['XYZIP Format', 'Low Risk', 'Retain', 'Not for Other']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with no risk, format is only a partial match')

    def test_no_risk_format_case(self):
        """
        Test for files that do not meet any risk criteria.
        The format is in Riskfileformats.csv, but the case is different and an exact match is required.
        It also doesn't have the combination of NARA low risk and a preservation plan other than Retain.
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """
        # Creates test input.
        rows = [['adobe photoshop file', 'Moderate Risk', 'Transform to TIFF or JPEG2000'],
                ['CorelDRAW Drawing', 'High Risk', 'Transform to a TBD format, possibly PDF or TIFF'],
                ['Zip Format', 'Low Risk', 'Retain']]
        df_results = pd.DataFrame(rows, columns=['FITS_Format_Name', 'NARA_Risk Level', 'NARA_Proposed Preservation Plan'])
        df_other = csv_to_dataframe(c.RISK)

        # Runs the function being tested and converts the resulting dataframe to a list, including the column headers.
        df_results = match_other_risk(df_results, df_other)
        result = [df_results.columns.to_list()] + df_results.values.tolist()

        # Creates a list with the expected result.
        expected = [['FITS_Format_Name', 'NARA_Risk Level', 'NARA_Proposed Preservation Plan', 'Other_Risk'],
                    ['adobe photoshop file', 'Moderate Risk', 'Transform to TIFF or JPEG2000', 'Not for Other'],
                    ['CorelDRAW Drawing', 'High Risk', 'Transform to a TBD format, possibly PDF or TIFF', 'Not for Other'],
                    ['Zip Format', 'Low Risk', 'Retain', 'Not for Other']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with no risk, format is a different case')

    def test_no_risk_low_only(self):
        """
        Test for files that do not meet any risk criteria.
        The format isn't in Riskfileformats.csv and NARA risk is low but the plan is Retain, so it isn't a match.
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """
        # Creates test input.
        rows = [['Audio Video Interleave Format (AVI)', 'Low Risk', 'Retain'],
                ['Broadcast Wave (BWF) v. 0', 'Low Risk', 'Retain']]
        df_results = pd.DataFrame(rows, columns=['FITS_Format_Name', 'NARA_Risk Level', 'NARA_Proposed Preservation Plan'])
        df_other = csv_to_dataframe(c.RISK)

        # Runs the function being tested and converts the resulting dataframe to a list, including the column headers.
        df_results = match_other_risk(df_results, df_other)
        result = [df_results.columns.to_list()] + df_results.values.tolist()

        # Creates a list with the expected result.
        expected = [['FITS_Format_Name', 'NARA_Risk Level', 'NARA_Proposed Preservation Plan', 'Other_Risk'],
                    ['Audio Video Interleave Format (AVI)', 'Low Risk', 'Retain', 'Not for Other'],
                    ['Broadcast Wave (BWF) v. 0', 'Low Risk', 'Retain', 'Not for Other']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with no risk, NARA is low risk but not transform')

    def test_no_risk_transform_only(self):
        """
        Test for files that do not meet any risk criteria.
        The format isn't in Riskfileformats.csv and NARA plan is not Retain, but it isn't low risk, so it isn't a match.
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """
        # Creates test input.
        rows = [['Apple Video file', 'Moderate Risk', 'Depends on version, transform to MP4 if not DRM protected, otherwise retain'],
                ['AutoCAD Drawing (2000-2002)', 'Moderate Risk', 'Transform to a TBD format'],
                ['Compressed Archive File', 'Moderate Risk', 'Retain but extract files from the container'],
                ['FoxPro 2.0', 'Moderate Risk', 'Transform to CSV'],
                ['Icon file format', 'High Risk', 'Further research is required']]
        df_results = pd.DataFrame(rows, columns=['FITS_Format_Name', 'NARA_Risk Level', 'NARA_Proposed Preservation Plan'])
        df_other = csv_to_dataframe(c.RISK)

        # Runs the function being tested and converts the resulting dataframe to a list, including the column headers.
        df_results = match_other_risk(df_results, df_other)
        result = [df_results.columns.to_list()] + df_results.values.tolist()

        # Creates a list with the expected result.
        expected = [['FITS_Format_Name', 'NARA_Risk Level', 'NARA_Proposed Preservation Plan', 'Other_Risk'],
                    ['Apple Video file', 'Moderate Risk', 'Depends on version, transform to MP4 if not DRM protected, otherwise retain', 'Not for Other'],
                    ['AutoCAD Drawing (2000-2002)', 'Moderate Risk', 'Transform to a TBD format', 'Not for Other'],
                    ['Compressed Archive File', 'Moderate Risk', 'Retain but extract files from the container', 'Not for Other'],
                    ['FoxPro 2.0', 'Moderate Risk', 'Transform to CSV', 'Not for Other'],
                    ['Icon file format', 'High Risk', 'Further research is required', 'Not for Other']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with no risk, NARA transform but not low risk')

    def test_format(self):
        """
        Test for files that match a format for other risk.
        The format is not NARA low risk and a preservation plan other than Retain.
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """
        # Creates test input.
        rows = [['Adobe Photoshop file', 'Moderate Risk', 'Transform to TIFF or JPEG2000'],
                ['CorelDraw Drawing', 'High Risk', 'Transform to a TBD format, possibly PDF or TIFF'],
                ['ZIP Format', 'Low Risk', 'Retain']]
        df_results = pd.DataFrame(rows,
                                  columns=['FITS_Format_Name', 'NARA_Risk Level', 'NARA_Proposed Preservation Plan'])
        df_other = csv_to_dataframe(c.RISK)

        # Runs the function being tested and converts the resulting dataframe to a list, including the column headers.
        df_results = match_other_risk(df_results, df_other)
        result = [df_results.columns.to_list()] + df_results.values.tolist()

        # Creates a list with the expected result.
        expected = [['FITS_Format_Name', 'NARA_Risk Level', 'NARA_Proposed Preservation Plan', 'Other_Risk'],
                    ['Adobe Photoshop file', 'Moderate Risk', 'Transform to TIFF or JPEG2000', 'Layered image file'],
                    ['CorelDraw Drawing', 'High Risk', 'Transform to a TBD format, possibly PDF or TIFF', 'Layered image file'],
                    ['ZIP Format', 'Low Risk', 'Retain', 'Archive format']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with format')

    def test_nara_low_transform(self):
        """
        Test for files that are NARA low risk with a plan other than Retain.
        The format is not in the Riskfileformats.csv spreadsheet.
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """
        # Creates test input.
        rows = [['iCalendar', 'Low Risk', 'Transform to CSV'],
                ['MBOX Email Format', 'Low Risk', 'Transform to EML but also retain MBOX'],
                ['MySQL Form Definition', 'Low Risk', 'Retain with the transformed database content.'],
                ['Open XML Paper Specification', 'Low Risk', 'Further research is required, possibly transform to PDF, or retain as OXPS'],
                ['Tagged Image File Format (TIFF) unspecified version', 'Low Risk', 'Depends on version, retain TIFF 1-6, otherwise see specific version plan']]
        df_results = pd.DataFrame(rows, columns=['FITS_Format_Name', 'NARA_Risk Level', 'NARA_Proposed Preservation Plan'])
        df_other = csv_to_dataframe(c.RISK)

        # Runs the function being tested and converts the resulting dataframe to a list, including the column headers.
        df_results = match_other_risk(df_results, df_other)
        result = [df_results.columns.to_list()] + df_results.values.tolist()

        # Creates a list with the expected result.
        expected = [['FITS_Format_Name', 'NARA_Risk Level', 'NARA_Proposed Preservation Plan', 'Other_Risk'],
                    ['iCalendar', 'Low Risk', 'Transform to CSV', 'NARA Low/Transform'],
                    ['MBOX Email Format', 'Low Risk', 'Transform to EML but also retain MBOX', 'NARA Low/Transform'],
                    ['MySQL Form Definition', 'Low Risk', 'Retain with the transformed database content.', 'NARA Low/Transform'],
                    ['Open XML Paper Specification', 'Low Risk', 'Further research is required, possibly transform to PDF, or retain as OXPS', 'NARA Low/Transform'],
                    ['Tagged Image File Format (TIFF) unspecified version', 'Low Risk', 'Depends on version, retain TIFF 1-6, otherwise see specific version plan', 'NARA Low/Transform']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with NARA low risk/transform')

    def test_format_and_nara_match(self):
        """
        Test for files that are NARA Low Risk/Transform and the format is in the Riskfileformats.csv spreadsheet.
        When a file matches both categories, the format risk is applied.
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """
        # Creates test input.
        rows = [['Encapsulated Postscript File', 'Low Risk', 'Transform to TIFF or JPEG2000'],
                ['Encapsulated Postscript File', 'Low Risk', 'Transform to TIFF or JPEG2000'],
                ['GZIP', 'Low Risk', 'Retain but extract files from the container']]
        df_results = pd.DataFrame(rows, columns=['FITS_Format_Name', 'NARA_Risk Level', 'NARA_Proposed Preservation Plan'])
        df_other = csv_to_dataframe(c.RISK)

        # Runs the function being tested and converts the resulting dataframe to a list, including the column headers.
        df_results = match_other_risk(df_results, df_other)
        result = [df_results.columns.to_list()] + df_results.values.tolist()

        # Creates a list with the expected result.
        expected = [['FITS_Format_Name', 'NARA_Risk Level', 'NARA_Proposed Preservation Plan', 'Other_Risk'],
                    ['Encapsulated Postscript File', 'Low Risk', 'Transform to TIFF or JPEG2000', 'Layered image file'],
                    ['Encapsulated Postscript File', 'Low Risk', 'Transform to TIFF or JPEG2000', 'Layered image file'],
                    ['GZIP', 'Low Risk', 'Retain but extract files from the container', 'Archive format']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with format and NARA low risk/transform')


if __name__ == '__main__':
    unittest.main()
