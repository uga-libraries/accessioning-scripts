"""Tests the function subtotal, including all four types of subtotals which are generated."""

import pandas as pd
import unittest
from format_analysis_functions import subtotal


class MyTestCase(unittest.TestCase):

    def setUp(self):
        """
        Makes a results dataframe and totals for testing subtotals that are not empty.
        To simplify testing, it only includes columns used for at least one subtotal.
        """
        rows = [['Adobe Photoshop', 100.1, 'Moderate Risk', 'Not for TA', 'Layered image file'],
                ['Adobe Photoshop', 101.22, 'Moderate Risk', 'Not for TA', 'Layered image file'],
                ['Cascading Style Sheet', 102.33, 'Low Risk', 'Not for TA', 'Possible saved web page'],
                ['DOS/Windows Executable', 103, 'High Risk', 'Format', 'Not for Other'],
                ['Encapsulated Postscript File', 104.1, 'Low Risk', 'Not for TA', 'NARA Low/Transform'],
                ['JPEG EXIF', 205.22, 'Low Risk', 'Trash', 'Not for Other'],
                ['JPEG EXIF', 206.333, 'Low Risk', 'Not for TA', 'Not for Other'],
                ['Open Office XML Workbook', 207, 'Low Risk', 'Not for TA', 'Not for Other'],
                ['QuickTime', 208.0, 'Low Risk', 'Not for TA', 'NARA Low/Transform'],
                ['Unknown Binary', 309.1, 'No Match', 'Format', 'Not for Other'],
                ['Unknown Binary', 0.22, 'No Match', 'Format', 'Not for Other'],
                ['Unknown Binary', 301.333, 'No Match', 'Format', 'Not for Other'],
                ['XLSX', 302.0, 'Low Risk', 'Not for TA', 'Not for Other'],
                ['Zip Format', 303, 'Moderate Risk', 'Not for TA', 'Archive format']]
        columns = ['FITS_Format_Name', 'FITS_Size_KB', 'NARA_Risk Level', 'Technical_Appraisal', 'Other_Risk']
        self.df_results = pd.DataFrame(rows, columns=columns)

        self.totals_dict = {'Files': len(self.df_results.index), 'MB': self.df_results['FITS_Size_KB'].sum() / 1000}

    def test_format_subtotal(self):
        """
        Test for the format subtotal, which is based on FITS_Format_Name and NARA_Risk Level.
        Variations include formats with one row, formats with multiple rows, one format with a NARA risk level,
        and multiple formats with the same NARA risk level.
        """

        # Runs the function being tested and converts the resulting dataframe into a list for easier comparison.
        # Uses reset_index() to include the index values in the dataframe, which are the two subtotal criteria.
        df_subtotal = subtotal(self.df_results, ['FITS_Format_Name', 'NARA_Risk Level'], self.totals_dict)
        results = df_subtotal.reset_index().values.tolist()

        # Makes a list with the expected values.
        expected = [['Adobe Photoshop', 'Moderate Risk', 2, 14.286, 0.201, 7.873],
                    ['Cascading Style Sheet', 'Low Risk', 1, 7.143, 0.102, 3.995],
                    ['DOS/Windows Executable', 'High Risk', 1, 7.143, 0.103, 4.035],
                    ['Encapsulated Postscript File', 'Low Risk', 1, 7.143, 0.104, 4.074],
                    ['JPEG EXIF', 'Low Risk', 2, 14.286, 0.412, 16.138],
                    ['Open Office XML Workbook', 'Low Risk', 1, 7.143, 0.207, 8.108],
                    ['QuickTime', 'Low Risk', 1, 7.143, 0.208, 8.147],
                    ['Unknown Binary', 'No Match', 3, 21.429, 0.611, 23.933],
                    ['XLSX', 'Low Risk', 1, 7.143, 0.302, 11.829],
                    ['Zip Format', 'Moderate Risk', 1, 7.143, 0.303, 11.869]]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(results, expected, 'Problem with format subtotal')

    def test_nara_risk_subtotal(self):
        """
        Test for the NARA risk subtotal, which is based on NARA_Risk Level.
        Variations include all 4 NARA risk levels, one format with the risk level,
        and multiple formats with the same risk level."""

        # Runs the function being tested and converts the resulting dataframe into a list for easier comparison.
        # Uses reset_index() to include the index values in the dataframe, which are the two subtotal criteria.
        df_subtotal = subtotal(self.df_results, ['NARA_Risk Level'], self.totals_dict)
        results = df_subtotal.reset_index().values.tolist()

        # Makes a list with the expected values.
        expected = [['High Risk', 1, 7.143, 0.103, 4.035],
                    ['Low Risk', 7, 50, 1.335, 52.292],
                    ['Moderate Risk', 3, 21.429, 0.504, 19.742],
                    ['No Match', 3, 21.429, 0.611, 23.933]]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(results, expected, 'Problem with NARA risk subtotal')

    def test_tech_appraisal_subtotal(self):
        """
        Test for the technical appraisal subtotal, which is based on technical appraisal criteria and FITS_Format_Name.
        Variations include both technical appraisal categories, one format with a category,
        and multiple formats with the same category.
        """

        # Runs the function being tested and converts the resulting dataframe into a list for easier comparison.
        # The dataframe is filtered for just formats which meet one of the criteria for technical appraisal.
        # Uses reset_index() to include the index values in the dataframe, which are the two subtotal criteria.
        df_subtotal = subtotal(self.df_results[self.df_results["Technical_Appraisal"] != "Not for TA"],
                               ['Technical_Appraisal', 'FITS_Format_Name'], self.totals_dict)
        results = df_subtotal.reset_index().values.tolist()

        # Makes a list with the expected values.
        expected = [['Format', 'DOS/Windows Executable', 1, 7.143, 0.103, 4.035],
                    ['Format', 'Unknown Binary', 3, 21.429, 0.611, 23.933],
                    ['Trash', 'JPEG EXIF', 1, 7.143, 0.205, 8.03]]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(results, expected, 'Problem with technical appraisal subtotal')

    def test_tech_appraisal_subtotal_none(self):
        """
        Test for the technical appraisal subtotal when no formats meet any technical appraisal criteria.
        """

        # Makes a dataframe and dictionary with file and size counts to use as input for the subtotal() function.
        rows = [['Adobe Photoshop', 101.22, 'Moderate Risk', 'Not for TA', 'Layered image file'],
                ['Cascading Style Sheet', 102.33, 'Low Risk', 'Not for TA', 'Possible saved web page'],
                ['JPEG EXIF', 206.333, 'Low Risk', 'Not for TA', 'Not for Other']]
        columns = ['FITS_Format_Name', 'FITS_Size_KB', 'NARA_Risk Level', 'Technical_Appraisal', 'Other_Risk']
        df_results = pd.DataFrame(rows, columns=columns)
        totals_dict = {'Files': len(df_results.index), 'MB': df_results['FITS_Size_KB'].sum() / 1000}

        # Runs the function being tested and converts the resulting dataframe into a list for easier comparison.
        # The dataframe is filtered for just formats which meet one of the criteria for technical appraisal.
        df_subtotal = subtotal(df_results[df_results["Technical_Appraisal"] != "Not for TA"],
                                              ['Technical_Appraisal', 'FITS_Format_Name'], totals_dict)
        results = df_subtotal.values.tolist()

        # Makes a list with the expected values.
        expected = 'No data of this type'

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        # Just the first item in the list (the message) is used for the comparison. The rest are blanks.
        self.assertEqual(results[0][0], expected, 'Problem with technical appraisal subtotal, no files match criteria')

    def test_other_risk_subtotal(self):
        """
        Test for the other risk subtotal, which is based on other risk criteria and FITS_Format_Name.
        Variations include all 4 technical appraisal categories, one format with a category,
        and multiple formats with the same category.
        """

        # Runs the function being tested and converts the resulting dataframe into a list for easier comparison.
        # The dataframe is filtered for just formats which meet one of the criteria for other risk.
        # Uses reset_index() to include the index values in the dataframe, which are the two subtotal criteria.
        df_subtotal = subtotal(self.df_results[self.df_results["Other_Risk"] != "Not for Other"],
                               ['Other_Risk', 'FITS_Format_Name'], self.totals_dict)
        results = df_subtotal.reset_index().values.tolist()

        # Makes a list with the expected values.
        expected = [['Archive format', 'Zip Format', 1, 7.143, 0.303, 11.869],
                    ['Layered image file', 'Adobe Photoshop', 2, 14.286, 0.201, 7.873],
                    ['NARA Low/Transform', 'Encapsulated Postscript File', 1, 7.143, 0.104, 4.074],
                    ['NARA Low/Transform', 'QuickTime', 1, 7.143, 0.208, 8.147],
                    ['Possible saved web page', 'Cascading Style Sheet', 1, 7.143, 0.102, 3.995]]

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        self.assertEqual(results, expected, 'Problem with other risk subtotal')

    def test_other_risk_subtotal_none(self):
        """
        Test for the other risk subtotal when no formats meet any other risk criteria.
        """

        # Makes a dataframe and dictionary with file and size counts to use as input for the subtotal() function.
        rows = [['Unknown Binary', 301.333, 'No Match', 'Format', 'Not for Other'],
                ['XLSX', 302.0, 'Low Risk', 'Not for TA', 'Not for Other'],]
        columns = ['FITS_Format_Name', 'FITS_Size_KB', 'NARA_Risk Level', 'Technical_Appraisal', 'Other_Risk']
        df_results = pd.DataFrame(rows, columns=columns)
        totals_dict = {'Files': len(df_results.index), 'MB': df_results['FITS_Size_KB'].sum() / 1000}

        # Runs the function being tested and converts the resulting dataframe into a list for easier comparison.
        # The dataframe is filtered for just formats which meet one of the criteria for technical appraisal.
        df_subtotal = subtotal(df_results[df_results["Other_Risk"] != "Not for Other"],
                               ['Other_Risk', 'FITS_Format_Name'], totals_dict)
        results = df_subtotal.values.tolist()

        # Makes a list with the expected values.
        expected = 'No data of this type'

        # Compares the results. assertEqual prints "OK" or the differences between the two lists.
        # Just the first item in the list (the message) is used for the comparison. The rest is blanks.
        self.assertEqual(results[0][0], expected, 'Problem with other risk subtotal, no files match criteria')


if __name__ == '__main__':
    unittest.main()
