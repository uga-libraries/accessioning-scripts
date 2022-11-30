import numpy as np
import pandas as pd
import unittest
from format_analysis_functions import subtotal

# TODO: not tested
class MyTestCase(unittest.TestCase):
    def test_format_subtotal(self):
        """Tests the format subtotal, which is based on FITS_Format_Name and NARA_Risk Level."""

        # Makes a dataframe to use as input for the subtotal() function.
        # Data variation: formats with one row, formats with multiple rows, one format with a NARA risk level,
        #                 multiple formats with a NARA risk level, blank in NARA risk level.
        rows = [['JPEG EXIF', 13.563, 'Low Risk'],
                ['JPEG EXIF', 14.1, 'Low Risk'],
                ['Open Office XML Workbook', 19.316, 'Low Risk'],
                ['Unknown Binary', 0, np.NaN],
                ['Unknown Binary', 1, np.NaN],
                ['Unknown Binary', 5, np.NaN],
                ['XLSX', 19.316, 'Low Risk'],
                ['Zip Format', 2.792, 'Moderate Risk']]
        column_names = ['FITS_Format_Name', 'FITS_Size_KB', 'NARA_Risk Level']
        df_results = pd.DataFrame(rows, columns=column_names)

        # Calculates the total files and total size in the dataframe to use for percentages with the subtotal.
        # In format_analysis.py, this is done in the main body of the script before subtotal() is called.
        totals_dict = {'Files': len(df_results.index), 'MB': df_results['FITS_Size_KB'].sum() / 1000}

        # Runs the function being tested.
        df_format_subtotal = subtotal(df_results, ['FITS_Format_Name', 'NARA_Risk Level'], totals_dict)

        # Makes a dataframe with the expected values.
        # The index values for the dataframe made by subtotal() are column values here
        # so that they are visible in the comparison dataframe to label errors.
        rows = [['JPEG EXIF', 'Low Risk', 2, 25, 0.028, 37.29],
                ['Unknown Binary', np.NaN, 3, 37.5, 0.006, 7.991],
                ['Zip Format', 'Moderate Risk', 1, 12.5, 0.003, 3.995],
                ['Open Office XML Workbook', 'Low Risk', 1, 12.5, 0.019, 25.304],
                ['XLSX', 'Low Risk', 1, 12.5, 0.019, 25.304]]
        column_names = ['FITS_Format_Name', 'NARA_Risk Level', 'File Count', 'File %', 'Size (MB)', 'Size %']
        df_expected = pd.DataFrame(rows, columns=column_names)

        # Compares the script output to the expected values.
        self.assertEqual(df_format_subtotal, df_expected, 'Problem with format subtotal')

    def test_nara_risk_subtotal(self):
        """Tests the NARA risk subtotal, which is based on NARA_Risk Level."""

        # Makes a dataframe to use as input for the subtotal() function.
        # Data variation: one format with a NARA risk level, multiple formats with a NARA risk level, all 4 risk levels.
        rows = [['DOS/Windows Executable', 1.23, 'High Risk'],
                ['DOS/Windows Executable', 2.34, 'High Risk'],
                ['DOS/Windows Executable', 3.45, 'High Risk'],
                ['JPEG EXIF', 13.563, 'Low Risk'],
                ['JPEG EXIF', 14.1, 'Low Risk'],
                ['Open Office XML Workbook', 19.316, 'Low Risk'],
                ['Unknown Binary', 0, 'No Match'],
                ['Unknown Binary', 5, 'No Match'],
                ['XLSX', 19.316, 'Low Risk'],
                ['Zip Format', 2.792, 'Moderate Risk']]
        column_names = ['FITS_Format_Name', 'FITS_Size_KB', 'NARA_Risk Level']
        df_results = pd.DataFrame(rows, columns=column_names)

        # Calculates the total files and total size in the dataframe to use for percentages with the subtotal.
        # In format_analysis.py, this is done in the main body of the script before subtotal() is called.
        totals_dict = {'Files': len(df_results.index), 'MB': df_results['FITS_Size_KB'].sum() / 1000}

        # Runs the function being tested.
        df_nara_risk_subtotal = subtotal(df_results, ['NARA_Risk Level'], totals_dict)

        # Makes a dataframe with the expected values.
        # The index value for the dataframe made by subtotal() is a column value here
        # so that it is visible in the comparison dataframe to label errors.
        rows = [['Low Risk', 4, 40, 0.066, 81.374],
                ['Moderate Risk', 1, 10, 0.003, 3.699],
                ['High Risk', 3, 30, 0.007, 8.631],
                ['No Match', 2, 20, 0.005, 6.165]]
        column_names = ['NARA_Risk Level', 'File Count', 'File %', 'Size (MB)', 'Size %']
        df_expected = pd.DataFrame(rows, columns=column_names)

        # Compares the script output to the expected values.
        self.assertEqual(df_nara_risk_subtotal, df_expected, 'Problem with NARA risk subtotal')

    def test_tech_appraisal_subtotal(self):
        """Tests the technical appraisal subtotal, which is based on technical appraisal criteria and FITS_Format_Name."""

        # Makes a dataframe to use as input for the subtotal() function.
        # Data variation: for both criteria, has a unique format and duplicated formats.
        rows = [['Format', 'DOS/Windows Executable', 100.23],
                ['Format', 'DOS/Windows Executable', 200.34],
                ['Format', 'PE32 executable', 300.45],
                ['Format', 'Unknown Binary', 0],
                ['Format', 'Unknown Binary', 50],
                ['Trash', 'JPEG EXIF', 130.563],
                ['Trash', 'JPEG EXIF', 140.1],
                ['Trash', 'Open Office XML Workbook', 190.316]]
        column_names = ['Technical_Appraisal', 'FITS_Format_Name', 'FITS_Size_KB']
        df_results = pd.DataFrame(rows, columns=column_names)

        # Calculates the total files and total size in the dataframe to use for percentages with the subtotal.
        # In format_analysis.py, this is done in the main body of the script before subtotal() is called.
        totals_dict = {'Files': len(df_results.index), 'MB': df_results['FITS_Size_KB'].sum() / 1000}

        # Runs the function being tested.
        df_tech_appraisal_subtotal = subtotal(df_results, ['Technical_Appraisal', 'FITS_Format_Name'], totals_dict)

        # Makes a dataframe with the expected values.
        # The index values for the dataframes made by subtotal() are column values here
        # so that they are visible in the comparison dataframe to label errors.
        rows = [['Format', 'DOS/Windows Executable', 2, 25, 0.301, 27.068],
                ['Format', 'PE32 executable', 1, 12.5, 0.300, 26.978],
                ['Format', 'Unknown Binary', 2, 25, 0.05, 4.496],
                ['Trash', 'JPEG EXIF', 2, 25, 0.271, 24.371],
                ['Trash', 'Open Office XML Workbook', 1, 12.5, 0.19, 17.086]]
        column_names = ['Technical_Appraisal', 'FITS_Format_Name', 'File Count', 'File %', 'Size (MB)', 'Size %']
        df_expected = pd.DataFrame(rows, columns=column_names)

        # Compares the script output to the expected values.
        self.assertEqual(df_tech_appraisal_subtotal, df_expected, 'Problem with technical appraisal subtotal')

    def test_tech_appraisal_subtotal_none(self):
        """Tests the technical appraisal subtotal when there are no files in the input
        which meet any technical appraisal criteria."""

        # Makes an empty dataframe to use as input for the subtotal() function.
        df_results = pd.DataFrame(columns=['Technical_Appraisal', 'FITS_Format_Name', 'FITS_Size_KB'])

        # Calculates the total files and total size in the dataframe to use for percentages with the subtotal.
        # In format_analysis.py, this is done in the main body of the script before subtotal() is called.
        totals_dict = {'Files': len(df_results.index), 'MB': df_results['FITS_Size_KB'].sum() / 1000}

        # Runs the function being tested.
        df_tech_appraisal_subtotal = subtotal(df_results, ['Technical_Appraisal', 'FITS_Format_Name'], totals_dict)

        # Makes a dataframe with the expected values.
        rows = [['No data of this type', np.NaN, np.NaN, np.NaN]]
        column_names = ['File Count', 'File %', 'Size (MB)', 'Size %']
        df_expected = pd.DataFrame(rows, columns=column_names)

        # Compares the script output to the expected values.
        self.assertEqual(df_tech_appraisal_subtotal, df_expected, 'Problem with technical appraisal subtotal - no files')

    def test_other_risk_subtotal(self):
        """Tests the other risk subtotal, which is based on other risk criteria and FITS_Format_Name."""

        # Makes a dataframe to use as input for the subtotal() function.
        # Data variation: for each of the values for other risk, has unique formats and duplicated formats.
        rows = [['Not for Other', 'DOS/Windows Executable', 100.23],
                ['Not for Other', 'JPEG EXIF', 1300.563],
                ['Not for Other', 'JPEG EXIF', 1400.1],
                ['Not for Other', 'JPEG EXIF', 1900.316],
                ['Not for Other', 'PE32 Executable', 200.34],
                ['Possible saved web page', 'Cascading Style Sheet', 10000],
                ['Archive format', 'Zip Format', 20000],
                ['Archive format', 'Zip Format', 20000],
                ['Archive format', 'Zip Format', 30000],
                ['Archive format', 'Zip Format', 30000]]
        column_names = ['Other_Risk', 'FITS_Format_Name', 'FITS_Size_KB']
        df_results = pd.DataFrame(rows, columns=column_names)

        # Calculates the total files and total size in the dataframe to use for percentages with the subtotal.
        # In format_analysis.py, this is done in the main body of the script before subtotal() is called.
        totals_dict = {'Files': len(df_results.index), 'MB': df_results['FITS_Size_KB'].sum() / 1000}

        # Runs the function being tested.
        df_other_risk_subtotal = subtotal(df_results, ['Other_Risk', 'FITS_Format_Name'], totals_dict)

        # Makes a dataframe with the expected values.
        # The index values for the dataframes made by subtotal() are column values here
        # so that they are visible in the comparison dataframe to label errors.
        rows = [['Not for Other', 'DOS/Windows Executable', 1, 10, 0.1, 0.087],
                ['Not for Other', 'JPEG EXIF', 3, 30, 4.601, 4.004],
                ['Not for Other', 'PE32 Executable', 1, 10, 0.2, 0.174],
                ['Possible saved web page', 'Cascading Style Sheet', 1, 10, 10, 8.703],
                ['Archive format', 'ZIP Format', 4, 40, 100, 87.031]]
        column_names = ['Other_Risk', 'FITS_Format_Name', 'File Count', 'File %', 'Size (MB)', 'Size %']
        df_expected = pd.DataFrame(rows, columns=column_names)

        # Compares the script output to the expected values.
        self.assertEqual(df_other_risk_subtotal, df_expected, 'Problem with other risk subtotal')

    def test_other_risk_subtotal_none(self):
        """Tests the other risk subtotal when there are no files in the input which meet any other risk criteria."""

        # Makes an empty dataframe to use as input for the subtotal() function.
        df_results = pd.DataFrame(columns=['Other_Risk', 'FITS_Format_Name', 'FITS_Size_KB'])

        # Calculates the total files and total size in the dataframe to use for percentages with the subtotal.
        # In format_analysis.py, this is done in the main body of the script before subtotal() is called.
        totals_dict = {'Files': len(df_results.index), 'MB': df_results['FITS_Size_KB'].sum() / 1000}

        # Runs the function being tested.
        df_other_risk_subtotal = subtotal(df_results, ['Other_Risk', 'FITS_Format_Name'], totals_dict)

        # Makes a dataframe with the expected values.
        rows = [['No data of this type', np.NaN, np.NaN, np.NaN]]
        column_names = ['File Count', 'File %', 'Size (MB)', 'Size %']
        df_expected = pd.DataFrame(rows, columns=column_names)

        # Compares the script output to the expected values.
        self.assertEqual(df_other_risk_subtotal, df_expected, 'Problem with other risk subtotal - no files')


if __name__ == '__main__':
    unittest.main()
