import numpy as np
import pandas as pd
import unittest
import configuration as c
from format_analysis_functions import csv_to_dataframe, match_other_risk


class MyTestCase(unittest.TestCase):
    def test_something(self):
        """Tests adding other risk categories to df_results, which already has information from FITS, NARA,
            and technical appraisal."""

        # Makes a dataframe to use as input.
        # Data variation: examples that match both, one, or neither of the other risk categories,
        #                 with identical cases and different cases (match is case-insensitive),
        #                 and at least one each of the format risk criteria.
        rows = [['Adobe Photoshop file', 'Moderate Risk', 'Transform to TIFF or JPEG2000'],
                ['Cascading Style Sheet', 'Low Risk', 'Retain'],
                ['CorelDraw Drawing', 'High Risk', 'Transform to a TBD format, possibly PDF or TIFF'],
                ['empty', np.NaN, np.NaN],
                ['Encapsulated Postscript File', 'Low Risk', 'Transform to TIFF or JPEG2000'],
                ['iCalendar', 'Low Risk', 'Transform to CSV'],
                ['MBOX Email Format', 'Low Risk', 'Transform to EML but also retain MBOX'],
                ['Plain text', 'Low Risk', 'Retain'],
                ['zip format', 'Low Risk', 'Retain']]
        column_names = ['FITS_Format_Name', 'NARA_Risk Level', 'NARA_Proposed Preservation Plan']
        df_results = pd.DataFrame(rows, columns=column_names)

        # Reads the risk file formats CSV into a dataframe and runs the function being tested.
        df_other = csv_to_dataframe(c.RISK)
        df_results = match_other_risk(df_results, df_other)

        # Makes a dataframe with the expected values.
        rows = [['Adobe Photoshop file', 'Moderate Risk', 'Transform to TIFF or JPEG2000', 'Layered image file'],
                ['Cascading Style Sheet', 'Low Risk', 'Retain', 'Possible saved web page'],
                ['CorelDraw Drawing', 'High Risk', 'Transform to a TBD format, possibly PDF or TIFF', 'Layered image file'],
                ['empty', np.NaN, np.NaN, 'Not for Other'],
                ['Encapsulated Postscript File', 'Low Risk', 'Transform to TIFF or JPEG2000', 'Layered image file'],
                ['iCalendar', 'Low Risk', 'Transform to CSV', 'NARA Low/Transform'],
                ['MBOX Email Format', 'Low Risk', 'Transform to EML but also retain MBOX', 'NARA Low/Transform'],
                ['Plain text', 'Low Risk', 'Retain', 'Not for Other'],
                ['zip format', 'Low Risk', 'Retain', 'Archive format']]
        column_names = ['FITS_Format_Name', 'NARA_Risk Level', 'NARA_Proposed Preservation Plan', 'Other_Risk']
        df_expected = pd.DataFrame(rows, columns=column_names)

        # Using pandas test functionality because unittest assertEqual is unable to compare dataframes.
        pd.testing.assert_frame_equal(df_results, df_expected)


if __name__ == '__main__':
    unittest.main()
