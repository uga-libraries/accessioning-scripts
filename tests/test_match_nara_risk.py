"""Tests combining NARA risk information with FITS information to produce df_results."""
# TODO: not tested

import numpy as np
import pandas as pd
import unittest
from format_analysis_functions import csv_to_dataframe, match_nara_risk
import configuration as c


class MyTestCase(unittest.TestCase):
    
    def test_match_nara_risk(self):
        
        # Makes a dataframe to use for FITS information.
        # PUID variations: match 1 PUID and multiple PUIDs
        # Name variations: match with version or name only, including case not matching
        # Extension variations: match single extension and pipe-separated extension, including case not matching
        # Also includes 2 that won't match
        rows = [[r'C:\PUID\file.zip', 'ZIP archive', np.NaN, 'https://www.nationalarchives.gov.uk/pronom/x-fmt/263'],
                [r'C:\PUID\3\movie.ifo', 'DVD Data File', np.NaN,
                 'https://www.nationalarchives.gov.uk/pronom/x-fmt/419'],
                [r'C:\Name\img.jp2', 'JPEG 2000 File Format', np.NaN, np.NaN],
                [r'C:\Name\Case\file.gz', 'gzip', np.NaN, np.NaN],
                [r'C:\Name\Version\database.nsf', 'Lotus Notes Database', '2', np.NaN],
                [r'C:\Ext\Both\file.dat', 'File Data', np.NaN, np.NaN],
                [r'C:\Ext\Case\file.BIN', 'Unknown Binary', np.NaN, np.NaN],
                [r'C:\Ext\Multi\img.jpg', 'JPEG', '1', np.NaN],
                [r'C:\Unmatched\file.new', 'Brand New Format', np.NaN, np.NaN],
                [r'C:\Unmatched\file.none', 'empty', np.NaN, np.NaN]]
        column_names = ['FITS_File_Path', 'FITS_Format_Name', 'FITS_Format_Version', 'FITS_PUID']
        df_fits = pd.DataFrame(rows, columns=column_names)

        # Reads the NARA risk CSV into a dataframe and runs the function.
        df_nara = csv_to_dataframe(c.NARA)
        df_results = match_nara_risk(df_fits, df_nara)

        # Makes a dataframe with the expected values.
        rows = [[r'C:\PUID\file.zip', 'ZIP archive', np.NaN, 'https://www.nationalarchives.gov.uk/pronom/x-fmt/263',
                 'ZIP archive', 'zip', 'https://www.nationalarchives.gov.uk/pronom/x-fmt/263', 'Moderate Risk',
                 'Retain but extract files from the container', 'PRONOM'],
                [r'C:\PUID\3\movie.ifo', 'DVD Data File', np.NaN,
                 'https://www.nationalarchives.gov.uk/pronom/x-fmt/419', 'DVD Data Backup File', 'bup',
                 'https://www.nationalarchives.gov.uk/pronom/x-fmt/419', 'Moderate Risk', 'Retain', 'PRONOM'],
                [r'C:\PUID\3\movie.ifo', 'DVD Data File', np.NaN,
                 'https://www.nationalarchives.gov.uk/pronom/x-fmt/419', 'DVD Data File', 'dvd',
                 'https://www.nationalarchives.gov.uk/pronom/x-fmt/419', 'Moderate Risk', 'Retain', 'PRONOM'],
                [r'C:\PUID\3\movie.ifo', 'DVD Data File', np.NaN,
                 'https://www.nationalarchives.gov.uk/pronom/x-fmt/419', 'DVD Info File', 'ifo',
                 'https://www.nationalarchives.gov.uk/pronom/x-fmt/419', 'Moderate Risk', 'Retain', 'PRONOM'],
                [r'C:\Name\img.jp2', 'JPEG 2000 File Format', np.NaN, np.NaN, 'JPEG 2000 File Format', 'jp2',
                 'https://www.nationalarchives.gov.uk/pronom/x-fmt/392', 'Low Risk', 'Retain', 'Format Name'],
                [r'C:\Name\Case\file.gz', 'gzip', np.NaN, np.NaN, 'GZIP', 'gz|tgz',
                 'https://www.nationalarchives.gov.uk/pronom/x-fmt/266', 'Low Risk',
                 'Retain but extract files from the container', 'Format Name'],
                [r'C:\Name\Version\database.nsf', 'Lotus Notes Database', '2', np.NaN, 'Lotus Notes Database 2',
                 'nsf|ns2', 'https://www.nationalarchives.gov.uk/pronom/x-fmt/336', 'Moderate Risk', 'Transform to CSV',
                 'Format Name'],
                [r'C:\Ext\Both\file.dat', 'File Data', np.NaN, np.NaN, 'Data File', 'dat', np.NaN, 'Moderate Risk',
                 'Retain', 'File Extension'],
                [r'C:\Ext\Both\file.dat', 'File Data', np.NaN, np.NaN, 'Windows Registry Files', 'reg|dat', np.NaN,
                 'Moderate Risk', 'Retain', 'File Extension'],
                [r'C:\Ext\Case\file.BIN', 'Unknown Binary', np.NaN, np.NaN, 'Binary file', 'bin',
                 'https://www.nationalarchives.gov.uk/pronom/fmt/208', 'High Risk', 'Retain', 'File Extension'],
                [r'C:\Ext\Multi\img.jpg', 'JPEG', '1', np.NaN, 'JPEG File Interchange Format 1.00', 'jpg|jpeg',
                 'https://www.nationalarchives.gov.uk/pronom/fmt/42', 'Low Risk', 'Retain', 'File Extension'],
                [r'C:\Ext\Multi\img.jpg', 'JPEG', '1', np.NaN, 'JPEG File Interchange Format 1.01', 'jpg|jpeg',
                 'https://www.nationalarchives.gov.uk/pronom/fmt/43', 'Low Risk', 'Retain', 'File Extension'],
                [r'C:\Ext\Multi\img.jpg', 'JPEG', '1', np.NaN, 'JPEG File Interchange Format 1.02', 'jpg|jpeg',
                 'https://www.nationalarchives.gov.uk/pronom/fmt/44', 'Low Risk', 'Retain', 'File Extension'],
                [r'C:\Ext\Multi\img.jpg', 'JPEG', '1', np.NaN, 'JPEG Raw Stream', 'jpg|jpeg',
                 'https://www.nationalarchives.gov.uk/pronom/fmt/41', 'Low Risk', 'Retain', 'File Extension'],
                [r'C:\Ext\Multi\img.jpg', 'JPEG', '1', np.NaN, 'JPEG unspecified version', 'jpg|jpeg', np.NaN,
                 'Low Risk', 'Retain', 'File Extension'],
                [r'C:\Unmatched\file.new', 'Brand New Format', np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, 'No Match',
                 np.NaN, 'No NARA Match'],
                [r'C:\Unmatched\file.none', 'empty', np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, 'No Match', np.NaN,
                 'No NARA Match']]
        column_names = ['FITS_File_Path', 'FITS_Format_Name', 'FITS_Format_Version', 'FITS_PUID',
                        'NARA_Format Name', 'NARA_File Extension(s)', 'NARA_PRONOM URL', 'NARA_Risk Level',
                        'NARA_Proposed Preservation Plan', 'NARA_Match_Type']
        df_expected = pd.DataFrame(rows, columns=column_names)

        # Using pandas test functionality because unittest assertEqual is unable to compare dataframes.
        pd.testing.assert_frame_equal(df_results, df_expected)


if __name__ == '__main__':
    unittest.main()
