"""Tests running the entire script through multiple iterations."""

import datetime
import hashlib
import os
import pandas as pd
import shutil
import subprocess
import unittest


def md5(file_path):
    """Calculates the MD5 of the specified file path. Reads the file in chunks to avoid memory issues.
    Returns the MD5."""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


class MyTestCase(unittest.TestCase):

    def setUp(self):
        """
        Copies test files organized into 1 accession with 2 disks to use for testing.
        The tests edit these files, so a copy must be used.
        Also makes variables with the expected values for each tab in the final format analysis report.
        """
        # Copies the folder to use for testing.
        # Formats included: csv, html, plain text, xlsx, zip
        # Variations: duplicate files, empty file, file with multiple identifications (xlsx),
        #             file with validation error (html), technical appraisal (empty, trash), other risk (zip)
        # All subtotals and subsets in the final format analysis report will have some information.
        shutil.copytree('test_collection', 'collection')

        # Paths to the folders in the copied collection to use throughout the tests.
        self.disk1_path = os.path.join(os.getcwd(), 'collection', 'accession', 'disk1')
        self.disk2_path = os.path.join(os.getcwd(), 'collection', 'accession', 'disk2')
        self.trash_path = os.path.join(os.getcwd(), 'collection', 'accession', 'disk1', 'trash')

        # Expected values for each tab in accession_format-analysis.xlsx
        # These could be in the main code for the test, but it is already long.

        # Expected values for the format subtotal.
        self.ex01 = [['FITS_Format_Name', 'NARA_Risk Level', 'File Count', 'File %', 'Size (MB)', 'Size %'],
                     ['empty', 'Low Risk', 1, 10, 0, 0],
                     ['Extensible Markup Language', 'Low Risk', 1, 10, 0, 0],
                     ['Office Open XML Workbook', 'Low Risk', 1, 10, 0.005, 14.002],
                     ['Plain text', 'Low Risk', 3, 30, 0.008, 22.403],
                     ['XLSX', 'Low Risk', 1, 10, .005, 14.002],
                     ['ZIP Format', 'Moderate Risk', 3, 30, 0.016, 44.805]]

        # Expected values for the NARA risk subtotal.
        self.ex02 = [['NARA_Risk Level', 'File Count', 'File %', 'Size (MB)', 'Size %'],
                     ['Low Risk', 7, 70, 0.019, 53.206],
                     ['Moderate Risk', 3, 30, 0.016, 44.805]]

        # Expected values for the tech appraisal subtotal.
        self.ex03 = [['Technical_Appraisal', 'FITS_Format_Name', 'File Count', 'File %', 'Size (MB)', 'Size %'],
                     ['Format', 'empty', 1, 10, 0, 0]]

        # Expected values for the other risk subtotal.
        self.ex04 = [['Other_Risk', 'FITS_Format_Name', 'File Count', 'File %', 'Size (MB)', 'Size %'],
                     ['Archive format', 'ZIP Format', 3, 30, 0.016, 44.805]]

        # Expected values for the media subtotal.
        self.ex05 = [['Media', 'File Count', 'Size (MB)', 'NARA High Risk (File Count)',
                      'NARA Moderate Risk (File Count)', 'NARA Low Risk (File Count)', 'No NARA Match (File Count)',
                      'Technical Appraisal_Format (File Count)', 'Other Risk Indicator (File Count)'],
                     ['disk1', 3, 0.014, 0, 0, 3, 0, 0, 0], ['disk2', 7, 0.021, 0, 3, 4, 0, 1, 3]]

        # Expected values for the NARA risk subset.
        self.ex06 = [['FITS_File_Path', 'FITS_Format_Name', 'FITS_Format_Version', 'FITS_Multiple_IDs',
                      'FITS_Date_Last_Modified', 'FITS_Size_KB', 'FITS_MD5', 'NARA_Risk Level',
                      'NARA_Proposed Preservation Plan', 'NARA_Match_Type', 'Technical_Appraisal', 'Other_Risk'],
                     [os.path.join(self.disk2_path, 'disk1backup.zip'), 'ZIP Format', 2, False, '2023-02-14', 5.488,
                      'd585e96a134ddb7ca6764d41a62f20a1', 'Moderate Risk',
                      'Retain but extract files from the container', 'PRONOM', 'Not for TA',
                      'Archive format'],
                     [os.path.join(self.disk2_path, 'disk1backup2.zip'), 'ZIP Format', 2, False, '2023-02-14', 5.488,
                      'd585e96a134ddb7ca6764d41a62f20a1', 'Moderate Risk',
                      'Retain but extract files from the container', 'PRONOM', 'Not for TA', 'Archive format'],
                     [os.path.join(self.disk2_path, 'disk1backup3.zip'), 'ZIP Format', 2, False, '2023-02-14', 5.488,
                      'd585e96a134ddb7ca6764d41a62f20a1', 'Moderate Risk',
                      'Retain but extract files from the container', 'PRONOM', 'Not for TA', 'Archive format']]

        # Expected values for the tech appraisal subset.
        self.ex07 = [['FITS_File_Path', 'FITS_Format_Name', 'FITS_Format_Version', 'FITS_Identifying_Tool(s)',
                      'FITS_Multiple_IDs', 'FITS_Size_KB', 'FITS_Creating_Application', 'NARA_Risk Level',
                      'NARA_Proposed Preservation Plan', 'NARA_Match_Type', 'Technical_Appraisal', 'Other_Risk'],
                     [os.path.join(self.disk2_path, 'empty.txt'), 'empty', 'BLANK', 'file utility version 5.03',
                      False, 0, 'BLANK', 'Low Risk', 'Retain', 'File Extension', 'Format', 'Not for Other']]

        # Expected values for the other risk subset.
        self.ex08 = [['FITS_File_Path', 'FITS_Format_Name', 'FITS_Format_Version', 'FITS_Identifying_Tool(s)',
                      'FITS_Multiple_IDs', 'FITS_Size_KB', 'NARA_Risk Level', 'NARA_Proposed Preservation Plan',
                      'NARA_Match_Type', 'Technical_Appraisal', 'Other_Risk'],
                     [os.path.join(self.disk2_path, 'disk1backup.zip'), 'ZIP Format', 2,
                      'Droid version 6.4; file utility version 5.03; Exiftool version 11.54; ffident version 0.2; Tika version 1.21',
                      False, 5.488, 'Moderate Risk', 'Retain but extract files from the container', 'PRONOM',
                      'Not for TA', 'Archive format'],
                     [os.path.join(self.disk2_path, 'disk1backup2.zip'), 'ZIP Format', 2,
                      'Droid version 6.4; file utility version 5.03; Exiftool version 11.54; ffident version 0.2; Tika version 1.21',
                      False, 5.488, 'Moderate Risk', 'Retain but extract files from the container', 'PRONOM',
                      'Not for TA', 'Archive format'],
                     [os.path.join(self.disk2_path, 'disk1backup3.zip'), 'ZIP Format', 2,
                      'Droid version 6.4; file utility version 5.03; Exiftool version 11.54; ffident version 0.2; Tika version 1.21',
                      False, 5.488, 'Moderate Risk', 'Retain but extract files from the container', 'PRONOM',
                      'Not for TA', 'Archive format']]

        # Expected values for the multiple format identifications subset.
        self.ex09 = [['FITS_File_Path', 'FITS_Format_Name', 'FITS_Format_Version', 'FITS_PUID',
                      'FITS_Identifying_Tool(s)', 'FITS_Multiple_IDs', 'FITS_Date_Last_Modified', 'FITS_Size_KB',
                      'FITS_MD5', 'FITS_Creating_Application', 'Technical_Appraisal', 'Other_Risk'],
                     [os.path.join(self.disk1_path, 'data.xlsx'), 'XLSX', 'BLANK', 'BLANK',
                      'Exiftool version 11.54', True, '2023-02-14', 5.405, 'e6e80af91da856ed8b3b7a6e14a7840d',
                      'Microsoft Excel', 'Not for TA', 'Not for Other'],
                     [os.path.join(self.disk1_path, 'data.xlsx'), 'Office Open XML Workbook', 'BLANK', 'BLANK',
                      'Tika version 1.21', True, '2023-02-14', 5.405, 'e6e80af91da856ed8b3b7a6e14a7840d',
                      'Microsoft Excel', 'Not for TA', 'Not for Other']]

        # Expected values for the duplicates subset.
        self.ex10 = [['FITS_File_Path', 'FITS_Size_KB', 'FITS_MD5'],
                      [os.path.join(self.disk2_path, 'disk1backup.zip'), 5.488, 'd585e96a134ddb7ca6764d41a62f20a1'],
                      [os.path.join(self.disk2_path, 'disk1backup2.zip'), 5.488, 'd585e96a134ddb7ca6764d41a62f20a1'],
                      [os.path.join(self.disk2_path, 'disk1backup3.zip'), 5.488, 'd585e96a134ddb7ca6764d41a62f20a1'],
                      [os.path.join(self.disk2_path, 'duplicate_file.txt'), 3.6, 'c0090e0840270f422e0c357b719e8857'],
                      [os.path.join(self.disk1_path, 'duplicate_file.txt'), 3.6, 'c0090e0840270f422e0c357b719e8857']]

        # Expected values for the validation subset.
        self.ex11 = [['FITS_File_Path', 'FITS_Format_Name', 'FITS_Format_Version', 'FITS_PUID',
                      'FITS_Identifying_Tool(s)', 'FITS_Multiple_IDs', 'FITS_Date_Last_Modified', 'FITS_Size_KB',
                      'FITS_MD5', 'FITS_Creating_Application', 'FITS_Valid', 'FITS_Well-Formed',
                      'FITS_Status_Message', 'NARA_Risk Level', 'NARA_Proposed Preservation Plan',
                      'NARA_Match_Type', 'Technical_Appraisal', 'Other_Risk'],
                     [os.path.join(self.disk2_path, 'error.html'), 'Extensible Markup Language', 1,
                      'BLANK', 'Jhove version 1.20.1', False, '2023-02-14', 0.036, '14b55b1626bac03dc8e35fdb14b1f6ed',
                      'BLANK', True, True, 'Not able to determine type of end of line severity=info',
                      'Low Risk', 'Retain', 'Format Name', 'Not for TA', 'Not for Other']]

    def tearDown(self):
        """
        Deletes the collection folder, with the altered copy of the test files and script outputs.
        """
        shutil.rmtree('collection')

    def test_iteration(self):
        """
        Tests that the script follows the correct logic based on the contents of the accession folder and
        that the contents are updated correctly. Runs the script 3 times to check all iterations:
            1. Start from scratch,
            2. Use existing FITS files (updating to match the accession folder), and
            3. Use existing full risk data csv.
        Results for testing are the messages indicating which iteration of the script is running and
        the contents of the format_analysis.xlsx spreadsheet produced after 3 rounds of running the code.
        """
        # ROUND ONE

        # Runs the script on the test accession folder and tests if the expected messages were produced.
        # In format_analysis.py, these messages are printed to the terminal for archivist review.
        script_path = os.path.join('..', 'format_analysis.py')
        accession_path = os.path.join(os.getcwd(), 'collection', 'accession')
        iteration_one = subprocess.run(f'python {script_path} {accession_path}', shell=True, stdout=subprocess.PIPE)
        msg = '\r\nGenerating new FITS format identification information.\r\n\r\n' \
              'Generating new risk data for the analysis report.\r\n'
        self.assertEqual(iteration_one.stdout.decode('utf-8'), msg, 'Problem with Iteration_Message_1')

        # ROUND TWO

        # Deletes the trash folder and adds a file to the accession folder to simulate archivist appraisal.
        # Also deletes the full_risk_data.csv so an updated one will be made with the changes.
        shutil.rmtree(self.trash_path)
        with open(os.path.join(self.disk2_path, 'new.txt'), 'w') as file:
            file.write('Text' * 300)
        os.remove(os.path.join(os.getcwd(), 'collection', 'accession_full_risk_data.csv'))

        # Runs the script again on the test accession folder.
        # It will update the FITS files to match the accession folder and update the three spreadsheets.
        iteration_two = subprocess.run(f'python {script_path} {accession_path}', shell=True, stdout=subprocess.PIPE)
        msg = '\r\nUpdating the XML files in the FITS folder to match the files in the accession folder.\r\n' \
              'This will update fits.csv but will NOT update full_risk_data.csv from a previous script iteration.\r\n' \
              'Delete full_risk_data.csv before the script gets to that step for it to be remade with the new information.\r\n\r\n' \
              'Generating new risk data for the analysis report.\r\n'
        self.assertEqual(iteration_two.stdout.decode('utf-8'), msg, 'Problem with Iteration_Message_2')

        # ROUND THREE

        # Edits the full_risk_data.csv to simulate archivist cleaning up risk matches.
        # Removes the FITS format ID of Zip Format from the Excel file and
        # removes all NARA matches for empty.txt except for Plain Text.
        df_risk = pd.read_csv(os.path.join(os.getcwd(), 'collection', 'accession_full_risk_data.csv'))
        xlsx_to_drop = df_risk[(df_risk['FITS_File_Path'].str.endswith('data.xlsx')) &
                               (df_risk['FITS_Format_Name'] == 'ZIP Format')]
        empty_to_drop = df_risk[(df_risk['FITS_File_Path'].str.endswith('empty.txt')) &
                                (df_risk['NARA_Format Name'] != 'Plain Text')]
        df_risk.drop(xlsx_to_drop.index, inplace=True)
        df_risk.drop(empty_to_drop.index, inplace=True)
        df_risk.to_csv(os.path.join(os.getcwd(), 'collection', 'accession_full_risk_data.csv'), index=False)

        # Runs the script again on the test accession folder.
        # It will use existing fits.csv and full_risk_data.csv to update format_analysis.xlsx.
        iteration_three = subprocess.run(f'python {script_path} {accession_path}', shell=True, stdout=subprocess.PIPE)
        msg = '\r\nUpdating the XML files in the FITS folder to match the files in the accession folder.\r\n' \
              'This will update fits.csv but will NOT update full_risk_data.csv from a previous script iteration.\r\n' \
              'Delete full_risk_data.csv before the script gets to that step for it to be remade with the new information.\r\n\r\n' \
              'Updating the analysis report using existing risk data.\r\n'
        self.assertEqual(iteration_three.stdout.decode('utf-8'), msg, 'Problem with Iteration_Message_3')

        # Makes a dataframe with the values from each tab in format_analysis.xlsx made by the script.
        # Replaces NaN with 'BLANK' to avoid comparison problems with NaN.
        xlsx = pd.ExcelFile(os.path.join('collection', 'accession_format-analysis.xlsx'))
        df_format_subtotal = pd.read_excel(xlsx, 'Format Subtotal')
        df_format_subtotal.fillna('BLANK', inplace=True)
        df_nara_risk_subtotal = pd.read_excel(xlsx, 'NARA Risk Subtotal')
        df_nara_risk_subtotal.fillna('BLANK', inplace=True)
        df_tech_appraisal_subtotal = pd.read_excel(xlsx, 'Tech Appraisal Subtotal')
        df_tech_appraisal_subtotal.fillna('BLANK', inplace=True)
        df_other_risk_subtotal = pd.read_excel(xlsx, 'Other Risk Subtotal')
        df_other_risk_subtotal.fillna('BLANK', inplace=True)
        df_media_subtotal = pd.read_excel(xlsx, 'Media Subtotal')
        df_media_subtotal.fillna('BLANK', inplace=True)
        df_nara_risk = pd.read_excel(xlsx, 'NARA Risk')
        df_nara_risk.fillna('BLANK', inplace=True)
        df_tech_appraisal = pd.read_excel(xlsx, 'For Technical Appraisal')
        df_tech_appraisal.fillna('BLANK', inplace=True)
        df_other_risk = pd.read_excel(xlsx, 'Other Risks')
        df_other_risk.fillna('BLANK', inplace=True)
        df_multiple_ids = pd.read_excel(xlsx, 'Multiple Formats')
        df_multiple_ids.fillna('BLANK', inplace=True)
        df_duplicates = pd.read_excel(xlsx, 'Duplicates')
        df_duplicates.fillna('BLANK', inplace=True)
        df_validation = pd.read_excel(xlsx, 'Validation')
        df_validation.fillna('BLANK', inplace=True)
        xlsx.close()

        # Makes a list from each result dataframe, including the column headers, for easier comparison.
        result01 = [df_format_subtotal.columns.to_list()] + df_format_subtotal.values.tolist()
        result02 = [df_nara_risk_subtotal.columns.to_list()] + df_nara_risk_subtotal.values.tolist()
        result03 = [df_tech_appraisal_subtotal.columns.to_list()] + df_tech_appraisal_subtotal.values.tolist()
        result04 = [df_other_risk_subtotal.columns.to_list()] + df_other_risk_subtotal.values.tolist()
        result05 = [df_media_subtotal.columns.to_list()] + df_media_subtotal.values.tolist()
        result06 = [df_nara_risk.columns.to_list()] + df_nara_risk.values.tolist()
        result07 = [df_tech_appraisal.columns.to_list()] + df_tech_appraisal.values.tolist()
        result08 = [df_other_risk.columns.to_list()] + df_other_risk.values.tolist()
        result09 = [df_multiple_ids.columns.to_list()] + df_multiple_ids.values.tolist()
        result10 = [df_duplicates.columns.to_list()] + df_duplicates.values.tolist()
        result11 = [df_validation.columns.to_list()] + df_validation.values.tolist()

        # Compares the script results to the expected values.
        self.assertEqual(result01.sort(), self.ex01.sort(), 'Problem with format subtotal')
        self.assertEqual(result02, self.ex02, 'Problem with NARA risk subtotal')
        self.assertEqual(result03, self.ex03, 'Problem with technical appraisal subtotal')
        self.assertEqual(result04, self.ex04, 'Problem with other risk subtotal')
        self.assertEqual(result05, self.ex05, 'Problem with media subtotal')
        self.assertEqual(result06, self.ex06, 'Problem with NARA risk subset')
        self.assertEqual(result07, self.ex07, 'Problem with technical appraisal subset')
        self.assertEqual(result08, self.ex08, 'Problem with other risk subset')
        self.assertEqual(result09, self.ex09, 'Problem with multiple ids subset')
        self.assertEqual(result10, self.ex10, 'Problem with duplicates subset')
        self.assertEqual(result11, self.ex11, 'Problem with validation subset')


if __name__ == '__main__':
    unittest.main()
