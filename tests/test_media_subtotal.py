import pandas as pd
import unittest
from format_analysis_functions import media_subtotal

# TODO: not tested
class MyTestCase(unittest.TestCase):
    def test_media_subtotal_function(self):
        """Tests variations in subtotal."""

        # Makes a dataframe and accession_folder variable to use as input.
        # Data variations: Disks with and without each risk type, unique values and values to add for subtotal.
        accession_folder = r'C:\ACC'
        rows = [[r'C:\ACC\Disk1\file.txt', 120, 'Low Risk', 'Not for TA', 'Not for Other'],
                [r'C:\ACC\Disk1\file2.txt', 130, 'Low Risk', 'Not for TA', 'Not for Other'],
                [r'C:\ACC\Disk1\file3.txt', 140, 'Low Risk', 'Not for TA', 'Not for Other'],
                [r'C:\ACC\Disk2\photo.jpg', 12345, 'Low Risk', 'Not for TA', 'Not for Other'],
                [r'C:\ACC\Disk2\file.psd', 15671, 'Moderate Risk', 'Not for TA', 'Layered image file'],
                [r'C:\ACC\Disk2\file1.psd', 15672, 'Moderate Risk', 'Not for TA', 'Layered image file'],
                [r'C:\ACC\Disk2\file2.psd', 15673, 'Moderate Risk', 'Not for TA', 'Layered image file'],
                [r'C:\ACC\Disk2\file.bak', 700, 'High Risk', 'Not for TA', 'Not for Other'],
                [r'C:\ACC\Disk2\empty.ext', 0, 'No Match', 'Format', 'Not for Other'],
                [r'C:\ACC\Disk2\empty1.ext', 0, 'No Match', 'Format', 'Not for Other'],
                [r'C:\ACC\Disk3\trash\file.bak', 700, 'High Risk', 'Trash', 'Not for Other'],
                [r'C:\ACC\Disk3\trash\empty.ext', 0, 'No Match', 'Trash', 'Not for Other'],
                [r'C:\ACC\Disk3\file.exe', 50, 'High Risk', 'Format', 'Not for Other'],
                [r'C:\ACC\Disk3\file.psd', 1567, 'Moderate Risk', 'Trash', 'Layered image file'],
                [r'C:\ACC\Disk4\file.css', 123, 'Low Risk', 'Not for TA', 'Possible saved web page'],
                [r'C:\ACC\Disk4\file.ics', 14455, 'Low Risk', 'Not for TA', 'NARA Low/Transform'],
                [r'C:\ACC\Disk4\draft\file.css', 125, 'Low Risk', 'Not for TA', 'Possible saved web page'],
                [r'C:\ACC\Disk4\draft\file.ics', 14457, 'Low Risk', 'Not for TA', 'NARA Low/Transform'],
                [r'C:\ACC\Disk4\draft\file.zip', 3399, 'Moderate Risk', 'Not for TA', 'Archive format'],
                [r'C:\ACC\Disk4\draft2\file.css', 145, 'Low Risk', 'Not for TA', 'Possible saved web page'],
                [r'C:\ACC\Disk4\draft2\file.ics', 116000, 'Low Risk', 'Not for TA', 'NARA Low/Transform'],
                [r'C:\ACC\log.txt', 12, 'Low Risk', 'Not for TA', 'Not for Other']]
        column_names = ['FITS_File_Path', 'FITS_Size_KB', 'NARA_Risk Level', 'Technical_Appraisal', 'Other_Risk']
        df_results = pd.DataFrame(rows, columns=column_names)

        # Runs the function being tested.
        df_media_subtotal = media_subtotal(df_results, accession_folder)

        # Makes a dataframe with the expected values.
        rows = [['Disk1', 3, 0.39, 0, 0, 3, 0, 0, 0],
                ['Disk2', 7, 60.061, 1, 3, 1, 2, 2, 3],
                ['Disk3', 4, 2.317, 2, 1, 0, 1, 1, 1],
                ['Disk4', 7, 148.704, 0, 1, 6, 0, 0, 7]]
        column_names = ['Media', 'File Count', 'Size (MB)', 'NARA High Risk (File Count)',
                        'NARA Moderate Risk (File Count)', 'NARA Low Risk (File Count)', 'No NARA Match (File Count)',
                        'Technical Appraisal_Format (File Count)', 'Other Risk Indicator (File Count)']
        df_expected = pd.DataFrame(rows, columns=column_names)
        df_expected.set_index('Media')

        # Compares the script output to the expected values.
        self.assertEqual(df_media_subtotal, df_expected, 'Problem with media subtotal')


if __name__ == '__main__':
    unittest.main()
