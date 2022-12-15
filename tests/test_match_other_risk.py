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
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """
        # Creates test input.
        rows = [['empty', np.NaN, np.NaN],
                ['Advanced Systems Format', 'Moderate Risk', 'Retain']]
        df_results = pd.DataFrame(rows, columns=['FITS_Format_Name', 'NARA_Risk Level', 'NARA_Proposed Preservation Plan'])
        df_other = csv_to_dataframe(c.RISK)

        # Runs the function being tested and converts the resulting dataframe to a list.
        df_results = match_other_risk(df_results, df_other)
        result = df_results.values.tolist()

        # Creates a list with the expected result.
        expected = [['empty', np.NaN, np.NaN, 'Not for Other'],
                    ['Advanced Systems Format', 'Moderate Risk', 'Retain', 'Not for Other']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with no risk')

    def test_no_risk_low_only(self):
        """
        Test for files that do not meet any risk criteria.
        NARA risk is low but the plan is not transform, so it isn't a match.
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """
        # Creates test input.
        rows = [['Audio Video Interleave Format (AVI)', 'Low Risk', 'Retain'],
                ['Broadcast Wave (BWF) v. 0', 'Low Risk', 'Retain']]
        df_results = pd.DataFrame(rows,
                                  columns=['FITS_Format_Name', 'NARA_Risk Level', 'NARA_Proposed Preservation Plan'])
        df_other = csv_to_dataframe(c.RISK)

        # Runs the function being tested and converts the resulting dataframe to a list.
        df_results = match_other_risk(df_results, df_other)
        result = df_results.values.tolist()

        # Creates a list with the expected result.
        expected = [['Audio Video Interleave Format (AVI)', 'Low Risk', 'Retain', 'Not for Other'],
                    ['Broadcast Wave (BWF) v. 0', 'Low Risk', 'Retain', 'Not for Other']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with no risk, NARA low risk but not transform')

    def test_no_risk_transform_only(self):
        """
        Test for files that do not meet any risk criteria.
        NARA plan is transform, but it isn't low risk, so it isn't a match.
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """
        # Creates test input.
        rows = [['AutoCAD Drawing (2000-2002)', 'Moderate Risk', 'Transform to a TBD format'],
                ['FoxPro 2.0', 'Moderate Risk', 'Transform to CSV']]
        df_results = pd.DataFrame(rows, columns=['FITS_Format_Name', 'NARA_Risk Level', 'NARA_Proposed Preservation Plan'])
        df_other = csv_to_dataframe(c.RISK)

        # Runs the function being tested and converts the resulting dataframe to a list.
        df_results = match_other_risk(df_results, df_other)
        result = df_results.values.tolist()

        # Creates a list with the expected result.
        expected = [['AutoCAD Drawing (2000-2002)', 'Moderate Risk', 'Transform to a TBD format', 'Not for Other'],
                    ['FoxPro 2.0', 'Moderate Risk', 'Transform to CSV', 'Not for Other']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with no risk, NARA transform but not low risk')

    def test_nara(self):
        """
        Test for files that are NARA low risk with a plan to transform.
        The format is not in the Riskfileformats.csv spreadsheet.
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """
        # Creates test input.
        rows = [['iCalendar', 'Low Risk', 'Transform to CSV'],
                ['MBOX Email Format', 'Low Risk', 'Transform to EML but also retain MBOX']]
        df_results = pd.DataFrame(rows, columns=['FITS_Format_Name', 'NARA_Risk Level', 'NARA_Proposed Preservation Plan'])
        df_other = csv_to_dataframe(c.RISK)

        # Runs the function being tested and converts the resulting dataframe to a list.
        df_results = match_other_risk(df_results, df_other)
        result = df_results.values.tolist()

        # Creates a list with the expected result.
        expected = [['iCalendar', 'Low Risk', 'Transform to CSV', 'NARA Low/Transform'],
                    ['MBOX Email Format', 'Low Risk', 'Transform to EML but also retain MBOX', 'NARA Low/Transform']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with NARA low risk/transform')

    def test_format_case_match(self):
        """
        Test for files that match a format for other risk, where the case and full format name match.
        The format is not NARA low risk with a plan to transform.
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """
        # Creates test input.
        rows = [['Adobe Photoshop file', 'Moderate Risk', 'Transform to TIFF or JPEG2000'],
                ['CorelDraw Drawing', 'High Risk', 'Transform to a TBD format, possibly PDF or TIFF'],
                ['ZIP Format', 'Low Risk', 'Retain']]
        df_results = pd.DataFrame(rows, columns=['FITS_Format_Name', 'NARA_Risk Level', 'NARA_Proposed Preservation Plan'])
        df_other = csv_to_dataframe(c.RISK)

        # Runs the function being tested and converts the resulting dataframe to a list.
        df_results = match_other_risk(df_results, df_other)
        result = df_results.values.tolist()

        # Creates a list with the expected result.
        expected = [['Adobe Photoshop file', 'Moderate Risk', 'Transform to TIFF or JPEG2000', 'Layered image file'],
                    ['CorelDraw Drawing', 'High Risk', 'Transform to a TBD format, possibly PDF or TIFF', 'Layered image file'],
                    ['ZIP Format', 'Low Risk', 'Retain', 'Archive format']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with format, case matches')

    # def test_format_case_match_partial(self):
    #     """
    #     Test for files that match a format for other risk,
    #     where the case matches and only partially matching the format string.
    #     The format is not NARA low risk with a plan to transform.
    #     Result for testing is the df returned by the function, converted to a list for an easier comparison.
    #     """
    #     # Creates test input.
    #     rows = [['Adobe Photoshop files', 'Moderate Risk', 'Transform to TIFF or JPEG2000'],
    #             ['A CorelDraw Drawing v1', 'High Risk', 'Transform to a TBD format, possibly PDF or TIFF'],
    #             ['XYZIP Format', 'Low Risk', 'Retain']]
    #     df_results = pd.DataFrame(rows,
    #                               columns=['FITS_Format_Name', 'NARA_Risk Level', 'NARA_Proposed Preservation Plan'])
    #     df_other = csv_to_dataframe(c.RISK)
    #
    #     # Runs the function being tested and converts the resulting dataframe to a list.
    #     df_results = match_other_risk(df_results, df_other)
    #     result = df_results.values.tolist()
    #
    #     # Creates a list with the expected result.
    #     expected = [['Adobe Photoshop files', 'Moderate Risk', 'Transform to TIFF or JPEG2000', 'Layered image file'],
    #                 ['A CorelDraw Drawing v1', 'High Risk', 'Transform to a TBD format, possibly PDF or TIFF',
    #                  'Layered image file'],
    #                 ['XYZIP Format', 'Low Risk', 'Retain', 'Archive format']]
    #
    #     # Compares the results. assertEqual prints "OK" or the differences between the two lists.
    #     self.assertEqual(result, expected, 'Problem with format, case matches, partial string')

    def test_format_case_no_match(self):
        """
        Test for files that match a format for other risk,
        where case does not matching case and the entire format name is matched.
        The format is not NARA low risk with a plan to transform.
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """
        # Creates test input.
        rows = [['adobe photoshop file', 'Moderate Risk', 'Transform to TIFF or JPEG2000'],
                ['CorelDRAW Drawing', 'High Risk', 'Transform to a TBD format, possibly PDF or TIFF'],
                ['Zip Format', 'Low Risk', 'Retain']]
        df_results = pd.DataFrame(rows,
                                  columns=['FITS_Format_Name', 'NARA_Risk Level', 'NARA_Proposed Preservation Plan'])
        df_other = csv_to_dataframe(c.RISK)

        # Runs the function being tested and converts the resulting dataframe to a list.
        df_results = match_other_risk(df_results, df_other)
        result = df_results.values.tolist()

        # Creates a list with the expected result.
        expected = [['adobe photoshop file', 'Moderate Risk', 'Transform to TIFF or JPEG2000', 'Layered image file'],
                    ['CorelDRAW Drawing', 'High Risk', 'Transform to a TBD format, possibly PDF or TIFF',
                     'Layered image file'],
                    ['Zip Format', 'Low Risk', 'Retain', 'Archive format']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with format, case does not match')

    # def test_format_case_no_match_partial(self):
    #     """
    #     Test for files that match a format for other risk,
    #     where case does not match and only partially matching the format string.
    #     The format is not NARA low risk with a plan to transform.
    #     Result for testing is the df returned by the function, converted to a list for an easier comparison.
    #     """
    #     # Creates test input
    #     rows = [['adobe photoshop files', 'Moderate Risk', 'Transform to TIFF or JPEG2000'],
    #             ['ACORELDRAW DRAWING V1', 'High Risk', 'Transform to a TBD format, possibly PDF or TIFF'],
    #             ['XYzip format', 'Low Risk', 'Retain']]
    #     df_results = pd.DataFrame(rows,
    #                               columns=['FITS_Format_Name', 'NARA_Risk Level', 'NARA_Proposed Preservation Plan'])
    #     df_other = csv_to_dataframe(c.RISK)
    #
    #     # Runs the function being tested and converts the resulting dataframe to a list.
    #     df_results = match_other_risk(df_results, df_other)
    #     result = df_results.values.tolist()
    #
    #     # Creates a list with the expected result.
    #     expected = [['adobe photoshop files', 'Moderate Risk', 'Transform to TIFF or JPEG2000', 'Layered image file'],
    #                 ['ACORELDRAW DRAWING V1', 'High Risk', 'Transform to a TBD format, possibly PDF or TIFF',
    #                  'Layered image file'],
    #                 ['WYzip format', 'Low Risk', 'Retain', 'Archive format']]
    #
    #     # Compares the results. assertEqual prints "OK" or the differences between the two lists.
    #     self.assertEqual(result, expected, 'Problem with format, case does not match, partial string')

    def test_nara_and_format(self):
        """
        Test for files that are NARA Low Risk/Transform and the format is in the Riskfileformats.csv spreadsheet.
        When a file matches both categories, the format risk is applied.
        Result for testing is the df returned by the function, converted to a list for an easier comparison.
        """
        # Creates test input.
        rows = [['Cascading Style Sheet', 'Low Risk', 'Retain'],
                ['ZIP Format', 'Low Risk', 'Retain']]
        df_results = pd.DataFrame(rows,
                                  columns=['FITS_Format_Name', 'NARA_Risk Level', 'NARA_Proposed Preservation Plan'])
        df_other = csv_to_dataframe(c.RISK)

        # Runs the function being tested and converts the resulting dataframe to a list.
        df_results = match_other_risk(df_results, df_other)
        result = df_results.values.tolist()

        # Creates a list with the expected result.
        expected = [['Cascading Style Sheet', 'Low Risk', 'Retain', 'Possible saved web page'],
                    ['ZIP Format', 'Low Risk', 'Retain', 'Archive format']]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(result, expected, 'Problem with NARA and format')


if __name__ == '__main__':
    unittest.main()
