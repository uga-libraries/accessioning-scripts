import datetime
import numpy as np
import os
import pandas as pd
import shutil
import subprocess
import unittest


# TODO - not tested, may be able to split into multiple tests (one for each iteration?)
class MyTestCase(unittest.TestCase):
    def test_iteration(self):
        """Tests that the script follows the correct logic based on the contents of the accession folder and
        that the contents are updated correctly. Runs the script 3 times to check all iterations: start from scratch,
        use existing FITS files (updating to match the accession folder), and use existing full risk data csv."""

        # Makes an accession folder with test files organized into 2 disks to use for testing.
        # All subtotals and subsets in the final report will have some information.
        # Formats included: csv, html, plain text, xlsx, zip
        # Variations: duplicate files, empty file, file with multiple identifications (xlsx),
        #             file with validation error (html), technical appraisal (empty, trash), other risk (zip)
        os.makedirs(r"accession\disk1\trash")
        with open(r"accession\disk1\trash\trash.txt", "w") as file:
            file.write("Trash Text " * 20)
        with open(r"accession\disk1\trash\trash1.txt", "w") as file:
            file.write("Trash Text " * 21)
        with open(r"accession\disk1\trash\trash2.txt", "w") as file:
            file.write("Trash Text " * 22)
        df_spreadsheet = pd.DataFrame()
        df_spreadsheet[["C1", "C2", "C2", "C3", "C4", "C5"]] = "Text" * 5000
        df_spreadsheet = pd.concat([df_spreadsheet] * 3000, ignore_index=True)
        df_spreadsheet.to_excel(r"accession\disk1\data.xlsx", index=False)
        with open(r"accession\disk1\duplicate_file.txt", "w") as file:
            file.write("Text" * 900)
        os.makedirs(r"accession\disk2")
        shutil.make_archive(r"accession\disk2\disk1backup", 'zip', r"accession\disk1")
        shutil.copyfile(r"accession\disk2\disk1backup.zip", r"accession\disk2\disk1backup2.zip")
        shutil.copyfile(r"accession\disk2\disk1backup.zip", r"accession\disk2\disk1backup3.zip")
        shutil.copyfile(r"accession\disk1\duplicate_file.txt", r"accession\disk2\duplicate_file.txt")
        open(r"accession\disk2\empty.txt", "w").close()
        with open(r"accession\disk2\error.html", "w") as file:
            file.write("<body>This isn't really html</body>")

        # ROUND ONE: Runs the script on the test accession folder and tests if the expected messages were produced.
        # In format_analysis.py, these messages are printed to the terminal for archivist review.
        iteration_one = subprocess.run("python format_analysis.py accession", shell=True, stdout=subprocess.PIPE)
        msg = "\r\nGenerating new FITS format identification information.\r\n\r\n" \
              "Generating new risk data for the analysis report.\r\n"
        self.assertEqual(iteration_one.stdout.decode("utf-8"), msg, 'Problem with Iteration_Message_1')

        # ROUND TWO: Deletes the trash folder and adds a file to the accession folder to simulate archivist appraisal.
        # Also deletes the full_risk_data.csv so an updated one will be made with the changes.
        shutil.rmtree(r"accession\disk1\trash")
        with open(r"accession\disk2\new.txt", "w") as file:
            file.write("Text" * 300)
        os.remove("accession_full_risk_data.csv")

        # Runs the script again on the test accession folder.
        # It will update the FITS files to match the accession folder and update the three spreadsheet.
        iteration_two = subprocess.run("python format_analysis.py accession", shell=True, stdout=subprocess.PIPE)
        msg = "\r\nUpdating the XML files in the FITS folder to match the files in the accession folder.\r\n" \
              "This will update fits.csv but will NOT update full_risk_data.csv from a previous script iteration.\r\n" \
              "Delete full_risk_data.csv before the script gets to that step for it to be remade with the new information.\r\n\r\n" \
              "Generating new risk data for the analysis report.\r\n"
        self.assertEqual(iteration_two.stdout.decode("utf-8"), msg, 'Problem with Iteration_Message_2')
        
        # ROUND THREE: Edits the full_risk_data.csv to simulate archivist cleaning up risk matches.
        # Removes the data_update.final.xlsx FITS id of Zip Format and NARA matches to empty.txt except for Plain Text.
        df_risk = pd.read_csv("accession_full_risk_data.csv")
        xlsx_to_drop = df_risk[(df_risk["FITS_File_Path"] == fr"accession\disk1\data.xlsx") &
                               (df_risk["FITS_Format_Name"] == "ZIP Format")]
        empty_to_drop = df_risk[(df_risk["FITS_File_Path"] == fr"accession\disk2\empty.txt") &
                                (df_risk["NARA_Format Name"] != "Plain Text")]
        df_risk.drop(xlsx_to_drop.index, inplace=True)
        df_risk.drop(empty_to_drop.index, inplace=True)
        df_risk.to_csv("accession_full_risk_data.csv", index=False)

        # Runs the script again on the test accession folder.
        # It will use existing fits.csv and full_risk_data.csv to update format_analysis.xlsx.
        iteration_three = subprocess.run("python format_analysis.py accession", shell=True, stdout=subprocess.PIPE)
        msg = "\r\nUpdating the XML files in the FITS folder to match the files in the accession folder.\r\n" \
              "This will update fits.csv but will NOT update full_risk_data.csv from a previous script iteration.\r\n" \
              "Delete full_risk_data.csv before the script gets to that step for it to be remade with the new information.\r\n\r\n" \
              "Updating the analysis report using existing risk data.\r\n"
        self.assertEqual(iteration_three.stdout.decode("utf-8"), msg, 'Problem with Iteration_Message_3')

        # The next several code blocks makes dataframes with the expected values for each tab in format_analysis.xlsx.

        # Expected values for things that change (date and size and MD5 for XLSX and ZIP) are calculated
        # instead of using a constant for comparison. Ones used frequently are saved to variables.
        today = datetime.date.today().strftime('%Y-%m-%d')
        xlsx_kb = round(os.path.getsize(r"accession\disk1\data.xlsx") / 1000, 3)
        xlsx_mb = round(xlsx_kb / 1000, 3)
        zip_kb = round(os.path.getsize(r"accession\disk2\disk1backup.zip") / 1000, 3)
        three_zip_mb = round((os.path.getsize(r"accession\disk2\disk1backup.zip") / 1000 * 3) / 1000, 3)
        total_mb = df_risk["FITS_Size_KB"].sum() / 1000

        # Expected values for the format subtotal.
        rows = [["empty", "Low Risk", 1, 10, 0, 0],
                ["Extensible Markup Language", "Low Risk", 1, 10, 0, 0],
                ["Office Open XML Workbook", "Low Risk", 1, 10, xlsx_mb, round((xlsx_mb / total_mb) * 100, 3)],
                ["Plain text", "Low Risk", 3, 30, 0.008, round((0.008 / total_mb) * 100, 3)],
                ["XLSX", "Low Risk", 1, 10, xlsx_mb, round((xlsx_mb / total_mb) * 100, 3)],
                ["ZIP Format", "Moderate Risk", 3, 30, three_zip_mb, round((three_zip_mb / total_mb) * 100, 3)]]
        column_names = ["FITS_Format_Name", "NARA_Risk Level", "File Count", "File %", "Size (MB)", "Size %"]
        df_format_subtotal_expected = pd.DataFrame(rows, columns=column_names)

        # Expected values for the NARA risk subtotal.
        low_mb = round(df_risk[df_risk["NARA_Risk Level"] == "Low Risk"]["FITS_Size_KB"].sum() / 1000, 3)
        rows = [["Low Risk", 7, 70, low_mb, round((low_mb / total_mb) * 100, 3)],
                ["Moderate Risk", 3, 30, three_zip_mb, round((three_zip_mb / total_mb) * 100, 3)]]
        column_names = ["NARA_Risk Level", "File Count", "File %", "Size (MB)", "Size %"]
        df_nara_risk_subtotal_expected = pd.DataFrame(rows, columns=column_names)

        # Expected values for the tech appraisal subtotal.
        rows = [["Format", "empty", 1, 10, 0, 0]]
        column_names = ["Technical_Appraisal", "FITS_Format_Name", "File Count", "File %", "Size (MB)", "Size %"]
        df_tech_appraisal_subtotal_expected = pd.DataFrame(rows, columns=column_names)

        # Expected values for the other risk subtotal.
        rows = [["Archive format", "ZIP Format", 3, 30, three_zip_mb, round((three_zip_mb / total_mb) * 100, 3)]]
        column_names = ["Other_Risk", "FITS_Format_Name", "File Count", "File %", "Size (MB)", "Size %"]
        df_other_risk_subtotal_expected = pd.DataFrame(rows, columns=column_names)

        # Expected values for the media subtotal.
        disk1_mb = round(df_risk[df_risk["FITS_File_Path"].str.contains(r"\\disk1\\")]["FITS_Size_KB"].sum() / 1000, 3)
        disk2_mb = round(df_risk[df_risk["FITS_File_Path"].str.contains(r"\\disk2\\")]["FITS_Size_KB"].sum() / 1000, 3)
        rows = [["disk1", 3, disk1_mb, 0, 0, 3, 0, 0, 0], ["disk2", 7, disk2_mb, 0, 3, 4, 0, 1, 3]]
        column_names = ["Media", "File Count", "Size (MB)", "NARA High Risk (File Count)",
                        "NARA Moderate Risk (File Count)", "NARA Low Risk (File Count)", "No NARA Match (File Count)",
                        "Technical Appraisal_Format (File Count)", "Other Risk Indicator (File Count)"]
        df_media_subtotal_expected = pd.DataFrame(rows, columns=column_names)

        # Expected values for the NARA risk subset.
        rows = [[r"\accession\disk2\disk1backup.zip", "ZIP Format", 2, False, today, zip_kb, "XXXXXXXXXX",
                 "Moderate Risk", "Retain but extract files from the container", "PRONOM", "Not for TA",
                 "Archive format"],
                [r"\accession\disk2\disk1backup2.zip", "ZIP Format", 2, False, today, zip_kb, "XXXXXXXXXX",
                 "Moderate Risk", "Retain but extract files from the container", "PRONOM", "Not for TA",
                 "Archive format"],
                [r"\accession\disk2\disk1backup3.zip", "ZIP Format", 2, False, today, zip_kb, "XXXXXXXXXX",
                 "Moderate Risk", "Retain but extract files from the container", "PRONOM", "Not for TA",
                 "Archive format"]]
        column_names = ["FITS_File_Path", "FITS_Format_Name", "FITS_Format_Version", "FITS_Multiple_IDs",
                        "FITS_Date_Last_Modified", "FITS_Size_KB", "FITS_MD5", "NARA_Risk Level",
                        "NARA_Proposed Preservation Plan", "NARA_Match_Type", "Technical_Appraisal", "Other_Risk"]
        df_nara_risk_expected = pd.DataFrame(rows, columns=column_names)

        # Expected values for the tech appraisal subset.
        rows = [[r"\accession\disk2\empty.txt", "empty", np.NaN, "file utility version 5.03",
                 False, 0, np.NaN, "Low Risk", "Retain", "File Extension", "Format", "Not for Other"]]
        column_names = ["FITS_File_Path", "FITS_Format_Name", "FITS_Format_Version", "FITS_Identifying_Tool(s)",
                        "FITS_Multiple_IDs", "FITS_Size_KB", "FITS_Creating_Application", "NARA_Risk Level",
                        "NARA_Proposed Preservation Plan", "NARA_Match_Type", "Technical_Appraisal", "Other_Risk"]
        df_tech_appraisal_expected = pd.DataFrame(rows, columns=column_names)

        # Expected values for the other risk subset.
        rows = [[r"\accession\disk2\disk1backup.zip", "ZIP Format", 2,
                 "Droid version 6.4; file utility version 5.03; Exiftool version 11.54; ffident version 0.2; Tika version 1.21",
                 False, zip_kb, "Moderate Risk", "Retain but extract files from the container", "PRONOM", "Not for TA",
                 "Archive format"],
                [r"\accession\disk2\disk1backup2.zip", "ZIP Format", 2,
                 "Droid version 6.4; file utility version 5.03; Exiftool version 11.54; ffident version 0.2; Tika version 1.21",
                 False, zip_kb, "Moderate Risk", "Retain but extract files from the container", "PRONOM", "Not for TA",
                 "Archive format"],
                [r"\accession\disk2\disk1backup3.zip", "ZIP Format", 2,
                 "Droid version 6.4; file utility version 5.03; Exiftool version 11.54; ffident version 0.2; Tika version 1.21",
                 False, zip_kb, "Moderate Risk", "Retain but extract files from the container", "PRONOM", "Not for TA",
                 "Archive format"]]
        column_names = ["FITS_File_Path", "FITS_Format_Name", "FITS_Format_Version", "FITS_Identifying_Tool(s)",
                        "FITS_Multiple_IDs", "FITS_Size_KB", "NARA_Risk Level", "NARA_Proposed Preservation Plan",
                        "NARA_Match_Type", "Technical_Appraisal", "Other_Risk"]
        df_other_risk_expected = pd.DataFrame(rows, columns=column_names)

        # Expected values for the multiple format identifications subset.
        rows = [[r"\accession\disk1\data.xlsx", "XLSX", np.NaN, np.NaN, "Exiftool version 11.54", True, today,
                 xlsx_kb, "XXXXXXXXXX", "Microsoft Excel", "Low Risk", "Retain", "File Extension", "Not for TA",
                 "Not for Other"],
                [r"\accession\disk1\data.xlsx", "Office Open XML Workbook", np.NaN, np.NaN,
                 "Tika version 1.21",
                 True, today, xlsx_kb, "XXXXXXXXXX", "Microsoft Excel", "Low Risk", "Retain", "File Extension",
                 "Not for TA", "Not for Other"]]
        column_names = ["FITS_File_Path", "FITS_Format_Name", "FITS_Format_Version", "FITS_PUID",
                        "FITS_Identifying_Tool(s)", "FITS_Multiple_IDs", "FITS_Date_Last_Modified", "FITS_Size_KB",
                        "FITS_MD5", "FITS_Creating_Application", "NARA_Risk Level", "NARA_Proposed Preservation Plan",
                        "NARA_Match_Type", "Technical_Appraisal", "Other_Risk"]
        df_multiple_ids_expected = pd.DataFrame(rows, columns=column_names)

        # Expected values for the duplicates subset.
        rows = [[r"\accession\disk2\disk1backup.zip", zip_kb, "XXXXXXXXXX"],
                [r"\accession\disk2\disk1backup2.zip", zip_kb, "XXXXXXXXXX"],
                [r"\accession\disk2\disk1backup3.zip", zip_kb, "XXXXXXXXXX"],
                [r"\accession\disk2\duplicate_file.txt", 3.6, "c0090e0840270f422e0c357b719e8857"],
                [r"\accession\disk1\duplicate_file.txt", 3.6, "c0090e0840270f422e0c357b719e8857"]]
        column_names = ["FITS_File_Path", "FITS_Size_KB", "FITS_MD5"]
        df_duplicates_expected = pd.DataFrame(rows, columns=column_names)

        # Expected values for the validation subset.
        rows = [[r"\accession\disk2\error.html", "Extensible Markup Language", 1, np.NaN, "Jhove version 1.20.1",
             False, today, 0.035, "e080b3394eaeba6b118ed15453e49a34", np.NaN, True, True,
             "Not able to determine type of end of line severity=info",
             "Low Risk", "Retain", "Format Name", "Not for TA", "Not for Other"]]
        column_names = ["FITS_File_Path", "FITS_Format_Name", "FITS_Format_Version", "FITS_PUID",
                        "FITS_Identifying_Tool(s)", "FITS_Multiple_IDs", "FITS_Date_Last_Modified", "FITS_Size_KB",
                        "FITS_MD5", "FITS_Creating_Application", "FITS_Valid", "FITS_Well-Formed",
                        "FITS_Status_Message",
                        "NARA_Risk Level", "NARA_Proposed Preservation Plan", "NARA_Match_Type", "Technical_Appraisal",
                        "Other_Risk"]
        df_validation_expected = pd.DataFrame(rows, columns=column_names)

        # Makes a dataframe with the values from each tab in format_analysis.xlsx made by the script.
        # Provides a default MD5 for XLSX or ZIP files, since those have a different MD5 each time they are made.
        # If the df is all XLSX or ZIP, the column is filled with the default. Otherwise, it is filtered by format first.
        xlsx = pd.ExcelFile("accession_format-analysis.xlsx")
        df_format_subtotal = pd.read_excel(xlsx, "Format Subtotal")
        df_nara_risk_subtotal = pd.read_excel(xlsx, "NARA Risk Subtotal")
        df_tech_appraisal_subtotal = pd.read_excel(xlsx, "Tech Appraisal Subtotal")
        df_other_risk_subtotal = pd.read_excel(xlsx, "Other Risk Subtotal")
        df_media_subtotal = pd.read_excel(xlsx, "Media Subtotal")
        df_nara_risk = pd.read_excel(xlsx, "NARA Risk")
        df_nara_risk["FITS_MD5"] = "XXXXXXXXXX"
        df_tech_appraisal = pd.read_excel(xlsx, "For Technical Appraisal")
        df_other_risk = pd.read_excel(xlsx, "Other Risks")
        df_multiple_ids = pd.read_excel(xlsx, "Multiple Formats")
        df_multiple_ids["FITS_MD5"] = "XXXXXXXXXX"
        df_duplicates = pd.read_excel(xlsx, "Duplicates")
        replace_md5 = df_duplicates["FITS_File_Path"].str.endswith("zip")
        df_duplicates.loc[replace_md5, "FITS_MD5"] = "XXXXXXXXXX"
        df_validation = pd.read_excel(xlsx, "Validation")
        xlsx.close()

        # Compares the expected values to the actual script values.
        self.assertEqual(df_format_subtotal, df_format_subtotal_expected, "Problem with Iteration_Subtotal_Format")
        self.assertEqual(df_tech_appraisal_subtotal, df_tech_appraisal_subtotal_expected, "Problem with Iteration_Subtotal_Tech_Appraisal")
        self.assertEqual(df_nara_risk_subtotal, df_nara_risk_subtotal_expected, "Problem with Iteration_Subtotal_NARA_Risk")
        self.assertEqual(df_other_risk_subtotal, df_other_risk_subtotal_expected, "Problem with Iteration_Subtotal_Other_Risk")
        self.assertEqual(df_media_subtotal, df_media_subtotal_expected, "Problem with Iteration_Subtotal_Media")
        self.assertEqual(df_nara_risk, df_nara_risk_expected, "Problem with Iteration_Subset_NARA_Risk")
        self.assertEqual(df_tech_appraisal, df_tech_appraisal_expected, "Problem with Iteration_Subset_Tech_Appraisal")
        self.assertEqual(df_other_risk, df_other_risk_expected, "Problem with Iteration_Subset_Other_Risk")
        self.assertEqual(df_multiple_ids, df_multiple_ids_expected, "Problem with Iteration_Subset_Multiple_IDs")
        self.assertEqual(df_duplicates, df_duplicates_expected, "Problem with Iteration_Subset_Duplicates")
        self.assertEqual(df_validation, df_validation_expected, "Problem with Iteration_Subset_Validation")

        # Deletes the test files.
        shutil.rmtree("accession")
        shutil.rmtree("accession_FITS")
        os.remove("accession_fits.csv")
        os.remove("accession_format-analysis.xlsx")
        os.remove("accession_full_risk_data.csv")


if __name__ == '__main__':
    unittest.main()
