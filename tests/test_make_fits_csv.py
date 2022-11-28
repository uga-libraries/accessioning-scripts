import datetime
import gzip
import numpy as np
import os
import pandas as pd
import shutil
import subprocess
import unittest
import configuration as c
from format_analysis_functions import make_fits_csv


class MyTestCase(unittest.TestCase):
    def test_make_fits_csv(self):
        """Tests all known variations for FITS data extraction and reformatting."""

        # Makes an accession folder with files organized into 2 folders.
        # Formats included: csv, gzip, html, plain text, xlsx
        # Variations: one and multiple format ids, with and without optional fields, one or multiple tools,
        #             empty with another format id, file with multiple ids with same name and one has PUID (gzip).
        os.makedirs(r"accession\disk1")
        df_spreadsheet = pd.DataFrame({"C1": ["text" * 1000], "C2": ["text" * 1000], "C3": ["text" * 1000]})
        df_spreadsheet = pd.concat([df_spreadsheet] * 500, ignore_index=True)
        df_spreadsheet.to_csv(r"accession\disk1\data.csv", index=False)
        df_spreadsheet.to_excel(r"accession\disk1\data.xlsx", index=False)
        df_spreadsheet["C3"] = "New Text" * 10000
        df_spreadsheet.to_csv(r"accession\disk1\data_update.csv", index=False)
        with open(r"accession\disk1\file.txt", "w") as file:
            file.write("Text" * 500)
        os.makedirs(r"accession\disk2")
        with open(r"accession\disk2\file.txt", "w") as file:
            file.write("Text" * 550)
        with open(r"accession\disk2\error.html", "w") as file:
            file.write("<body>This isn't really html</body>")
        open(r"accession\disk2\empty.txt", "w").close()
        with gzip.open(r"accession\disk2\zipping.gz", "wb") as file:
            file.write(b"Test Text\n" * 100000)

        # Makes FITS XML for the accession to use for testing.
        # In format_analysis.py, there is also error handling for if FITS has a load class error.
        os.mkdir('accession_FITS')
        subprocess.run(f'"{c.FITS}" -r -i "accession" -o "accession_FITS"', shell=True)

        # RUNS THE FUNCTION BEING TESTED.
        make_fits_csv(fr"accession_FITS", 'accession_FITS', os.getcwd(), "accession")

        # Makes a dataframe with the expected values.
        # Calculates size for XLSX because the size varies every time it is made.
        today = datetime.date.today().strftime('%Y-%m-%d')
        rows = [[fr"accession\disk1\data.csv", "Comma-Separated Values (CSV)", np.NaN,
                 "https://www.nationalarchives.gov.uk/pronom/x-fmt/18", "Droid version 6.4", False, today, 6002.01,
                 "f95a4c954014342e4bf03f51fcefaecd", np.NaN, np.NaN, np.NaN, np.NaN],
                [fr"accession\disk1\data.xlsx", "ZIP Format", 2,
                 "https://www.nationalarchives.gov.uk/pronom/x-fmt/263",
                 "Droid version 6.4; file utility version 5.03; ffident version 0.2", True, today,
                 round(os.path.getsize(fr"accession\disk1\data.xlsx") / 1000, 3), "XXXXXXXXXX",
                 "Microsoft Excel", np.NaN, np.NaN, np.NaN],
                [fr"accession\disk1\data.xlsx", "XLSX", np.NaN, np.NaN, "Exiftool version 11.54", True, today,
                 round(os.path.getsize(fr"accession\disk1\data.xlsx") / 1000, 3), "XXXXXXXXXX",
                 "Microsoft Excel", np.NaN, np.NaN, np.NaN],
                [fr"accession\disk1\data.xlsx", "Office Open XML Workbook", np.NaN, np.NaN,
                 "Tika version 1.21",
                 True, today, round(os.path.getsize(fr"accession\disk1\data.xlsx") / 1000, 3),
                 "XXXXXXXXXX", "Microsoft Excel", np.NaN, np.NaN, np.NaN],
                [fr"accession\disk1\data_update.csv", "Comma-Separated Values (CSV)", np.NaN,
                 "https://www.nationalarchives.gov.uk/pronom/x-fmt/18", "Droid version 6.4", False, today, 44002.01,
                 "d5e857a4bd33d2b5a2f96b78ccffe1f3", np.NaN, np.NaN, np.NaN, np.NaN],
                [fr"accession\disk2\empty.txt", "empty", np.NaN, np.NaN, "file utility version 5.03", False,
                 today,
                 0, "d41d8cd98f00b204e9800998ecf8427e", np.NaN, np.NaN, np.NaN, np.NaN],
                [fr"accession\disk2\error.html", "Extensible Markup Language", 1, np.NaN,
                 "Jhove version 1.20.1",
                 False, today, 0.035, "e080b3394eaeba6b118ed15453e49a34", np.NaN, True, True,
                 "Not able to determine type of end of line severity=info"],
                [fr"accession\disk1\file.txt", "Plain text", np.NaN,
                 "https://www.nationalarchives.gov.uk/pronom/x-fmt/111",
                 "Droid version 6.4; Jhove version 1.20.1; file utility version 5.03", False, today, 2,
                 "7b71af3fdf4a2f72a378e3e77815e497", np.NaN, True, True, np.NaN],
                [fr"accession\disk2\file.txt", "Plain text", np.NaN,
                 "https://www.nationalarchives.gov.uk/pronom/x-fmt/111",
                 "Droid version 6.4; Jhove version 1.20.1; file utility version 5.03", False, today, 2.2,
                 "e700d0871d44af1a217f0bf32320f25c", np.NaN, True, True, np.NaN],
                [fr"accession\disk2\zipping.gz", "GZIP Format", np.NaN,
                 "https://www.nationalarchives.gov.uk/pronom/x-fmt/266", "Droid version 6.4; Tika version 1.21",
                 False, today, 1.993, "XXXXXXXXXX", np.NaN, np.NaN, np.NaN, np.NaN]]
        column_names = ["File_Path", "Format_Name", "Format_Version", "PUID", "Identifying_Tool(s)", "Multiple_IDs",
                        "Date_Last_Modified", "Size_KB", "MD5", "Creating_Application", "Valid", "Well-Formed",
                        "Status_Message"]
        df_expected = pd.DataFrame(rows, columns=column_names)

        # Reads the script output into a dataframe.
        # Provides a default MD5 value for data.xlsx and zipping.gz because fixity is different every time they are made.
        df_fits = pd.read_csv("accession_fits.csv")
        replace_md5 = (df_fits["File_Path"].str.endswith("data.xlsx")) | (
            df_fits["File_Path"].str.endswith("zipping.gz"))
        df_fits.loc[replace_md5, "MD5"] = "XXXXXXXXXX"

        # Deletes the test files.
        shutil.rmtree("accession")
        shutil.rmtree("accession_FITS")
        os.remove("accession_fits.csv")

        # Compares the script output to the expected values.
        self.assertEqual(df_fits, df_expected, 'Problem with make fits csv')

    def test_encoding_error(self):
        """Tests encoding error handling when saving FITS file data to the CSV."""

        # Makes an accession folder with plain text files.
        # Variations: one with no encoding error, two with encoding errors (from pi symbol and smiley face).
        os.makedirs(fr"accession\disk1")
        with open(r"accession\disk1\file.txt", "w") as file:
            file.write("Text" * 1000)
        with open(r"accession\disk1\pi_errorπ.txt", "w") as file:
            file.write("Text" * 2500)
        with open(r"accession\disk1\smiley_error.txt", "w") as file:
            file.write("Text" * 1500)

        # Makes FITS XML for the accession to use for testing.
        # In format_analysis.py, there is also error handling for if FITS has a load class error.
        os.mkdir('accession_FITS')
        subprocess.run(f'"{c.FITS}" -r -i "accession" -o "accession_FITS"', shell=True)

        # RUNS THE FUNCTION BEING TESTED.
        make_fits_csv(fr"accession_FITS", "accession", os.getcwd(), "accession")

        # Makes a dataframe with the expected values for accession_encode_errors.txt.
        rows = [[fr"accession\disk1\pi_errorπ.txt"],
                [fr"accession\disk1\smiley_error.txt"]]
        df_encode_expected = pd.DataFrame(rows, columns=["Paths"])

        # Makes a dataframe with the expected values for accession_fits.csv.
        rows = [[fr"accession\disk1\file.txt", "Plain text", np.NaN,
                 "https://www.nationalarchives.gov.uk/pronom/x-fmt/111",
                 "Droid version 6.4; Jhove version 1.20.1; file utility version 5.03", False,
                 datetime.date.today().strftime('%Y-%m-%d'), 4.0, "1a640a2c9c60ffea3174b2f73a536c48", np.NaN, True,
                 True,
                 np.NaN]]
        column_names = ["File_Path", "Format_Name", "Format_Version", "PUID", "Identifying_Tool(s)", "Multiple_IDs",
                        "Date_Last_Modified", "Size_KB", "MD5", "Creating_Application", "Valid", "Well-Formed",
                        "Status_Message"]
        df_fits_csv_expected = pd.DataFrame(rows, columns=column_names)

        # Reads the script outputs into dataframes.
        df_encode = pd.read_csv("accession_encode_errors.txt", header=None, names=["Paths"])
        df_fits_csv = pd.read_csv("accession_fits.csv")

        # Deletes the test files.
        shutil.rmtree("accession")
        shutil.rmtree("accession_FITS")
        os.remove("accession_encode_errors.txt")
        os.remove("accession_fits.csv")

        # Compares the script outputs to the expected values.
        self.assertEqual(df_encode, df_encode_expected, 'Problem with encoding error - log')
        self.assertEqual(df_fits_csv, df_fits_csv_expected, 'Problem with encoding error - csv')


if __name__ == '__main__':
    unittest.main()
