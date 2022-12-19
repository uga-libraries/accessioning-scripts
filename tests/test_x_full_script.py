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
        Makes a collection folder with one accession folder that has files organized into 2 disks to use for testing.
        Formats included: csv, html, plain text, xlsx, zip
        Variations: duplicate files, empty file, file with multiple identifications (xlsx),
                    file with validation error (html), technical appraisal (empty, trash), other risk (zip)
        All subtotals and subsets in the final format analysis report will have some information.

        Also makes variables with the expected values for each tab in the final format analysis report.
        """
        # Makes a folder named collection, which contains a folder named accession,
        # which contains 2 folders named disk1 and disk2. The folder disk1 contains a folder named trash.
        self.disk1_path = os.path.join(os.getcwd(), 'collection', 'accession', 'disk1')
        self.disk2_path = os.path.join(os.getcwd(), 'collection', 'accession', 'disk2')
        self.trash_path = os.path.join(self.disk1_path, 'trash')
        os.makedirs(self.trash_path)
        os.makedirs(self.disk2_path)

        # Makes 3 text files in the trash folder, which are candidates for technical appraisal.
        with open(os.path.join(self.trash_path, 'trash.txt'), 'w') as file:
            file.write('Trash Text ' * 20)
        with open(os.path.join(self.trash_path, 'trash1.txt'), 'w') as file:
            file.write('Trash Text ' * 21)
        with open(os.path.join(self.trash_path, 'trash2.txt'), 'w') as file:
            file.write('Trash Text ' * 22)

        # Uses pandas to make an Excel spreadsheet in the disk1 folder, which have multiple FITs format ids.
        df_spreadsheet = pd.DataFrame()
        df_spreadsheet[['C1', 'C2', 'C2', 'C3', 'C4', 'C5']] = 'Text' * 5000
        df_spreadsheet = pd.concat([df_spreadsheet] * 3000, ignore_index=True)
        df_spreadsheet.to_excel(os.path.join(self.disk1_path, 'data.xlsx'), index=False)

        # Makes a text file in the disk1 folder and copies it to the disk2 folder to make a duplicate.
        with open(os.path.join(self.disk1_path, 'duplicate_file.txt'), 'w') as file:
            file.write('Text' * 900)
        shutil.copyfile(os.path.join(self.disk1_path, 'duplicate_file.txt'),
                        os.path.join(self.disk2_path, 'duplicate_file.txt'))

        # Makes a zip file of the contents of the disk1 folder and saves it to the disk2 folder.
        # Then makes 2 copies of the zip file and saves those to the disk2 folder.
        # Zip files are a format that meets the other risk criteria.
        shutil.make_archive(os.path.join(self.disk2_path, 'disk1backup'), 'zip', self.disk1_path)
        shutil.copyfile(os.path.join(self.disk2_path, 'disk1backup.zip'), os.path.join(self.disk2_path, 'disk1backup2.zip'))
        shutil.copyfile(os.path.join(self.disk2_path, 'disk1backup.zip'), os.path.join(self.disk2_path, 'disk1backup3.zip'))

        # Makes an empty text file in the disk2 folder, which is a candidate for technical appraisal.
        open(os.path.join(self.disk2_path, 'empty.txt'), 'w').close()

        # Makes a file that claims to be HTML but is in fact a text file, to get a validation error in the FITS.
        with open(os.path.join(self.disk2_path, 'error.html'), 'w') as file:
            file.write('<body>This is not really html</body>')

    def tearDown(self):
        """
        Deletes the test files.
        The initial test files and all script products are in the collection folder.
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

        # The next several code blocks makes lists with the expected values for each tab in format_analysis.xlsx.

        # Expected values for things that change (XLSX and ZIP) and are in more than one list are calculated here.
        # There are 3 copies of the zip file and this information is the same for all 3.
        today = datetime.date.today().strftime('%Y-%m-%d')
        xlsx_kb = round(os.path.getsize(os.path.join(self.disk1_path, 'data.xlsx')) / 1000, 3)
        xlsx_mb = round(xlsx_kb / 1000, 3)
        xlsx_md5 = md5(os.path.join(self.disk1_path, 'data.xlsx'))
        zip_kb = round(os.path.getsize(os.path.join(self.disk2_path, 'disk1backup.zip')) / 1000, 3)
        zip_mb = round((os.path.getsize(os.path.join(self.disk2_path, 'disk1backup.zip')) / 1000 * 3) / 1000, 3)
        zip_md5 = md5(os.path.join(self.disk2_path, 'disk1backup.zip'))
        total_mb = df_risk['FITS_Size_KB'].sum() / 1000

        # Expected values for the format subtotal.
        expected01 = [['FITS_Format_Name', 'NARA_Risk Level', 'File Count', 'File %', 'Size (MB)', 'Size %'],
                      ['empty', 'Low Risk', 1, 10, 0, 0],
                      ['Extensible Markup Language', 'Low Risk', 1, 10, 0, 0],
                      ['Office Open XML Workbook', 'Low Risk', 1, 10, xlsx_mb, round((xlsx_mb / total_mb) * 100, 3)],
                      ['Plain text', 'Low Risk', 3, 30, 0.008, round((0.008 / total_mb) * 100, 3)],
                      ['XLSX', 'Low Risk', 1, 10, xlsx_mb, round((xlsx_mb / total_mb) * 100, 3)],
                      ['ZIP Format', 'Moderate Risk', 3, 30, zip_mb, round((zip_mb / total_mb) * 100, 3)]]

        # Expected values for the NARA risk subtotal.
        low_mb = round(df_risk[df_risk['NARA_Risk Level'] == 'Low Risk']['FITS_Size_KB'].sum() / 1000, 3)
        expected02 = [['NARA_Risk Level', 'File Count', 'File %', 'Size (MB)', 'Size %'],
                      ['Low Risk', 7, 70, low_mb, round((low_mb / total_mb) * 100, 3)],
                      ['Moderate Risk', 3, 30, zip_mb, round((zip_mb / total_mb) * 100, 3)]]

        # Expected values for the tech appraisal subtotal.
        expected03 = [['Technical_Appraisal', 'FITS_Format_Name', 'File Count', 'File %', 'Size (MB)', 'Size %'],
                      ['Format', 'empty', 1, 10, 0, 0]]

        # Expected values for the other risk subtotal.
        expected04 = [['Other_Risk', 'FITS_Format_Name', 'File Count', 'File %', 'Size (MB)', 'Size %'],
                      ['Archive format', 'ZIP Format', 3, 30, zip_mb, round((zip_mb / total_mb) * 100, 3)]]

        # Expected values for the media subtotal.
        disk1_mb = round(df_risk[df_risk['FITS_File_Path'].str.contains(r'\\disk1\\')]['FITS_Size_KB'].sum() / 1000, 3)
        disk2_mb = round(df_risk[df_risk['FITS_File_Path'].str.contains(r'\\disk2\\')]['FITS_Size_KB'].sum() / 1000, 3)
        expected05 = [['Media', 'File Count', 'Size (MB)', 'NARA High Risk (File Count)',
                       'NARA Moderate Risk (File Count)', 'NARA Low Risk (File Count)', 'No NARA Match (File Count)',
                       'Technical Appraisal_Format (File Count)', 'Other Risk Indicator (File Count)'],
                      ['disk1', 3, disk1_mb, 0, 0, 3, 0, 0, 0], ['disk2', 7, disk2_mb, 0, 3, 4, 0, 1, 3]]

        # Expected values for the NARA risk subset.
        expected06 = [['FITS_File_Path', 'FITS_Format_Name', 'FITS_Format_Version', 'FITS_Multiple_IDs',
                       'FITS_Date_Last_Modified', 'FITS_Size_KB', 'FITS_MD5', 'NARA_Risk Level',
                       'NARA_Proposed Preservation Plan', 'NARA_Match_Type', 'Technical_Appraisal', 'Other_Risk'],
                      [os.path.join(self.disk2_path, 'disk1backup.zip'), 'ZIP Format', 2, False, today, zip_kb, zip_md5,
                       'Moderate Risk', 'Retain but extract files from the container', 'PRONOM', 'Not for TA',
                       'Archive format'],
                      [os.path.join(self.disk2_path, 'disk1backup2.zip'), 'ZIP Format', 2, False, today, zip_kb, zip_md5,
                       'Moderate Risk', 'Retain but extract files from the container', 'PRONOM', 'Not for TA',
                       'Archive format'],
                      [os.path.join(self.disk2_path, 'disk1backup3.zip'), 'ZIP Format', 2, False, today, zip_kb, zip_md5,
                       'Moderate Risk', 'Retain but extract files from the container', 'PRONOM', 'Not for TA',
                       'Archive format']]

        # Expected values for the tech appraisal subset.
        expected07 = [['FITS_File_Path', 'FITS_Format_Name', 'FITS_Format_Version', 'FITS_Identifying_Tool(s)',
                       'FITS_Multiple_IDs', 'FITS_Size_KB', 'FITS_Creating_Application', 'NARA_Risk Level',
                       'NARA_Proposed Preservation Plan', 'NARA_Match_Type', 'Technical_Appraisal', 'Other_Risk'],
                      [os.path.join(self.disk2_path, 'empty.txt'), 'empty', 'BLANK', 'file utility version 5.03',
                       False, 0, 'BLANK', 'Low Risk', 'Retain', 'File Extension', 'Format', 'Not for Other']]

        # Expected values for the other risk subset.
        expected08 = [['FITS_File_Path', 'FITS_Format_Name', 'FITS_Format_Version', 'FITS_Identifying_Tool(s)',
                       'FITS_Multiple_IDs', 'FITS_Size_KB', 'NARA_Risk Level', 'NARA_Proposed Preservation Plan',
                       'NARA_Match_Type', 'Technical_Appraisal', 'Other_Risk'],
                      [os.path.join(self.disk2_path, 'disk1backup.zip'), 'ZIP Format', 2,
                       'Droid version 6.4; file utility version 5.03; Exiftool version 11.54; ffident version 0.2; Tika version 1.21',
                       False, zip_kb, 'Moderate Risk', 'Retain but extract files from the container', 'PRONOM',
                       'Not for TA', 'Archive format'],
                      [os.path.join(self.disk2_path, 'disk1backup2.zip'), 'ZIP Format', 2,
                       'Droid version 6.4; file utility version 5.03; Exiftool version 11.54; ffident version 0.2; Tika version 1.21',
                       False, zip_kb, 'Moderate Risk', 'Retain but extract files from the container', 'PRONOM',
                       'Not for TA', 'Archive format'],
                      [os.path.join(self.disk2_path, 'disk1backup3.zip'), 'ZIP Format', 2,
                       'Droid version 6.4; file utility version 5.03; Exiftool version 11.54; ffident version 0.2; Tika version 1.21',
                       False, zip_kb, 'Moderate Risk', 'Retain but extract files from the container', 'PRONOM',
                       'Not for TA', 'Archive format']]

        # Expected values for the multiple format identifications subset.
        expected09 = [['FITS_File_Path', 'FITS_Format_Name', 'FITS_Format_Version', 'FITS_PUID',
                       'FITS_Identifying_Tool(s)', 'FITS_Multiple_IDs', 'FITS_Date_Last_Modified', 'FITS_Size_KB',
                       'FITS_MD5', 'FITS_Creating_Application', 'Technical_Appraisal', 'Other_Risk'],
                      [os.path.join(self.disk1_path, 'data.xlsx'), 'XLSX', 'BLANK', 'BLANK',
                       'Exiftool version 11.54', True, today, xlsx_kb, xlsx_md5, 'Microsoft Excel', 'Not for TA',
                       'Not for Other'],
                      [os.path.join(self.disk1_path, 'data.xlsx'), 'Office Open XML Workbook', 'BLANK', 'BLANK',
                       'Tika version 1.21', True, today, xlsx_kb, xlsx_md5, 'Microsoft Excel', 'Not for TA',
                       'Not for Other']]

        # Expected values for the duplicates subset.
        expected10 = [['FITS_File_Path', 'FITS_Size_KB', 'FITS_MD5'],
                      [os.path.join(self.disk2_path, 'disk1backup.zip'), zip_kb, zip_md5],
                      [os.path.join(self.disk2_path, 'disk1backup2.zip'), zip_kb, zip_md5],
                      [os.path.join(self.disk2_path, 'disk1backup3.zip'), zip_kb, zip_md5],
                      [os.path.join(self.disk2_path, 'duplicate_file.txt'), 3.6, 'c0090e0840270f422e0c357b719e8857'],
                      [os.path.join(self.disk1_path, 'duplicate_file.txt'), 3.6, 'c0090e0840270f422e0c357b719e8857']]

        # Expected values for the validation subset.
        expected11 = [['FITS_File_Path', 'FITS_Format_Name', 'FITS_Format_Version', 'FITS_PUID',
                       'FITS_Identifying_Tool(s)', 'FITS_Multiple_IDs', 'FITS_Date_Last_Modified', 'FITS_Size_KB',
                       'FITS_MD5', 'FITS_Creating_Application', 'FITS_Valid', 'FITS_Well-Formed',
                       'FITS_Status_Message', 'NARA_Risk Level', 'NARA_Proposed Preservation Plan',
                       'NARA_Match_Type', 'Technical_Appraisal', 'Other_Risk'],
                      [os.path.join(self.disk2_path, 'error.html'), 'Extensible Markup Language', 1,
                       'BLANK', 'Jhove version 1.20.1', False, today, 0.036, '14b55b1626bac03dc8e35fdb14b1f6ed',
                       'BLANK', True, True, 'Not able to determine type of end of line severity=info',
                       'Low Risk', 'Retain', 'Format Name', 'Not for TA', 'Not for Other']]

        # Compares the script results to the expected values.
        self.assertEqual(result01.sort(), expected01.sort(), 'Problem with format subtotal')
        self.assertEqual(result02, expected02, 'Problem with NARA risk subtotal')
        self.assertEqual(result03, expected03, 'Problem with technical appraisal subtotal')
        self.assertEqual(result04, expected04, 'Problem with other risk subtotal')
        self.assertEqual(result05, expected05, 'Problem with media subtotal')
        self.assertEqual(result06, expected06, 'Problem with NARA risk subset')
        self.assertEqual(result07, expected07, 'Problem with technical appraisal subset')
        self.assertEqual(result08, expected08, 'Problem with other risk subset')
        self.assertEqual(result09, expected09, 'Problem with multiple ids subset')
        self.assertEqual(result10, expected10, 'Problem with duplicates subset')
        self.assertEqual(result11, expected11, 'Problem with validation subset')


if __name__ == '__main__':
    unittest.main()
