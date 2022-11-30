import pandas as pd
import unittest


# TODO: not tested. This is not a function.
class MyTestCase(unittest.TestCase):
    def test_something(self):
        """Tests that duplicates from multiple NARA matches with the same risk information are correctly removed.
            In format_analysis.py, this is done in the main body of the script."""

        # Makes a dataframe to use as input, with a subset of the columns usually in df_results.
        # Data variation: one FITS ID with one NARA match, multiple FITS IDs with one NARA match each,
        #                 multiple NARA matches with the same risk, multiple NARA matches with different risks.
        rows = [[r'C:\acc\disk1\data.csv', 'Comma-Separated Values (CSV)', 'Comma Separated Values', 'csv',
                 'https://www.nationalarchives.gov.uk/pronom/x-fmt/18', 'Low Risk', 'Retain'],
                [r'C:\acc\disk1\data.xlsx', 'Open Office XML Workbook', 'Microsoft Excel Office Open XML', 'xlsx',
                 'https://www.nationalarchives.gov.uk/pronom/fmt/214', 'Low Risk', 'Retain'],
                [r'C:\acc\disk1\data.xlsx', 'XLSX', 'Microsoft Excel Office Open XML', 'xlsx',
                 'https://www.nationalarchives.gov.uk/pronom/fmt/214', 'Low Risk', 'Retain'],
                [r'C:\acc\disk1\empty.txt', 'empty', 'ASCII 7-bit Text', 'txt|asc|csv|tab',
                 'https://www.nationalarchives.gov.uk/pronom/x-fmt/22', 'Low Risk', 'Retain'],
                [r'C:\acc\disk1\empty.txt', 'empty', 'ASCII 8-bit Text', 'txt|asc|csv|tab',
                 'https://www.nationalarchives.gov.uk/pronom/x-fmt/283', 'Low Risk', 'Retain'],
                [r'C:\acc\disk1\empty.txt', 'empty', 'JSON', 'json|txt',
                 'https://www.nationalarchives.gov.uk/pronom/fmt/817', 'Low Risk', 'Retain'],
                [r'C:\acc\disk1\empty.txt', 'empty', 'Plain Text', 'Plain_Text|txt|text|asc|rte',
                 'https://www.nationalarchives.gov.uk/pronom/x-fmt/111', 'Low Risk', 'Retain'],
                [r'C:\acc\disk1\file.pdf', 'PDF', 'Portable Document Format (PDF) version 1.7', 'pdf',
                 'https://www.nationalarchives.gov.uk/pronom/fmt/276', 'Moderate Risk', 'Retain'],
                [r'C:\acc\disk1\file.pdf', 'PDF', 'Portable Document Format (PDF) version 2.0', 'pdf',
                 'https://www.nationalarchives.gov.uk/pronom/fmt/1129', 'Moderate Risk', 'Retain'],
                [r'C:\acc\disk1\file.pdf', 'PDF', 'Portable Document Format/Archiving (PDF/A-1a) accessible', 'pdf',
                 'https://www.nationalarchives.gov.uk/pronom/fmt/95', 'Low Risk', 'Retain']]
        column_names = ['FITS_File_Path', 'FITS_Format_Name', 'NARA_Format Name', 'NARA_File Extension(s)',
                        'NARA_PRONOM URL', 'NARA_Risk Level', 'NARA_Proposed Preservation Plan']
        df_results = pd.DataFrame(rows, columns=column_names)

        # RUNS THE CODE BEING TESTED: Removes columns with NARA identification info and then removes duplicate rows.
        df_results.drop(['NARA_Format Name', 'NARA_File Extension(s)', 'NARA_PRONOM URL'], inplace=True, axis=1)
        df_results.drop_duplicates(inplace=True)

        # Makes a dataframe with the expected values.
        rows = [[r'C:\acc\disk1\data.csv', 'Comma-Separated Values (CSV)', 'Low Risk', 'Retain'],
                [r'C:\acc\disk1\data.xlsx', 'Open Office XML Workbook', 'Low Risk', 'Retain'],
                [r'C:\acc\disk1\data.xlsx', 'XLSX', 'Low Risk', 'Retain'],
                [r'C:\acc\disk1\empty.txt', 'empty', 'Low Risk', 'Retain'],
                [r'C:\acc\disk1\file.pdf', 'PDF', 'Moderate Risk', 'Retain'],
                [r'C:\acc\disk1\file.pdf', 'PDF', 'Low Risk', 'Retain']]
        column_names = ['FITS_File_Path', 'FITS_Format_Name', 'NARA_Risk Level', 'NARA_Proposed Preservation Plan']
        df_expected = pd.DataFrame(rows, columns=column_names)

        # Compares the script output to the expected values.
        self.assertEqual(df_results, df_expected, 'Problem with deduplicating dataframe')


if __name__ == '__main__':
    unittest.main()
