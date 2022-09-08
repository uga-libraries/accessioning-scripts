"""Purpose: tests for each function and analysis component (each subset and subtotal) in the format_analysis.py script.
Each test creates simplified input, runs the code, and compares it to the expected output.
Test results are saved to a directory specified with the script argument.
Comment out any test you do not wish to run.

For any tests that do not import the function from format_analysis.py, sync the code before running the test.
If the input for any function or analysis changes, edit the test input and expected results."""

# usage: python path/format_analysis_tests.py output_folder
import io
import os.path
import shutil

from format_analysis_functions import *


def compare_strings(test_name, actual, expected):
    """Compares two strings, one with the actual script output and one with the expected values.
    Prints if they match (test passes) or not (test fails) and updates the counter.
    Results for failed tests are saved to a text file in the output folder for review."""

    if actual == expected:
        print("Pass: ", test_name)
        global PASSED_TESTS
        PASSED_TESTS += 1
    else:
        print("FAIL: ", test_name)
        global FAILED_TESTS
        FAILED_TESTS += 1

        with open(f"{test_name}_comparison_results.txt", "w") as file:
            file.write("Test output:\n")
            file.write(actual)
            file.write("\n\nExpected output:\n")
            file.write(expected)


def compare_dataframes(test_name, df_actual, df_expected):
    """Compares two dataframes, one with the actual script output and one with the expected values.
    Prints if they match (test passes) or not (test fails) and updates the counter.
    Results for failed tests are saved to a CSV in the output folder for review."""

    # Makes a new dataframe that merges the values of the two dataframes.
    df_comparison = df_actual.merge(df_expected, indicator=True, how="outer")

    # Makes a dataframe with just the errors (merge value isn't both).
    df_errors = df_comparison[df_comparison["_merge"] != "both"]

    # If the merged dataframe is empty (everything matched), prints that the test passes.
    # Otherwise, saves the dataframe with the complete merge (including matches) to a CSV in the output directory.
    if len(df_errors) == 0:
        print("Pass: ", test_name)
        global PASSED_TESTS
        PASSED_TESTS += 1
    else:
        print("FAIL: ", test_name)
        global FAILED_TESTS
        FAILED_TESTS += 1
        df_comparison.to_csv(f"{test_name}_comparison_results.csv", index=False)


def test_argument(repo_path):
    """Tests error handling for a missing or incorrect script argument."""

    # Calculates the path to the format_analysis.py script.
    script_path = os.path.join(repo_path, "format_analysis.py")

    # Runs the script without an argument and verifies the correct error message would print.
    no_argument = subprocess.run(f"python {script_path}", shell=True, stdout=subprocess.PIPE)
    error_msg = "\r\nThe required script argument (accession_folder) is missing.\r\nPlease run the script again." \
                "\r\nScript usage: python path/format_analysis.py path/accession_folder\r\n"
    compare_strings("Argument_Missing", no_argument.stdout.decode("utf-8"), error_msg)

    # Runs the script with an argument that isn't a valid path and verifies the correct error message would print.
    wrong_argument = subprocess.run(f"python {script_path} C:/User/Wrong/Path", shell=True, stdout=subprocess.PIPE)
    error_msg = "\r\nThe provided accession folder 'C:/User/Wrong/Path' is not a valid directory." \
                "\r\nPlease run the script again." \
                "\r\nScript usage: python path/format_analysis.py path/accession_folder\r\n"
    compare_strings("Argument_Invalid_Path", wrong_argument.stdout.decode("utf-8"), error_msg)


def test_check_configuration_function(repo_path):
    """Tests error handling from missing configuration file, missing variables and variables with invalid paths."""

    # Renames the current configuration file so errors can be generated without losing the correct file.
    os.rename(f"{repo_path}/configuration.py", f"{repo_path}/configuration_original.py")

    # Runs the script with no configuration.py present, since it was just renamed.
    no_config = subprocess.run(f"python {repo_path}/format_analysis.py {os.getcwd()}", shell=True, stdout=subprocess.PIPE)
    error_msg = "\r\nCould not run the script. Missing the required configuration.py file." \
                "\r\nMake a configuration.py file using configuration_template.py and save it to the folder with the script.\r\n"
    compare_strings("Config_Missing", no_config.stdout.decode("utf-8"), error_msg)

    # Makes a configuration file without any of the required variables to use for testing.
    # Verifies that the check_configuration() function returns the expected error messages.
    # Deletes the file after the test is complete.
    with open(f"{repo_path}/configuration.py", "w") as config:
        config.write('# Constants used for other scripts\nvariable = "value"\n')
    no_var = subprocess.run(f"python {repo_path}/format_analysis.py {os.getcwd()}", shell=True, stdout=subprocess.PIPE)
    error_msg = '\r\nProblems detected with configuration.py:\r\n' \
                '   * FITS variable is missing from the configuration file.\r\n' \
                '   * ITA variable is missing from the configuration file.\r\n' \
                '   * RISK variable is missing from the configuration file.\r\n' \
                '   * NARA variable is missing from the configuration file.\r\n\r\n' \
                'Correct the configuration file and run the script again. Use configuration_template.py as a model.\r\n'
    compare_strings("Config_Missing_Variables", no_var.stdout.decode("utf-8"), error_msg)
    os.remove(f"{repo_path}/configuration.py")

    # Makes a configuration file with the required variables but all are incorrect file paths to use for testing.
    # Verifies that the check_configuration() function returns the expected error messages.
    # Deletes the file after the test is complete.
    with open(f"{repo_path}/configuration.py", "w") as config:
        config.write('# Constants used for other scripts\n')
        config.write('FITS = "C:/Users/Error/fits.bat"\n')
        config.write('ITA = "C:/Users/Error/ITAfileformats.csv"\n')
        config.write('RISK = "C:/Users/Error/Riskfileformats.csv"\n')
        config.write('NARA = "C:/Users/Error/NARA.csv"\n')
    path_err = subprocess.run(f"python {repo_path}/format_analysis.py {os.getcwd()}", shell=True, stdout=subprocess.PIPE)
    error_msg = "\r\nProblems detected with configuration.py:\r\n" \
                "   * FITS path 'C:/Users/Error/fits.bat' is not correct.\r\n" \
                "   * ITAfileformats.csv path 'C:/Users/Error/ITAfileformats.csv' is not correct.\r\n" \
                "   * Riskfileformats.csv path 'C:/Users/Error/Riskfileformats.csv' is not correct.\r\n" \
                "   * NARA Preservation Action Plans CSV path 'C:/Users/Error/NARA.csv' is not correct.\r\n\r\n" \
                "Correct the configuration file and run the script again. Use configuration_template.py as a model.\r\n"
    compare_strings("Config_Variable_Paths", path_err.stdout.decode("utf-8"), error_msg)
    os.remove(f"{repo_path}/configuration.py")

    # Renames the correct configuration file back to configuration.py.
    os.rename(f"{repo_path}/configuration_original.py", f"{repo_path}/configuration.py")


def test_csv_to_dataframe_function():
    """Tests reading all four CSVs into dataframes and adding prefixes to FITS and NARA dataframes."""

    # Makes a FITS CSV with no special characters.
    # In format_analysis.py, this would be made earlier in the script and has more columns.
    # The other CSVs read by this function are already on the local machine and paths are in configuration.py
    with open("accession_fits.csv", "w", newline="") as file:
        file_write = csv.writer(file)
        file_write.writerow(["File_Path", "Format_Name", "Format_Version", "Multiple_IDs"])
        file_write.writerow([r"C:\Coll\accession\CD001_Images\IMG1.JPG", "JPEG EXIF", "1.01", False])
        file_write.writerow([r"C:\Coll\accession\CD002_Website\index.html", "Hypertext Markup Language", "4.01", True])
        file_write.writerow([r"C:\Coll\accession\CD002_Website\index.html", "HTML Transitional", "HTML 4.01", True])

    # Runs the function on all four CSVs.
    df_fits = csv_to_dataframe("accession_fits.csv")
    df_ita = csv_to_dataframe(c.ITA)
    df_other = csv_to_dataframe(c.RISK)
    df_nara = csv_to_dataframe(c.NARA)

    # For each CSV, tests the function worked by verifying the column names and that the dataframe isn't empty.
    # Column names are converted to a comma separated string to work with the compare_strings() function.
    global FAILED_TESTS
    if len(df_fits) != 0:
        expected = "FITS_File_Path, FITS_Format_Name, FITS_Format_Version, FITS_Multiple_IDs"
        compare_strings("FITS_CSV_DF", ', '.join(df_fits.columns.to_list()), expected)
    else:
        print("FAIL: FITS_CSV_DF is empty")
        FAILED_TESTS += 1

    if len(df_ita) != 0:
        compare_strings("ITA_CSV_DF", ', '.join(df_ita.columns.to_list()), "FITS_FORMAT, NOTES")
    else:
        print("FAIL: ITA_CSV_DF is empty")
        FAILED_TESTS += 1

    if len(df_other) != 0:
        compare_strings("Other_CSV_DF", ', '.join(df_other.columns.to_list()), "FITS_FORMAT, RISK_CRITERIA")
    else:
        print("FAIL: Other_CSV_DF is empty")
        FAILED_TESTS += 1

    if len(df_nara) != 0:
        expected = "NARA_Format Name, NARA_File Extension(s), NARA_Category/Plan(s), NARA_NARA Format ID, " \
                   "NARA_MIME type(s), NARA_Specification/Standard URL, NARA_PRONOM URL, NARA_LOC URL, " \
                   "NARA_British Library URL, NARA_WikiData URL, NARA_ArchiveTeam URL, NARA_ForensicsWiki URL, " \
                   "NARA_Wikipedia URL, NARA_docs.fileformat.com, NARA_Other URL, NARA_Notes, NARA_Risk Level, " \
                   "NARA_Preservation Action, NARA_Proposed Preservation Plan, NARA_Description and Justification, " \
                   "NARA_Preferred Processing and Transformation Tool(s)"
        compare_strings("NARA_CSV_DF", ', '.join(df_nara.columns.to_list()), expected)
    else:
        print("FAIL: NARA_CSV_DF is empty")
        FAILED_TESTS += 1


def test_csv_to_dataframe_function_errors():
    """Tests unicode error handling."""

    # Makes a FITS CSV with special characters.
    # In format_analysis.py, this would be made earlier in the script and has more columns.
    with open("accession_fits.csv", "w", newline="") as file:
        file_write = csv.writer(file)
        file_write.writerow(["File_Path", "Format_Name", "Format_Version", "Multiple_IDs"])
        file_write.writerow([r"C:\Coll\accession\CD001_Images\©Image.JPG", "JPEG EXIF", "1.01", False])
        file_write.writerow([r"C:\Coll\accession\CD002_Website\indexé.html", "Hypertext Markup Language", "4.01", True])
        file_write.writerow([r"C:\Coll\accession\CD002_Website\indexé.html", "HTML Transitional", "HTML 4.01", True])

    # Runs the function but prevents it from printing a status message to the terminal.
    # In format_analysis.py, it prints a warning for the archivist that the CSV had encoding errors.
    text_trap = io.StringIO()
    sys.stdout = text_trap
    df_fits = csv_to_dataframe("accession_fits.csv")
    sys.stdout = sys.__stdout__

    # Makes a dataframe with the expected values in df_fits after the CSV is read with encoding_errors="ignore".
    # This causes characters to be skipped if they can't be read.
    rows = [[r"C:\Coll\accession\CD001_Images\Image.JPG", "JPEG EXIF", "1.01", False],
            [r"C:\Coll\accession\CD002_Website\index.html", "Hypertext Markup Language", "4.01", True],
            [r"C:\Coll\accession\CD002_Website\index.html", "HTML Transitional", "HTML 4.01", True]]
    column_names = ["FITS_File_Path", "FITS_Format_Name", "FITS_Format_Version", "FITS_Multiple_IDs"]
    df_expected = pd.DataFrame(rows, columns=column_names)

    # Compares the contents of the FITS folder to the expected values.
    compare_dataframes("CSV_DF_Encoding", df_fits, df_expected)

    # Deletes the test file.
    os.remove("accession_fits.csv")


def test_make_fits():
    """Tests the command for making FITS files the first time."""

    # Makes an accession folder with test files to use for testing.
    accession_folder = fr"{output}\accession"
    os.makedirs(fr"{accession_folder}\folder")
    for file_path in ("file.txt", r"folder\file.txt", r"folder\other.txt"):
        with open(fr"accession\{file_path}", "w") as file:
            file.write("Text")

    # Makes the directory for FITS files.
    # In format_analysis.py, this is done in the main body of the script after testing that the folder doesn't exist.
    fits_output = f"{output}/accession_FITS"
    os.mkdir(fits_output)

    # Calls FITS with the correct location.
    # In format_analysis.py, this is done in the main body of the script and also exits the script if there is an error.
    fits_status = subprocess.run(f'"{c.FITS}" -r -i "{accession_folder}" -o "{fits_output}"',
                                 shell=True, stderr=subprocess.PIPE)
    if fits_status.stderr == b'Error: Could not find or load main class edu.harvard.hul.ois.fits.Fits\r\n':
        print("Unable to generate FITS XML for this accession because FITS is in a different directory from the accession.")
        print("Copy the FITS folder to the same letter directory as the accession files and run the script again.")

    # Makes a dataframe with the files that should be in the accession_fits folder based on the input.
    df_expected = pd.DataFrame(["file.txt.fits.xml", "file.txt-1.fits.xml", "other.txt.fits.xml"], columns=["Files"])

    # Makes a dataframe with the files that are actually in the accession_fits folder after running the test.
    fits_files = []
    for root, dirs, files in os.walk("accession_fits"):
        fits_files.extend(files)
    df_fits_files = pd.DataFrame(fits_files, columns=["Files"])

    # Compares the contents of the FITS folder to the expected values.
    compare_dataframes("Make_FITS", df_fits_files, df_expected)

    # Deletes the test files.
    shutil.rmtree(fr"{output}\accession")
    shutil.rmtree(fr"{output}\accession_FITS")


def test_fits_class_error():
    """Tests the error handling for FITS when it is in a different directory than the source files.
    For this test to work, the fits.bat file must be in the specified location."""

    # Makes an accession folder with a test file to use for testing.
    accession_folder = fr"{output}\accession"
    os.mkdir(accession_folder)
    with open(fr"accession\file.txt", "w") as file:
        file.write("Text")

    # Makes the directory for FITS files.
    # In format_analysis.py, this is done in the main body of the script after testing that the folder doesn't exist.
    fits_output = f"{output}/accession_FITS"
    os.mkdir(fits_output)

    # Makes a variable with a FITS file path in a different directory from the accession folder.
    # In format_analysis.py, the FITS file path is in the configuration.py file.
    fits_path = r"X:\test\fits.bat"

    # Calls FITS which is located in a different directory to generate an error.
    fits_result = subprocess.run(f'"{fits_path}" -r -i "{accession_folder}" -o "{fits_output}"',
                                 shell=True, stderr=subprocess.PIPE)

    # Verifies the correct error message would be printed by the script and prints the test result.
    # In format_analysis.py, the error would also cause the script to exit.
    error_msg = "Error: Could not find or load main class edu.harvard.hul.ois.fits.Fits\r\n"
    compare_strings("FITS_Class_Error", fits_result.stderr.decode("utf-8"), error_msg)

    # Deletes the test files.
    shutil.rmtree(fr"{output}\accession")
    shutil.rmtree(fr"{output}\accession_FITS")


def test_update_fits_function():
    """Tests removing FITS for deleted files and adding FITs for new files."""

    # Makes an accession folder with test files to use for testing.
    accession_folder = fr"{output}\accession"
    os.makedirs(fr"{accession_folder}\folder")
    paths = ["file.txt", "delete_one.txt", r"folder\delete_one.txt", r"folder\delete_too.txt",
             r"folder\file.txt", r"folder\spare.txt"]
    for file_path in paths:
        with open(fr"accession\{file_path}", "w") as file:
            file.write("Text")

    # Makes FITS XML for those files to use for testing.
    # In format_analysis.py, this is done in the main body of the script.
    fits_output = fr"{output}\accession_FITS"
    os.mkdir(fits_output)
    subprocess.run(f'"{c.FITS}" -r -i "{accession_folder}" -o "{fits_output}"', shell=True)

    # Deletes 2 files and adds 1 file to the accession folder.
    os.remove(r"accession\delete_one.txt")
    os.remove(r"accession\folder\delete_too.txt")
    with open(r"accession\new_file.txt", "w") as file:
        file.write("Text")

    # Runs the function to update FITs files.
    update_fits(accession_folder, fits_output, output, "accession")

    # Makes a dataframe with the files which should be in the FITs folder.
    expected = ["delete_one.txt-1.fits.xml", "file.txt.fits.xml", "file.txt-1.fits.xml", "new_file.txt.fits.xml",
                "spare.txt.fits.xml"]
    df_expected = pd.DataFrame(expected, columns=["Files"])

    # Makes a dataframe with the files that are in the FITS folder.
    fits_files = []
    for root, dirs, files in os.walk("accession_fits"):
        fits_files.extend(files)
    df_fits_files = pd.DataFrame(fits_files, columns=["Files"])

    # Compares the contents of the FITS folder to the expected values.
    compare_dataframes("Update_FITS", df_fits_files, df_expected)

    # Deletes the test files.
    shutil.rmtree("accession")
    shutil.rmtree("accession_FITS")


def test_make_fits_csv():
    """Tests all variations for FITS data extraction and reformatting."""

    # Makes an accession folder with test files organized into 2 disks to use for testing.
    # Formats included: csv, html, plain text, xlsx
    # Variations: one and multiple format ids, with and without optional fields, one or multiple tools
    accession_folder = fr"{output}\accession"
    os.makedirs(fr"{accession_folder}\disk1")
    df_spreadsheet = pd.DataFrame({"C1": ["text"*1000], "C2": ["text"*1000], "C3": ["text"*1000]})
    df_spreadsheet = pd.concat([df_spreadsheet]*100, ignore_index=True)
    df_spreadsheet.to_csv(r"accession\disk1\data.csv", index=False)
    df_spreadsheet.to_excel(r"accession\disk1\data.xlsx", index=False)
    df_spreadsheet["C3"] = "New Text"
    df_spreadsheet.to_csv(r"accession\disk1\data_update.csv", index=False)
    with open(r"accession\disk1\file.txt", "w") as file:
        file.write("Text" * 50)
    os.makedirs(fr"{accession_folder}\disk2")
    with open(r"accession\disk2\file.txt", "w") as file:
        file.write("Text" * 55)
    with open(r"accession\disk2\error.html", "w") as file:
        file.write("<body>This isn't really html</body>")

    # Makes FITS files using the test accession folder.
    # In format_analysis.py, there is also error handling for if FITS has a load class error.
    fits_output = f"{output}/accession_FITS"
    os.mkdir(fits_output)
    subprocess.run(f'"{c.FITS}" -r -i "{accession_folder}" -o "{fits_output}"', shell=True)

    # Runs the function being tested.
    make_fits_csv(fr"{output}\accession_FITS", accession_folder, output, "accession")

    # Makes a dataframe with the expected values.
    # Does not include fixity because that changes every time XLSX is made.
    # Calculates size for XLSX because the size varies every time it is made.
    today = datetime.date.today().strftime('%Y-%m-%d')
    rows = [[fr"{output}\accession\disk1\data.csv", "Comma-Separated Values (CSV)", np.NaN, "https://www.nationalarchives.gov.uk/pronom/x-fmt/18",
             "Droid version 6.4", False, today, 1200.41, np.NaN, np.NaN, np.NaN, np.NaN],
            [fr"{output}\accession\disk1\data.xlsx", "ZIP Format", 2, "https://www.nationalarchives.gov.uk/pronom/x-fmt/263",
             "Droid version 6.4; file utility version 5.03; ffident version 0.2", True, today,
             round(os.path.getsize(fr"{output}\accession\disk1\data.xlsx")/1000, 3), "Microsoft Excel", np.NaN, np.NaN, np.NaN],
            [fr"{output}\accession\disk1\data.xlsx", "XLSX", np.NaN, np.NaN, "Exiftool version 11.54", True, today,
             round(os.path.getsize(fr"{output}\accession\disk1\data.xlsx")/1000, 3), "Microsoft Excel", np.NaN, np.NaN, np.NaN],
            [fr"{output}\accession\disk1\data.xlsx", "Office Open XML Workbook", np.NaN, np.NaN, "Tika version 1.21",
             True, today, round(os.path.getsize(fr"{output}\accession\disk1\data.xlsx")/1000, 3), "Microsoft Excel", np.NaN, np.NaN, np.NaN],
            [fr"{output}\accession\disk1\data_update.csv", "Comma-Separated Values (CSV)", np.NaN, "https://www.nationalarchives.gov.uk/pronom/x-fmt/18",
             "Droid version 6.4", False, today, 801.21, np.NaN, np.NaN, np.NaN, np.NaN],
            [fr"{output}\accession\disk1\file.txt", "Plain text", np.NaN, "https://www.nationalarchives.gov.uk/pronom/x-fmt/111",
             "Droid version 6.4; Jhove version 1.20.1; file utility version 5.03", False, today, 0.2, np.NaN, True, True, np.NaN],
            [fr"{output}\accession\disk2\file.txt", "Plain text", np.NaN, "https://www.nationalarchives.gov.uk/pronom/x-fmt/111",
             "Droid version 6.4; Jhove version 1.20.1; file utility version 5.03", False, today, 0.22, np.NaN, True, True, np.NaN],
            [fr"{output}\accession\disk2\error.html", "Extensible Markup Language", 1, np.NaN, "Jhove version 1.20.1",
             False, today, 0.035, np.NaN, True, True, "Not able to determine type of end of line severity=info"]]
    column_names = ["File_Path", "Format_Name", "Format_Version", "PUID", "Identifying_Tool(s)", "Multiple_IDs",
                    "Date_Last_Modified", "Size_KB", "Creating_Application", "Valid", "Well-Formed", "Status_Message"]
    df_expected = pd.DataFrame(rows, columns=column_names)

    # Reads the script output into a dataframe.
    # Removes fixity because that changes every time XLSX and ZIP are made.
    df_fits = pd.read_csv("accession_fits.csv")
    df_fits = df_fits.drop("MD5", axis=1)

    # Compares the script output to the expected values.
    compare_dataframes("Make_FITS_CSV", df_fits, df_expected)

    # Deletes the test files.
    shutil.rmtree("accession")
    shutil.rmtree("accession_FITS")
    os.remove("accession_fits.csv")


def test_make_fits_csv_function_errors():
    """Tests encoding error handling when saving FITS file data to the CSV."""


def test_match_nara_risk_function():
    """Tests combining NARA risk information with FITS information to produce df_results."""

    # Makes a dataframe to use for FITS information.
    # PUID variations: match 1 PUID and multiple PUIDs
    # Name variations: match with version or name only, including case not matching
    # Extension variations: match single extension and pipe-separated extension, including case not matching
    # Also includes 2 that won't match
    rows = [[r"C:\PUID\file.zip", "ZIP archive", np.NaN, "https://www.nationalarchives.gov.uk/pronom/x-fmt/263"],
            [r"C:\PUID\Double\movie.ifo", "DVD Data File", np.NaN, "https://www.nationalarchives.gov.uk/pronom/x-fmt/419"],
            [r"C:\Name\img.jp2", "JPEG 2000 File Format", np.NaN, np.NaN],
            [r"C:\Name\Case\file.gz", "gzip", np.NaN, np.NaN],
            [r"C:\Name\Version\database.nsf", "Lotus Notes Database", "2", np.NaN],
            [r"C:\Ext\Both\file.dat", "File Data", np.NaN, np.NaN],
            [r"C:\Ext\Case\file.BIN", "Unknown Binary", np.NaN, np.NaN],
            [r"C:\Ext\Multi\img.jpg", "JPEG", "1", np.NaN],
            [r"C:\Unmatched\file.new", "Brand New Format", np.NaN, np.NaN],
            [r"C:\Unmatched\file.none", "empty", np.NaN, np.NaN]]
    column_names = ["FITS_File_Path", "FITS_Format_Name", "FITS_Format_Version", "FITS_PUID"]
    df_fits = pd.DataFrame(rows, columns=column_names)

    # Reads the NARA risk CSV into a dataframe.
    # In format_analysis.py, this is done in the main body of the script before the function is called.
    df_nara = csv_to_dataframe(c.NARA)

    # Runs the function being tested.
    df_results = match_nara_risk(df_fits, df_nara)

    # Makes a dataframe with the expected values.
    rows = [[r"C:\PUID\file.zip", "ZIP archive", np.NaN, "https://www.nationalarchives.gov.uk/pronom/x-fmt/263",
             "ZIP archive", "zip", "https://www.nationalarchives.gov.uk/pronom/x-fmt/263", "Moderate Risk",
             "Retain but extract files from the container", "PRONOM"],
            [r"C:\PUID\Double\movie.ifo", "DVD Data File", np.NaN,
             "https://www.nationalarchives.gov.uk/pronom/x-fmt/419", "DVD Data Backup File", "bup",
             "https://www.nationalarchives.gov.uk/pronom/x-fmt/419", "Moderate Risk", "Retain", "PRONOM"],
            [r"C:\PUID\Double\movie.ifo", "DVD Data File", np.NaN,
             "https://www.nationalarchives.gov.uk/pronom/x-fmt/419", "DVD Data File", "dvd",
             "https://www.nationalarchives.gov.uk/pronom/x-fmt/419", "Moderate Risk", "Retain", "PRONOM"],
            [r"C:\PUID\Double\movie.ifo", "DVD Data File", np.NaN,
             "https://www.nationalarchives.gov.uk/pronom/x-fmt/419", "DVD Info File", "ifo",
             "https://www.nationalarchives.gov.uk/pronom/x-fmt/419", "Moderate Risk", "Retain", "PRONOM"],
            [r"C:\Name\img.jp2", "JPEG 2000 File Format", np.NaN, np.NaN, "JPEG 2000 File Format", "jp2",
             "https://www.nationalarchives.gov.uk/pronom/x-fmt/392", "Low Risk", "Retain", "Format Name"],
            [r"C:\Name\Case\file.gz", "gzip", np.NaN, np.NaN, "GZIP", "gz|tgz",
             "https://www.nationalarchives.gov.uk/pronom/x-fmt/266", "Low Risk",
             "Retain but extract files from the container", "Format Name"],
            [r"C:\Name\Version\database.nsf", "Lotus Notes Database", "2", np.NaN, "Lotus Notes Database 2",
             "nsf|ns2", "https://www.nationalarchives.gov.uk/pronom/x-fmt/336", "Moderate Risk", "Transform to CSV",
             "Format Name"],
            [r"C:\Ext\Both\file.dat", "File Data", np.NaN, np.NaN, "Data File", "dat", np.NaN, "Moderate Risk",
             "Retain", "File Extension"],
            [r"C:\Ext\Both\file.dat", "File Data", np.NaN, np.NaN, "Windows Registry Files", "reg|dat", np.NaN,
             "Moderate Risk", "Retain", "File Extension"],
            [r"C:\Ext\Case\file.BIN", "Unknown Binary", np.NaN, np.NaN, "Binary file", "bin",
             "https://www.nationalarchives.gov.uk/pronom/fmt/208", "High Risk", "Retain", "File Extension"],
            [r"C:\Ext\Multi\img.jpg", "JPEG", "1", np.NaN, "JPEG File Interchange Format 1.00", "jpg|jpeg",
             "https://www.nationalarchives.gov.uk/pronom/fmt/42", "Low Risk", "Retain", "File Extension"],
            [r"C:\Ext\Multi\img.jpg", "JPEG", "1", np.NaN, "JPEG File Interchange Format 1.01", "jpg|jpeg",
             "https://www.nationalarchives.gov.uk/pronom/fmt/43", "Low Risk", "Retain", "File Extension"],
            [r"C:\Ext\Multi\img.jpg", "JPEG", "1", np.NaN, "JPEG File Interchange Format 1.02", "jpg|jpeg",
             "https://www.nationalarchives.gov.uk/pronom/fmt/44", "Low Risk", "Retain", "File Extension"],
            [r"C:\Ext\Multi\img.jpg", "JPEG", "1", np.NaN, "JPEG Raw Stream", "jpg|jpeg",
             "https://www.nationalarchives.gov.uk/pronom/fmt/41", "Low Risk", "Retain", "File Extension"],
            [r"C:\Ext\Multi\img.jpg", "JPEG", "1", np.NaN, "JPEG unspecified version", "jpg|jpeg", np.NaN,
             "Low Risk", "Retain", "File Extension"],
            [r"C:\Unmatched\file.new", "Brand New Format", np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, "No Match",
             np.NaN, "No NARA Match"],
            [r"C:\Unmatched\file.none", "empty", np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, "No Match", np.NaN,
             "No NARA Match"]]
    column_names = ["FITS_File_Path", "FITS_Format_Name", "FITS_Format_Version", "FITS_PUID",
                    "NARA_Format Name", "NARA_File Extension(s)", "NARA_PRONOM URL", "NARA_Risk Level",
                    "NARA_Proposed Preservation Plan", "NARA_Match_Type"]
    df_expected = pd.DataFrame(rows, columns=column_names)

    # Compares the script output to the expected values.
    compare_dataframes("Match_NARA", df_results, df_expected)


def test_match_technical_appraisal_function():
    """Tests adding technical appraisal categories to df_results,
    which will already have information from FITS and NARA.
    In format_analysis.py, this is done in the main body of the script."""

    # Makes a dataframe to use as input.
    # Data variation: examples that match both, one, or neither of the technical appraisal categories,
    # with identical cases and different cases (match is case-insensitive).
    rows = [[r"C:\CD1\Flower.JPG", "JPEG EXIF"],
            [r"C:\CD1\Trashes\Flower1.JPG", "JPEG EXIF"],
            [r"C:\CD2\Script\config.pyc", "unknown binary"],
            [r"C:\CD2\Trash Data\data.zip", "ZIP Format"],
            [r"C:\CD2\trash\New Document.txt", "Plain text"],
            [r"C:\CD2\Trash\New Text.txt", "Plain text"],
            [r"C:\FD1\empty.txt", "empty"],
            [r"C:\FD1\trashes\program.dll", "PE32 executable"]]
    column_names = ["FITS_File_Path", "FITS_Format_Name"]
    df_results = pd.DataFrame(rows, columns=column_names)

    # Reads the technical appraisal CSV into a dataframe.
    # In format_analysis.py, this is done in the main body of the script before the function is called.
    df_ita = csv_to_dataframe(c.ITA)

    # Runs the function being tested.
    df_results = match_technical_appraisal(df_results, df_ita)

    # Makes a dataframe with the expected values.
    rows = [[r"C:\CD1\Flower.JPG", "JPEG EXIF", "Not for TA"],
            [r"C:\CD1\Trashes\Flower1.JPG", "JPEG EXIF", "Trash"],
            [r"C:\CD2\Script\config.pyc", "unknown binary", "Format"],
            [r"C:\CD2\Trash Data\data.zip", "ZIP Format", "Not for TA"],
            [r"C:\CD2\trash\New Document.txt", "Plain text", "Trash"],
            [r"C:\CD2\Trash\New Text.txt", "Plain text", "Trash"],
            [r"C:\FD1\empty.txt", "empty", "Format"],
            [r"C:\FD1\trashes\program.dll", "PE32 executable", "Trash"]]
    column_names = ["FITS_File_Path", "FITS_Format_Name", "Technical Appraisal"]
    df_expected = pd.DataFrame(rows, columns=column_names)

    # Compares the script output to the expected values.
    compare_dataframes("Match_TA", df_results, df_expected)


def test_match_other_risk_function():
    """Tests adding other risk categories to df_results,
    which will already have information from FITS, NARA, and technical appraisal.
    In format_analysis.py, this is done in the main body of the script."""

    # Makes a dataframe to use as input.
    # Data variation: examples that match both, one, or neither of the other risk categories,
    # with identical cases and different cases (match is case-insensitive),
    # and at least one each of the format risk criteria.
    rows = [["Adobe Photoshop file", "Moderate Risk", "Transform to TIFF or JPEG2000"],
            ["Cascading Style Sheet", "Low Risk", "Retain"],
            ["CorelDraw Drawing", "High Risk", "Transform to a TBD format, possibly PDF or TIFF"],
            ["empty", np.NaN, np.NaN],
            ["Encapsulated Postscript File", "Low Risk", "Transform to TIFF or JPEG2000"],
            ["iCalendar", "Low Risk", "Transform to CSV"],
            ["MBOX Email Format", "Low Risk", "Transform to EML but also retain MBOX"],
            ["Plain text", "Low Risk", "Retain"],
            ["zip format", "Low Risk", "Retain"]]
    column_names = ["FITS_Format_Name", "NARA_Risk Level", "NARA_Proposed Preservation Plan"]
    df_results = pd.DataFrame(rows, columns=column_names)

    # Reads the risk file formats CSV into a dataframe.
    # In format_analysis.py, this is done in the main body of the script before the function is called.
    df_other = csv_to_dataframe(c.RISK)

    # Runs the function being tested.
    df_results = match_other_risk(df_results, df_other)

    # Makes a dataframe with the expected values.
    rows = [["Adobe Photoshop file", "Moderate Risk", "Transform to TIFF or JPEG2000", "Layered image file"],
            ["Cascading Style Sheet", "Low Risk", "Retain", "Possible saved web page"],
            ["CorelDraw Drawing", "High Risk", "Transform to a TBD format, possibly PDF or TIFF", "Layered image file"],
            ["empty", np.NaN, np.NaN, "Not for Other"],
            ["Encapsulated Postscript File", "Low Risk", "Transform to TIFF or JPEG2000", "Layered image file"],
            ["iCalendar", "Low Risk", "Transform to CSV", "NARA Low/Transform"],
            ["MBOX Email Format", "Low Risk", "Transform to EML but also retain MBOX", "NARA Low/Transform"],
            ["Plain text", "Low Risk", "Retain", "Not for Other"],
            ["zip format", "Low Risk", "Retain", "Archive format"]]
    column_names = ["FITS_Format_Name", "NARA_Risk Level", "NARA_Proposed Preservation Plan", "Other_Risk"]
    df_expected = pd.DataFrame(rows, columns=column_names)

    # Compares the script output to the expected values.
    compare_dataframes("Match_Other", df_results, df_expected)


def test_deduplicating_results():
    """Tests that duplicates from multiple NARA matches with the same risk information are correctly removed."""

    # Makes a dataframe to use as input, with a subset of the columns usually in df_results.
    # Data variation: one FITS ID with one NARA match, multiple FITS IDs with one NARA match each,
    # multiple NARA matches with the same risk, multiple NARA matches with different risks.
    rows = [[r"C:\acc\disk1\data.csv", "Comma-Separated Values (CSV)", "Comma Separated Values", "csv", "https://www.nationalarchives.gov.uk/pronom/x-fmt/18", "Low Risk", "Retain"],
            [r"C:\acc\disk1\data.xlsx", "Open Office XML Workbook", "Microsoft Excel Office Open XML", "xlsx", "https://www.nationalarchives.gov.uk/pronom/fmt/214", "Low Risk", "Retain"],
            [r"C:\acc\disk1\data.xlsx", "XLSX", "Microsoft Excel Office Open XML", "xlsx", "https://www.nationalarchives.gov.uk/pronom/fmt/214", "Low Risk", "Retain"],
            [r"C:\acc\disk1\empty.txt", "empty", "ASCII 7-bit Text", "txt|asc|csv|tab", "https://www.nationalarchives.gov.uk/pronom/x-fmt/22", "Low Risk", "Retain"],
            [r"C:\acc\disk1\empty.txt", "empty", "ASCII 8-bit Text", "txt|asc|csv|tab", "https://www.nationalarchives.gov.uk/pronom/x-fmt/283", "Low Risk", "Retain"],
            [r"C:\acc\disk1\empty.txt", "empty", "JSON", "json|txt", "https://www.nationalarchives.gov.uk/pronom/fmt/817", "Low Risk", "Retain"],
            [r"C:\acc\disk1\empty.txt", "empty", "Plain Text", "Plain_Text|txt|text|asc|rte", "https://www.nationalarchives.gov.uk/pronom/x-fmt/111", "Low Risk", "Retain"],
            [r"C:\acc\disk1\file.pdf", "PDF", "Portable Document Format (PDF) version 1.7", "pdf", "https://www.nationalarchives.gov.uk/pronom/fmt/276", "Moderate Risk", "Retain"],
            [r"C:\acc\disk1\file.pdf", "PDF", "Portable Document Format (PDF) version 2.0", "pdf", "https://www.nationalarchives.gov.uk/pronom/fmt/1129", "Moderate Risk", "Retain"],
            [r"C:\acc\disk1\file.pdf", "PDF", "Portable Document Format/Archiving (PDF/A-1a) accessible", "pdf", "https://www.nationalarchives.gov.uk/pronom/fmt/95", "Low Risk", "Retain"]]
    column_names = ["FITS_File_Path", "FITS_Format_Name", "NARA_Format Name", "NARA_File Extension(s)",
                    "NARA_PRONOM URL", "NARA_Risk Level", "NARA_Proposed Preservation Plan"]
    df_results = pd.DataFrame(rows, columns=column_names)

    # Removes columns with NARA identification info and then removes duplicate rows.
    # In format_analysis.py, this is done in the main body of the script.
    df_results.drop(["NARA_Format Name", "NARA_File Extension(s)", "NARA_PRONOM URL"], inplace=True, axis=1)
    df_results.drop_duplicates(inplace=True)

    # Makes a dataframe with the expected values.
    rows = [[r"C:\acc\disk1\data.csv", "Comma-Separated Values (CSV)", "Low Risk", "Retain"],
            [r"C:\acc\disk1\data.xlsx", "Open Office XML Workbook", "Low Risk", "Retain"],
            [r"C:\acc\disk1\data.xlsx", "XLSX", "Low Risk", "Retain"],
            [r"C:\acc\disk1\empty.txt", "empty", "Low Risk", "Retain"],
            [r"C:\acc\disk1\file.pdf", "PDF", "Moderate Risk", "Retain"],
            [r"C:\acc\disk1\file.pdf", "PDF", "Low Risk", "Retain"]]
    column_names = ["FITS_File_Path", "FITS_Format_Name", "NARA_Risk Level", "NARA_Proposed Preservation Plan"]
    df_expected = pd.DataFrame(rows, columns=column_names)

    # Compares the script output to the expected values.
    compare_dataframes("Deduplicate_Results_DF", df_results, df_expected)


def test_nara_risk_subset():
    """Tests the NARA risk subset, which is based on the NARA_Risk Level column."""

    # Makes a dataframe to use as input.
    # Data variation: all 4 risk levels and all columns to be dropped.
    rows = [[r"C:\Disk1\file.txt", "Plain text", "Low Risk", "drop", "drop", "drop", "drop", "drop", "drop"],
            [r"C:\Disk1\photo.jpg", "JPEG EXIF", "Low Risk", "drop", "drop", "drop", "drop", "drop", "drop"],
            [r"C:\Disk1\file.psd", "Adobe Photoshop file", "Moderate Risk", "drop", "drop", "drop", "drop", "drop", "drop"],
            [r"C:\Disk1\file.bak", "Backup File", "High Risk", "drop", "drop", "drop", "drop", "drop", "drop"],
            [r"C:\Disk1\new.txt", "empty", "No Match", "drop", "drop", "drop", "drop", "drop", "drop"]]
    column_names = ["FITS_File_Path", "FITS_Format_Name", "NARA_Risk Level", "FITS_PUID", "FITS_Identifying_Tool(s)",
                    "FITS_Creating_Application", "FITS_Valid", "FITS_Well-Formed", "FITS_Status_Message"]
    df_results = pd.DataFrame(rows, columns=column_names)

    # Calculates the subset.
    # In format_analysis.py, this is done in the main body of the script.
    df_nara_risk = df_results[df_results["NARA_Risk Level"] != "Low Risk"].copy()
    df_nara_risk.drop(["FITS_PUID", "FITS_Identifying_Tool(s)", "FITS_Creating_Application",
                       "FITS_Valid", "FITS_Well-Formed", "FITS_Status_Message"], inplace=True, axis=1)

    # Makes a dataframe with the expected values.
    rows = [[r"C:\Disk1\file.psd", "Adobe Photoshop file", "Moderate Risk"],
            [r"C:\Disk1\file.bak", "Backup File", "High Risk"],
            [r"C:\Disk1\new.txt", "empty", "No Match"]]
    column_names = ["FITS_File_Path", "FITS_Format_Name", "NARA_Risk Level"]
    df_expected = pd.DataFrame(rows, columns=column_names)

    # Compares the script output to the expected values.
    compare_dataframes("NARA_Risk_Subset", df_nara_risk, df_expected)


def test_multiple_subset():
    """Tests the files with multiple FITs format ids subset, which is based on the FITS_File_Path column."""

    # Makes a dataframe to use as input.
    # Data variation: files with multiple ids and files without; all columns to be dropped.
    rows = [[r"C:\Disk1\file1.txt", "Plain text", False, "drop", "drop", "drop"],
            [r"C:\Disk1\file2.html", "Hypertext Markup Language", True, "drop", "drop", "drop"],
            [r"C:\Disk1\file2.html", "HTML Transitional", True, "drop", "drop", "drop"],
            [r"C:\Disk1\file3.xlsx", "Open Office XML Document", True, "drop", "drop", "drop"],
            [r"C:\Disk1\file3.xlsx", "Open Office XML Workbook", True, "drop", "drop", "drop"],
            [r"C:\Disk1\file3.xlsx", "XLSX", True, "drop", "drop", "drop"],
            [r"C:\Disk1\photo.jpg", "JPEG EXIF", False, "drop", "drop", "drop"]]
    column_names = ["FITS_File_Path", "FITS_Format_Name", "FITS_Multiple_IDs",
                    "FITS_Valid", "FITS_Well-Formed", "FITS_Status_Message"]
    df_results = pd.DataFrame(rows, columns=column_names)

    # Calculates the subset.
    # In format_analysis.py, this is done in the main body of the script.
    df_multiple = df_results[df_results.duplicated("FITS_File_Path", keep=False) == True].copy()
    df_multiple.drop(["FITS_Valid", "FITS_Well-Formed", "FITS_Status_Message"], inplace=True, axis=1)

    # Makes a dataframe with the expected values.
    rows = [[r"C:\Disk1\file2.html", "Hypertext Markup Language", True],
            [r"C:\Disk1\file2.html", "HTML Transitional", True],
            [r"C:\Disk1\file3.xlsx", "Open Office XML Document", True],
            [r"C:\Disk1\file3.xlsx", "Open Office XML Workbook", True],
            [r"C:\Disk1\file3.xlsx", "XLSX", True]]
    column_names = ["FITS_File_Path", "FITS_Format_Name", "FITS_Multiple_IDs"]
    df_expected = pd.DataFrame(rows, columns=column_names)

    # Compares the script output to the expected values.
    compare_dataframes("Multiple_Subset", df_multiple, df_expected)


def test_validation_subset():
    """Tests the FITS validation subset, which is based on the FITS_Valid, FITS_Well-Formed,
    and FITS_Status_Message columns."""

    # Makes a dataframe to use as input.
    # Data variation: values in 0, 1, 2, or 3 columns will include the file in the validation subset.
    # Some of these combinations probably wouldn't happen in real data, but want to be thorough.
    rows = [[r"C:\Disk1\file1.txt", "Plain text", True, True, np.NaN],
            [r"C:\Disk1\file2.html", "Hypertext Markup Language", np.NaN, np.NaN, np.NaN],
            [r"C:\Disk1\file2.html", "HTML Transitional", False, True, np.NaN],
            [r"C:\Disk1\file3.xlsx", "Open Office XML Document", True, False, np.NaN],
            [r"C:\Disk1\file3.xlsx", "Open Office XML Workbook", True, True, "Validation Error"],
            [r"C:\Disk1\file3.xlsx", "XLSX", False, False, np.NaN],
            [r"C:\Disk1\photo.jpg", "JPEG EXIF", True, False, "Validation Error"],
            [r"C:\Disk1\photo1.jpg", "JPEG EXIF", False, True, "Validation Error"],
            [r"C:\Disk1\photo2.jpg", "JPEG EXIF", False, False, "Validation Error"]]
    column_names = ["FITS_File_Path", "FITS_Format_Name", "FITS_Valid", "FITS_Well-Formed", "FITS_Status_Message"]
    df_results = pd.DataFrame(rows, columns=column_names)

    # Calculates the subset.
    # In format_analysis.py, this is done in the main body of the script.
    df_validation = df_results[(df_results["FITS_Valid"] == False) | (df_results["FITS_Well-Formed"] == False) |
                               (df_results["FITS_Status_Message"].notnull())].copy()

    # Makes a dataframe with the expected values.
    rows = [[r"C:\Disk1\file2.html", "HTML Transitional", False, True, np.NaN],
            [r"C:\Disk1\file3.xlsx", "Open Office XML Document", True, False, np.NaN],
            [r"C:\Disk1\file3.xlsx", "Open Office XML Workbook", True, True, "Validation Error"],
            [r"C:\Disk1\file3.xlsx", "XLSX", False, False, np.NaN],
            [r"C:\Disk1\photo.jpg", "JPEG EXIF", True, False, "Validation Error"],
            [r"C:\Disk1\photo1.jpg", "JPEG EXIF", False, True, "Validation Error"],
            [r"C:\Disk1\photo2.jpg", "JPEG EXIF", False, False, "Validation Error"]]
    column_names = ["FITS_File_Path", "FITS_Format_Name", "FITS_Valid", "FITS_Well-Formed", "FITS_Status_Message"]
    df_expected = pd.DataFrame(rows, columns=column_names)

    # Compares the script output to the expected values.
    compare_dataframes("Validation_Subset", df_validation, df_expected)


def test_tech_appraisal_subset():
    """Tests the technical appraisal subset, which is based on the Technical_Appraisal column."""

    # Makes a dataframe to use as input.
    # Data variation: all 3 technical appraisal categories and all columns to drop.
    rows = [["DOS/Windows Executable", "Format", "drop", "drop", "drop", "drop", "drop", "drop"],
            ["JPEG EXIF", "Not for TA", "drop", "drop", "drop", "drop", "drop", "drop"],
            ["Unknown Binary", "Format", "drop", "drop", "drop", "drop", "drop", "drop"],
            ["Plain text", "Not for TA", "drop", "drop", "drop", "drop", "drop", "drop"],
            ["JPEG EXIF", "Trash", "drop", "drop", "drop", "drop", "drop", "drop"],
            ["Open Office XML Workbook", "Trash", "drop", "drop", "drop", "drop", "drop", "drop"]]
    column_names = ["FITS_Format_Name", "Technical_Appraisal", "FITS_PUID", "FITS_Date_Last_Modified",
                    "FITS_MD5", "FITS_Valid", "FITS_Well-Formed", "FITS_Status_Message"]
    df_results = pd.DataFrame(rows, columns=column_names)

    # Calculates the subset.
    # In format_analysis.py, this is done in the main body of the script.
    df_tech_appraisal = df_results[df_results["Technical_Appraisal"] != "Not for TA"].copy()
    df_tech_appraisal.drop(["FITS_PUID", "FITS_Date_Last_Modified", "FITS_MD5", "FITS_Valid", "FITS_Well-Formed",
                            "FITS_Status_Message"], inplace=True, axis=1)

    # Makes a dataframe with the expected values.
    rows = [["DOS/Windows Executable", "Format"],
            ["Unknown Binary", "Format"],
            ["JPEG EXIF", "Trash"],
            ["Open Office XML Workbook", "Trash"]]
    column_names = ["FITS_Format_Name", "Technical_Appraisal"]
    df_expected = pd.DataFrame(rows, columns=column_names)

    # Compares the script output to the expected values.
    compare_dataframes("Tech_Appraisal_Subset", df_tech_appraisal, df_expected)


def test_other_risk_subset():
    """Tests the other risk subset, which is based on the Other_Risk column."""

    # Makes a dataframe to use as input.
    # Data variation: all other risk categories and all columns to drop.
    rows = [["DOS/Windows Executable", "Not for Other", "drop", "drop", "drop", "drop", "drop", "drop", "drop"],
            ["Adobe Photoshop file", "Layered image file", "drop", "drop", "drop", "drop", "drop", "drop", "drop"],
            ["JPEG EXIF", "Not for Other", "drop", "drop", "drop", "drop", "drop", "drop", "drop"],
            ["Cascading Style Sheet", "Possible saved web page", "drop", "drop", "drop", "drop", "drop", "drop", "drop"],
            ["iCalendar", "NARA Low/Transform", "drop", "drop", "drop", "drop", "drop", "drop", "drop"],
            ["Zip Format", "Archive format", "drop", "drop", "drop", "drop", "drop", "drop", "drop"]]
    column_names = ["FITS_Format_Name", "Other_Risk", "FITS_PUID", "FITS_Date_Last_Modified", "FITS_MD5",
                    "FITS_Creating_Application", "FITS_Valid", "FITS_Well-Formed", "FITS_Status_Message"]
    df_results = pd.DataFrame(rows, columns=column_names)

    # Calculates the subset.
    # In format_analysis.py, this is done in the main body of the script.
    df_other_risk = df_results[df_results["Other_Risk"] != "Not for Other"].copy()
    df_other_risk.drop(["FITS_PUID", "FITS_Date_Last_Modified", "FITS_MD5", "FITS_Creating_Application", "FITS_Valid",
                        "FITS_Well-Formed", "FITS_Status_Message"], inplace=True, axis=1)

    # Makes a dataframe with the expected values.
    rows = [["Adobe Photoshop file", "Layered image file"],
            ["Cascading Style Sheet", "Possible saved web page"],
            ["iCalendar", "NARA Low/Transform"],
            ["Zip Format", "Archive format"]]
    column_names = ["FITS_Format_Name", "Other_Risk"]
    df_expected = pd.DataFrame(rows, columns=column_names)

    # Compares the script output to the expected values.
    compare_dataframes("Other_Risk_Subset", df_other_risk, df_expected)


def test_duplicates_subset():
    """Tests the duplicates subset, which is based on the FITS_File_Path and FITS_MD5 columns."""

    # Makes a dataframe to use as input.
    # Data variation: unique files, files duplicate because of multiple FITs file ids, and real duplicate files.
    rows = [[r"C:\Disk1\file1.txt", "Plain text", 0.004, "098f6bcd4621d373cade4e832627b4f6"],
            [r"C:\Disk1\file3.xlsx", "Open Office XML Document", 19.316, "b66e2fa385872d1a16d31b00f4b5f035"],
            [r"C:\Disk1\file3.xlsx", "Open Office XML Workbook", 19.316, "b66e2fa385872d1a16d31b00f4b5f035"],
            [r"C:\Disk1\file3.xlsx", "XLSX", 19.316, "b66e2fa385872d1a16d31b00f4b5f035"],
            [r"C:\Disk1\photo.jpg", "JPEG EXIF", 13.563, "686779fae835aadff6474898f5781e99"],
            [r"C:\Disk2\file1.txt", "Plain text", 0.004, "098f6bcd4621d373cade4e832627b4f6"],
            [r"C:\Disk3\file1.txt", "Plain text", 0.004, "098f6bcd4621d373cade4e832627b4f6"]]
    column_names = ["FITS_File_Path", "FITS_Format_Name", "FITS_Size_KB", "FITS_MD5"]
    df_results = pd.DataFrame(rows, columns=column_names)

    # Calculates the subset.
    # In format_analysis.py, this is done in the main body of the script.
    df_duplicates = df_results[["FITS_File_Path", "FITS_Size_KB", "FITS_MD5"]].copy()
    df_duplicates = df_duplicates.drop_duplicates(subset=["FITS_File_Path"], keep=False)
    df_duplicates = df_duplicates.loc[df_duplicates.duplicated(subset="FITS_MD5", keep=False)]

    # Makes a dataframe with the expected values.
    rows = [[r"C:\Disk1\file1.txt", 0.004, "098f6bcd4621d373cade4e832627b4f6"],
            [r"C:\Disk2\file1.txt", 0.004, "098f6bcd4621d373cade4e832627b4f6"],
            [r"C:\Disk3\file1.txt", 0.004, "098f6bcd4621d373cade4e832627b4f6"]]
    column_names = ["FITS_File_Path", "FITS_Size_KB", "FITS_MD5"]
    df_expected = pd.DataFrame(rows, columns=column_names)

    # Compares the script output to the expected values.
    compare_dataframes("Duplicates_Subset", df_duplicates, df_expected)


def test_empty_subset():
    """Tests handling of an empty subset, which can happen with any subset.
    Using the file with multiple format ids and duplicate MD5s subsets for testing."""

    # Makes a dataframe to use as input where all files have a unique identification and unique MD5.
    rows = [[r"C:\Disk1\file1.txt", "Plain text", 0.004, "098f6bcd4621d373cade4e832627b4f6"],
            [r"C:\Disk1\file2.txt", "Plain text", 5.347, "c9f6d785a33cfac2cc1f51ab4704b8a1"],
            [r"C:\Disk2\file3.pdf", "Portable Document Format", 187.972, "6dfeecf4e4200a0ad147a7271a094e68"],
            [r"c:\Disk2\file4.txt", "Plain text", 0.178, "97e4f6e6f35e5606855d0917e22740b9"]]
    column_names = ["FITS_File_Path", "FITS_Format_Name", "FITS_Size_KB", "FITS_MD5"]
    df_results = pd.DataFrame(rows, columns=column_names)

    # Calculates both subsets.
    # In format_analysis.py, this is done in the main body of the script.
    df_multiple = df_results[df_results.duplicated("FITS_File_Path", keep=False) == True].copy()

    df_duplicates = df_results[["FITS_File_Path", "FITS_Size_KB", "FITS_MD5"]].copy()
    df_duplicates = df_duplicates.drop_duplicates(subset=["FITS_File_Path"], keep=False)
    df_duplicates = df_duplicates.loc[df_duplicates.duplicated(subset="FITS_MD5", keep=False)]

    # Tests each subset for if they are empty and supplies default text.
    # In format_analysis.py, this is done in the main body of the script
    # and includes all 6 subset dataframes in the tuple.
    for df in (df_multiple, df_duplicates):
        if len(df) == 0:
            df.loc[len(df)] = ["No data of this type"] + [np.NaN] * (len(df.columns) - 1)

    # Makes dataframes with the expected values for each subset.
    rows = [["No data of this type", np.NaN, np.NaN, np.NaN]]
    column_names = ["FITS_File_Path", "FITS_Format_Name", "FITS_Size_KB", "FITS_MD5"]
    df_multiple_expected = pd.DataFrame(rows, columns=column_names)

    rows = [["No data of this type", np.NaN, np.NaN]]
    column_names = ["FITS_File_Path", "FITS_Size_KB", "FITS_MD5"]
    df_duplicates_expected = pd.DataFrame(rows, columns=column_names)

    # Compares the script output to the expected values for each subset.
    compare_dataframes("Empty_Multiple_Subset", df_multiple, df_multiple_expected)
    compare_dataframes("Empty_Duplicate_Subset", df_duplicates, df_duplicates_expected)


def test_format_subtotal():
    """Tests the format subtotals, which is based on FITS_Format_Name and NARA_Risk Level."""

    # Makes a dataframe to use as input for the subtotal() function.
    # Data variation: formats with one row, formats with multiple rows, one format with a NARA risk level,
    # multiple formats with a NARA risk level, blank in NARA risk level.
    rows = [["JPEG EXIF", 13.563, "Low Risk"],
            ["JPEG EXIF", 14.1, "Low Risk"],
            ["Open Office XML Workbook", 19.316, "Low Risk"],
            ["Unknown Binary", 0, np.NaN],
            ["Unknown Binary", 1, np.NaN],
            ["Unknown Binary", 5, np.NaN],
            ["XLSX", 19.316, "Low Risk"],
            ["Zip Format", 2.792, "Moderate Risk"]]
    column_names = ["FITS_Format_Name", "FITS_Size_KB", "NARA_Risk Level"]
    df_results = pd.DataFrame(rows, columns=column_names)

    # Calculates the total files and total size in the dataframe to use for percentages with the subtotals.
    # In format_analysis.py, this is done in the main body of the script before subtotal() is called.
    totals_dict = {"Files": len(df_results.index), "MB": df_results["FITS_Size_KB"].sum() / 1000}

    # Runs the subtotal() function for this subtotal.
    df_format_subtotals = subtotal(df_results, ["FITS_Format_Name", "NARA_Risk Level"], totals_dict)

    # Makes a dataframe with the expected values.
    # The index values for the dataframe made by subtotal() are column values here
    # so that they are visible in the comparison dataframe to label errors.
    rows = [["JPEG EXIF", "Low Risk", 2, 25, 0.028, 37.29],
            ["Unknown Binary", np.NaN, 3, 37.5, 0.006, 7.991],
            ["Zip Format", "Moderate Risk", 1, 12.5, 0.003, 3.995],
            ["Open Office XML Workbook", "Low Risk", 1, 12.5, 0.019, 25.304],
            ["XLSX", "Low Risk", 1, 12.5, 0.019, 25.304]]
    column_names = ["FITS_Format_Name", "NARA_Risk Level", "File Count", "File %", "Size (MB)", "Size %"]
    df_expected = pd.DataFrame(rows, columns=column_names)

    # Compares the script output to the expected values.
    compare_dataframes("Format_Subtotals", df_format_subtotals, df_expected)


def test_nara_risk_subtotal():
    """Tests the NARA risk subtotals, which is based on NARA_Risk Level."""

    # Makes a dataframe to use as input for the subtotal() function.
    # Data variation: one format with a NARA risk level, multiple formats with a NARA risk level, all 4 risk levels.
    rows = [["DOS/Windows Executable", 1.23, "High Risk"],
            ["DOS/Windows Executable", 2.34, "High Risk"],
            ["DOS/Windows Executable", 3.45, "High Risk"],
            ["JPEG EXIF", 13.563, "Low Risk"],
            ["JPEG EXIF", 14.1, "Low Risk"],
            ["Open Office XML Workbook", 19.316, "Low Risk"],
            ["Unknown Binary", 0, "No Match"],
            ["Unknown Binary", 5, "No Match"],
            ["XLSX", 19.316, "Low Risk"],
            ["Zip Format", 2.792, "Moderate Risk"]]
    column_names = ["FITS_Format_Name", "FITS_Size_KB", "NARA_Risk Level"]
    df_results = pd.DataFrame(rows, columns=column_names)

    # Calculates the total files and total size in the dataframe to use for percentages with the subtotals.
    # In format_analysis.py, this is done in the main body of the script before subtotal() is called.
    totals_dict = {"Files": len(df_results.index), "MB": df_results["FITS_Size_KB"].sum() / 1000}

    # Runs the subtotal() function for this subtotal.
    df_nara_risk_subtotals = subtotal(df_results, ["NARA_Risk Level"], totals_dict)

    # Makes a dataframe with the expected values.
    # The index value for the dataframe made by subtotal() is a column value here
    # so that it is visible in the comparison dataframe to label errors.
    rows = [["Low Risk", 4, 40, 0.066, 81.374],
            ["Moderate Risk", 1, 10, 0.003, 3.699],
            ["High Risk", 3, 30, 0.007, 8.631],
            ["No Match", 2, 20, 0.005, 6.165]]
    column_names = ["NARA_Risk Level", "File Count", "File %", "Size (MB)", "Size %"]
    df_expected = pd.DataFrame(rows, columns=column_names)

    # Compares the script output to the expected values.
    compare_dataframes("NARA_Risk_Subtotals", df_nara_risk_subtotals, df_expected)


def test_technical_appraisal_subtotal():
    """Tests the technical appraisal subtotals, which is based on technical appraisal criteria and FITS_Format_Name."""

    # Makes a dataframe to use as input for the subtotal() function.
    # Data variation: for both criteria, has a unique format and duplicated formats.
    rows = [["Format", "DOS/Windows Executable", 100.23],
            ["Format", "DOS/Windows Executable", 200.34],
            ["Format", "PE32 executable", 300.45],
            ["Format", "Unknown Binary", 0],
            ["Format", "Unknown Binary", 50],
            ["Trash", "JPEG EXIF", 130.563],
            ["Trash", "JPEG EXIF", 140.1],
            ["Trash", "Open Office XML Workbook", 190.316]]
    column_names = ["Technical_Appraisal", "FITS_Format_Name", "FITS_Size_KB"]
    df_results = pd.DataFrame(rows, columns=column_names)

    # Calculates the total files and total size in the dataframe to use for percentages with the subtotals.
    # In format_analysis.py, this is done in the main body of the script before subtotal() is called.
    totals_dict = {"Files": len(df_results.index), "MB": df_results["FITS_Size_KB"].sum() / 1000}

    # Runs the subtotal() function for this subtotal.
    df_tech_appraisal_subtotals = subtotal(df_results, ["Technical_Appraisal", "FITS_Format_Name"], totals_dict)

    # Makes a dataframe with the expected values.
    # The index values for the dataframes made by subtotal() are column values here
    # so that they are visible in the comparison dataframe to label errors.
    rows = [["Format", "DOS/Windows Executable", 2, 25, 0.301, 27.068],
            ["Format", "PE32 executable", 1, 12.5, 0.300, 26.978],
            ["Format", "Unknown Binary", 2, 25, 0.05, 4.496],
            ["Trash", "JPEG EXIF", 2, 25, 0.271, 24.371],
            ["Trash", "Open Office XML Workbook", 1, 12.5, 0.19, 17.086]]
    column_names = ["Technical_Appraisal", "FITS_Format_Name", "File Count", "File %", "Size (MB)", "Size %"]
    df_expected = pd.DataFrame(rows, columns=column_names)

    # Compares the script output to the expected values.
    compare_dataframes("Tech_Appraisal_Subtotals", df_tech_appraisal_subtotals, df_expected)


def test_technical_appraisal_subtotal_empty():
    """Tests the technical appraisal subtotals when there are no files in the input
    which meet any technical appraisal criteria."""

    # Makes an empty dataframe to use as input for the subtotal() function.
    df_results = pd.DataFrame(columns=["Technical_Appraisal", "FITS_Format_Name", "FITS_Size_KB"])

    # Calculates the total files and total size in the dataframe to use for percentages with the subtotals.
    # In format_analysis.py, this is done in the main body of the script before subtotal() is called.
    totals_dict = {"Files": len(df_results.index), "MB": df_results["FITS_Size_KB"].sum() / 1000}

    # Runs the subtotal() function for this subtotal.
    df_tech_appraisal_subtotals = subtotal(df_results, ["Technical_Appraisal", "FITS_Format_Name"], totals_dict)

    # Makes a dataframe with the expected values.
    rows = [["No data of this type", np.NaN, np.NaN, np.NaN]]
    column_names = ["File Count", "File %", "Size (MB)", "Size %"]
    df_expected = pd.DataFrame(rows, columns=column_names)

    # Compares the script output to the expected values.
    compare_dataframes("Tech_Appraisal_Subtotals_Empty", df_tech_appraisal_subtotals, df_expected)


def test_other_risk_subtotal():
    """Tests the other risk subtotals, which is based on other risk criteria and FITS_Format_Name."""

    # Makes a dataframe to use as input for the subtotal() function.
    # Data variation: for each of the values for other risk, has unique formats and duplicated formats.
    rows = [["Not for Other", "DOS/Windows Executable", 100.23],
            ["Not for Other", "JPEG EXIF", 1300.563],
            ["Not for Other", "JPEG EXIF", 1400.1],
            ["Not for Other", "JPEG EXIF", 1900.316],
            ["Not for Other", "PE32 Executable", 200.34],
            ["Possible saved web page", "Cascading Style Sheet", 10000],
            ["Archive format", "Zip Format", 20000],
            ["Archive format", "Zip Format", 20000],
            ["Archive format", "Zip Format", 30000],
            ["Archive format", "Zip Format", 30000]]
    column_names = ["Other_Risk", "FITS_Format_Name", "FITS_Size_KB"]
    df_results = pd.DataFrame(rows, columns=column_names)

    # Calculates the total files and total size in the dataframe to use for percentages with the subtotals.
    # In format_analysis.py, this is done in the main body of the script before subtotal() is called.
    totals_dict = {"Files": len(df_results.index), "MB": df_results["FITS_Size_KB"].sum() / 1000}

    # Runs the subtotal() function for this subtotal.
    df_other_risk_subtotals = subtotal(df_results, ["Other_Risk", "FITS_Format_Name"], totals_dict)

    # Makes a dataframe with the expected values.
    # The index values for the dataframes made by subtotal() are column values here
    # so that they are visible in the comparison dataframe to label errors.
    rows = [["Not for Other", "DOS/Windows Executable", 1, 10, 0.1, 0.087],
            ["Not for Other", "JPEG EXIF", 3, 30, 4.601, 4.004],
            ["Not for Other", "PE32 Executable", 1, 10, 0.2, 0.174],
            ["Possible saved web page", "Cascading Style Sheet", 1, 10, 10, 8.703],
            ["Archive format", "ZIP Format", 4, 40, 100, 87.031]]
    column_names = ["Other_Risk", "FITS_Format_Name", "File Count", "File %", "Size (MB)", "Size %"]
    df_expected = pd.DataFrame(rows, columns=column_names)

    # Compares the script output to the expected values.
    compare_dataframes("Other_Risk_Subtotals", df_other_risk_subtotals, df_expected)


def test_other_risk_subtotal_empty():
    """Tests the other risk subtotals when there are no files in the input which meet any other risk criteria."""

    # Makes an empty dataframe to use as input for the subtotal() function.
    df_results = pd.DataFrame(columns=["Other_Risk", "FITS_Format_Name", "FITS_Size_KB"])

    # Calculates the total files and total size in the dataframe to use for percentages with the subtotals.
    # In format_analysis.py, this is done in the main body of the script before subtotal() is called.
    totals_dict = {"Files": len(df_results.index), "MB": df_results["FITS_Size_KB"].sum() / 1000}

    # Runs the subtotal() function for this subtotal.
    df_other_risk_subtotals = subtotal(df_results, ["Other_Risk", "FITS_Format_Name"], totals_dict)

    # Makes a dataframe with the expected values.
    rows = [["No data of this type", np.NaN, np.NaN, np.NaN]]
    column_names = ["File Count", "File %", "Size (MB)", "Size %"]
    df_expected = pd.DataFrame(rows, columns=column_names)

    # Compares the script output to the expected values.
    compare_dataframes("Other_Risk_Subtotals_Empty", df_other_risk_subtotals, df_expected)


def test_media_subtotal_function():
    """Tests variations in subtotals."""

    # Makes a dataframe and accession_folder variable to use as input.
    # Data variations: Disks with and without each risk type, unique values and values to add for subtotals.
    accession_folder = r"C:\ACC"
    rows = [[r"C:\ACC\Disk1\file.txt", 120, "Low Risk", "Not for TA", "Not for Other"],
            [r"C:\ACC\Disk1\file2.txt", 130, "Low Risk", "Not for TA", "Not for Other"],
            [r"C:\ACC\Disk1\file3.txt", 140, "Low Risk", "Not for TA", "Not for Other"],
            [r"C:\ACC\Disk2\photo.jpg", 12345, "Low Risk", "Not for TA", "Not for Other"],
            [r"C:\ACC\Disk2\file.psd", 15671, "Moderate Risk", "Not for TA", "Layered image file"],
            [r"C:\ACC\Disk2\file1.psd", 15672, "Moderate Risk", "Not for TA", "Layered image file"],
            [r"C:\ACC\Disk2\file2.psd", 15673, "Moderate Risk", "Not for TA", "Layered image file"],
            [r"C:\ACC\Disk2\file.bak", 700, "High Risk", "Not for TA", "Not for Other"],
            [r"C:\ACC\Disk2\empty.ext", 0, "No Match", "Format", "Not for Other"],
            [r"C:\ACC\Disk2\empty1.ext", 0, "No Match", "Format", "Not for Other"],
            [r"C:\ACC\Disk3\trash\file.bak", 700, "High Risk", "Trash", "Not for Other"],
            [r"C:\ACC\Disk3\trash\empty.ext", 0, "No Match", "Trash", "Not for Other"],
            [r"C:\ACC\Disk3\file.exe", 50, "High Risk", "Format", "Not for Other"],
            [r"C:\ACC\Disk3\file.psd", 1567, "Moderate Risk", "Trash", "Layered image file"],
            [r"C:\ACC\Disk4\file.css", 123, "Low Risk", "Not for TA", "Possible saved web page"],
            [r"C:\ACC\Disk4\file.ics", 14455, "Low Risk", "Not for TA", "NARA Low/Transform"],
            [r"C:\ACC\Disk4\draft\file.css", 125, "Low Risk", "Not for TA", "Possible saved web page"],
            [r"C:\ACC\Disk4\draft\file.ics", 14457, "Low Risk", "Not for TA", "NARA Low/Transform"],
            [r"C:\ACC\Disk4\draft\file.zip", 3399, "Moderate Risk", "Not for TA", "Archive format"],
            [r"C:\ACC\Disk4\draft2\file.css", 145, "Low Risk", "Not for TA", "Possible saved web page"],
            [r"C:\ACC\Disk4\draft2\file.ics", 116000, "Low Risk", "Not for TA", "NARA Low/Transform"],
            [r"C:\ACC\log.txt", 12, "Low Risk", "Not for TA", "Not for Other"]]
    column_names = ["FITS_File_Path", "FITS_Size_KB", "NARA_Risk Level", "Technical_Appraisal", "Other_Risk"]
    df_results = pd.DataFrame(rows, columns=column_names)

    # Runs the media_subtotal() function. Uses the output folder for the accession folder.
    df_media_subtotals = media_subtotal(df_results, accession_folder)

    # Makes a dataframe with the expected values.
    rows = [["Disk1", 3, 0.39, 0, 0, 3, 0, 0, 0],
            ["Disk2", 7, 60.061, 1, 3, 1, 2, 2, 3],
            ["Disk3", 4, 2.317, 2, 1, 0, 1, 1, 1],
            ["Disk4", 7, 148.704, 0, 1, 6, 0, 0, 7]]
    column_names = ["Media", "File Count", "Size (MB)", "NARA High Risk (File Count)",
                    "NARA Moderate Risk (File Count)", "NARA Low Risk (File Count)", "No NARA Match (File Count)",
                    "Technical Appraisal_Format (File Count)", "Other Risk Indicator (File Count)"]
    df_expected = pd.DataFrame(rows, columns=column_names)
    df_expected.set_index("Media")

    # Compares the script output to the expected values.
    compare_dataframes("Media_Subtotals", df_media_subtotals, df_expected)


def test_iteration(repo_path):
    """Tests that the script follows the correct logic based on the contents of the accession folder and
    that the contents are updated correctly. Runs the script 3 times to check all iterations: start from scratch,
    use existing FITS files (updating to match the accession folder), and use existing full risk data csv."""

    # Makes an accession folder with test files organized into 2 disks to use for testing.
    # All subtotals and subsets in the final report will have some information.
    # Formats included: csv, html, plain text, xlsx, zip
    # Variations: duplicate files, empty file, file with multiple identifications (xlsx),
    # file with validation error (html), technical appraisal (empty, trash), other risk (zip)
    accession_folder = fr"{output}\accession"
    os.makedirs(fr"{accession_folder}\disk1\trash")
    with open(r"accession\disk1\trash\trash.txt", "w") as file:
        file.write("Trash Text " * 20000)
    with open(r"accession\disk1\trash\trash1.txt", "w") as file:
        file.write("Trash Text " * 20001)
    with open(r"accession\disk1\trash\trash2.txt", "w") as file:
        file.write("Trash Text " * 20002)
    df_spreadsheet = pd.DataFrame({"C1": ["text"*9000], "C2": ["text"*9000], "C3": ["text"*9000]})
    df_spreadsheet = pd.concat([df_spreadsheet]*1000, ignore_index=True)
    df_spreadsheet.to_csv(r"accession\disk1\data.csv", index=False)
    df_spreadsheet[["C3", "C4", "C5", "C6"]] = "New Text" * 1000
    df_spreadsheet.to_csv(r"accession\disk1\data_update.csv", index=False)
    df_spreadsheet[["C7", "C8", "C9", "C19"]] = "More Text" * 1000
    df_spreadsheet.to_excel(r"accession\disk1\data_update_final.xlsx", index=False)
    with open(r"accession\disk1\duplicate_file.txt", "w") as file:
        file.write("Text" * 900000)
    os.makedirs(fr"{accession_folder}\disk2")
    shutil.make_archive(r"accession\disk2\disk1backup", 'zip', r"accession\disk1")
    with open(r"accession\disk2\duplicate_file.txt", "w") as file:
        file.write("Text" * 900000)
    with open(r"accession\disk2\empty.txt", "w") as file:
        file.write("")
    with open(r"accession\disk2\error.html", "w") as file:
        file.write("<body>This isn't really html</body>")

    # Calculates the path for running the format_analysis.py script.
    script_path = os.path.join(repo_path, "format_analysis.py")

    # Runs the script on the test accession folder and tests if the expected messages were produced.
    # In format_analysis.py, these messages are printed to the terminal for archivist review.
    iteration_one = subprocess.run(f"python {script_path} {accession_folder}", shell=True, stdout=subprocess.PIPE)
    msg = "\r\nGenerating new FITS format identification information.\r\n\r\nGenerating new risk data for the report.\r\n"
    compare_strings("Iteration_Message_1", iteration_one.stdout.decode("utf-8"), msg)

    # Deletes trash folder and adds a missed file to the accession folder to simulate archivist appraisal.
    # Also deletes the full_risk_data.csv so an updated one will be made with the changes.
    shutil.rmtree(r"accession\disk1\trash")
    with open(r"accession\disk2\new.txt", "w") as file:
        file.write("Text"*30000)
    os.remove("accession_full_risk_data.csv")

    # Runs the script again on the test accession folder.
    # It will update the FITS files to match the accession folder and update the three spreadsheet.
    iteration_two = subprocess.run(f"python {script_path} {accession_folder}", shell=True, stdout=subprocess.PIPE)
    msg = "\r\nUpdating the XML files in the FITS folder to match files in the accession folder.\r\n" \
          "This will update fits.csv but currently does not update full_risk_data.csv from a previous script iteration.\r\n" \
          "Delete full_risk_data.csv before the script gets to that step for it to be remade with the new information.\r\n\r\n" \
          "Generating new risk data for the report.\r\n"
    compare_strings("Iteration_Message_2", iteration_two.stdout.decode("utf-8"), msg)

    # Edits the full_risk_data.csv to simulate archivist cleaning up risk matches.
    df_risk = pd.read_csv("accession_full_risk_data.csv")
    df_risk.drop(index=[2, 10, 12, 13, 14], inplace=True)
    df_risk.to_csv("accession_full_risk_data.csv", index=False)

    # Runs the script again on the test accession folder.
    # It will use existing fits.csv and full_risk_data.csv to update format_analysis.xlsx.
    iteration_three = subprocess.run(f"python {script_path} {accession_folder}", shell=True, stdout=subprocess.PIPE)
    msg = "\r\nUpdating the XML files in the FITS folder to match files in the accession folder.\r\n" \
          "This will update fits.csv but currently does not update full_risk_data.csv from a previous script iteration.\r\n" \
          "Delete full_risk_data.csv before the script gets to that step for it to be remade with the new information.\r\n\r\n" \
          "Updating the report using existing risk data.\r\n"
    compare_strings("Iteration_Message_3", iteration_three.stdout.decode("utf-8"), msg)

    # Makes dataframes with the expected values for each tab in format_analysis.xlsx.
    # Does not include the FITS_MD5 column for df with Excel or zip files, which are different each time they are made.
    # Calculates date, which is when the file was generated, with datetime to keep the expected value accurate.
    # Calculates size for df with XLSX and ZIP with os.path because they are different each time they are made.
    today = datetime.date.today().strftime('%Y-%m-%d')

    rows = [["Comma-Separated Values (CSV)", "Low Risk", 2, 20, 212, 96.2],
            ["empty", "Low Risk", 1, 10, 0, 0],
            ["Extensible Markup Language", "Low Risk", 1, 10, 0, 0],
            ["Office Open XML Workbook", "Low Risk", 1, 10, 0.4, 0.2],
            ["Plain text", "Low Risk", 3, 30, 7.3, 3.3],
            ["XLSX", "Low Risk", 1, 10, 0.4, 0.2],
            ["ZIP Format", "Moderate Risk", 1, 10, 0.3, 0.1]]
    column_names = ["FITS_Format_Name", "NARA_Risk Level", "File Count", "File %", "Size (MB)", "Size %"]
    df_format_subtotals_expected = pd.DataFrame(rows, columns=column_names)

    rows = [["Low Risk", 9, 90, 220.1, 99.9], ["Moderate Risk", 1, 10, 0.3, 0.1]]
    column_names = ["NARA_Risk Level", "File Count", "File %", "Size (MB)", "Size %"]
    df_nara_risk_subtotals_expected = pd.DataFrame(rows, columns=column_names)

    rows = [["Format", "empty", 1, 10, 0, 0]]
    column_names = ["Technical_Appraisal", "FITS_Format_Name", "File Count", "File %", "Size (MB)", "Size %"]
    df_tech_appraisal_subtotals_expected = pd.DataFrame(rows, columns=column_names)

    rows = [["Archive format", "ZIP Format", 1, 10, 0.3, 0.1]]
    column_names = ["Other_Risk", "FITS_Format_Name", "File Count", "File %", "Size (MB)", "Size %"]
    df_other_risk_subtotals_expected = pd.DataFrame(rows, columns=column_names)

    rows = [["disk1", 5, 216.4, 0, 0, 5, 0, 0, 0], ["disk2", 5, 4, 0, 1, 4, 0, 1, 1]]
    column_names = ["Media", "File Count", "Size (MB)", "NARA High Risk (File Count)", "NARA Moderate Risk (File Count)",
                    "NARA Low Risk (File Count)", "No NARA Match (File Count)", "Technical Appraisal_Format (File Count)",
                    "Other Risk Indicator (File Count)"]
    df_media_subtotals_expected = pd.DataFrame(rows, columns=column_names)

    rows = [[fr"{output}\accession\disk2\disk1backup.zip", "ZIP Format", 2, False, today,
             round(os.path.getsize(r"accession\disk2\disk1backup.zip")/1000, 3), "Moderate Risk",
             "Retain but extract files from the container", "PRONOM", "Not for TA", "Archive format"]]
    column_names = ["FITS_File_Path", "FITS_Format_Name", "FITS_Format_Version", "FITS_Multiple_IDs",
                    "FITS_Date_Last_Modified", "FITS_Size_KB", "NARA_Risk Level",
                    "NARA_Proposed Preservation Plan", "NARA_Match_Type", "Technical_Appraisal", "Other_Risk"]
    df_nara_risk_expected = pd.DataFrame(rows, columns=column_names)

    rows = [[fr"{output}\accession\disk2\empty.txt", "empty", np.NaN, "file utility version 5.03",
             False, 0, np.NaN, "Low Risk", "Retain", "File Extension", "Format", "Not for Other"]]
    column_names = ["FITS_File_Path", "FITS_Format_Name", "FITS_Format_Version", "FITS_Identifying_Tool(s)",
                    "FITS_Multiple_IDs", "FITS_Size_KB", "FITS_Creating_Application", "NARA_Risk Level",
                    "NARA_Proposed Preservation Plan", "NARA_Match_Type", "Technical_Appraisal", "Other_Risk"]
    df_for_technical_appraisal_expected = pd.DataFrame(rows, columns=column_names)

    rows = [[fr"{output}\accession\disk2\disk1backup.zip", "ZIP Format", 2,
             "Droid version 6.4; file utility version 5.03; Exiftool version 11.54; ffident version 0.2; Tika version 1.21",
             False, round(os.path.getsize(r"accession\disk2\disk1backup.zip")/1000, 3), "Moderate Risk",
             "Retain but extract files from the container", "PRONOM", "Not for TA", "Archive format"]]
    column_names = ["FITS_File_Path", "FITS_Format_Name", "FITS_Format_Version", "FITS_Identifying_Tool(s)",
                    "FITS_Multiple_IDs", "FITS_Size_KB", "NARA_Risk Level", "NARA_Proposed Preservation Plan",
                    "NARA_Match_Type", "Technical_Appraisal", "Other_Risk"]
    df_other_risks_expected = pd.DataFrame(rows, columns=column_names)

    rows = [[fr"{output}\accession\disk1\data_update_final.xlsx", "XLSX", np.NaN, np.NaN,
             "Exiftool version 11.54", True, today, round(os.path.getsize(r"accession\disk1\data_update_final.xlsx")/1000, 3),
             np.NaN, "Low Risk", "Retain", "File Extension", "Not for TA", "Not for Other"],
            [fr"{output}\accession\disk1\data_update_final.xlsx", "Office Open XML Workbook", np.NaN, np.NaN,
             "Tika version 1.21", True, today, round(os.path.getsize(r"accession\disk1\data_update_final.xlsx")/1000, 3),
             np.NaN, "Low Risk", "Retain", "File Extension", "Not for TA", "Not for Other"]]
    column_names = ["FITS_File_Path", "FITS_Format_Name", "FITS_Format_Version", "FITS_PUID", "FITS_Identifying_Tool(s)",
                    "FITS_Multiple_IDs", "FITS_Date_Last_Modified", "FITS_Size_KB", "FITS_Creating_Application",
                    "NARA_Risk Level", "NARA_Proposed Preservation Plan", "NARA_Match_Type", "Technical_Appraisal", "Other_Risk"]
    df_multiple_formats_expected = pd.DataFrame(rows, columns=column_names)

    rows = [[fr"{output}\accession\disk2\duplicate_file.txt", 3600, "fe6fb9d365e141e326adfaea99c87fa6"],
            [fr"{output}\accession\disk1\duplicate_file.txt", 3600, "fe6fb9d365e141e326adfaea99c87fa6"]]
    column_names = ["FITS_File_Path", "FITS_Size_KB", "FITS_MD5"]
    df_duplicates_expected = pd.DataFrame(rows, columns=column_names)

    rows = [[fr"{output}\accession\disk2\error.html", "Extensible Markup Language", 1, np.NaN, "Jhove version 1.20.1", False,
             today, 0.035, "e080b3394eaeba6b118ed15453e49a34", np.NaN, True, True, "Not able to determine type of end of line severity=info",
             "Low Risk", "Retain", "Format Name", "Not for TA", "Not for Other"]]
    column_names = ["FITS_File_Path", "FITS_Format_Name", "FITS_Format_Version", "FITS_PUID", "FITS_Identifying_Tool(s)",
                    "FITS_Multiple_IDs", "FITS_Date_Last_Modified", "FITS_Size_KB", "FITS_MD5", "FITS_Creating_Application",
                    "FITS_Valid", "FITS_Well-Formed", "FITS_Status_Message", "NARA_Risk Level",
                    "NARA_Proposed Preservation Plan", "NARA_Match_Type", "Technical_Appraisal", "Other_Risk"]
    df_validation_expected = pd.DataFrame(rows, columns=column_names)

    # Makes a dataframe from each tab in format_analysis.xlsx.
    # Removing FITS_MD5 for df with Excel or zip files, since those have a different MD5 each time they are made.
    # Rounding file size and percentage for subtotals with Excel or zip files, since they vary in size each time.
    # For subsets, used Python to calculate individual file sizes to keep the number accurate.
    xlsx = pd.ExcelFile("accession_format-analysis.xlsx")
    df_format_subtotals = pd.read_excel(xlsx, "Format Subtotals")
    df_format_subtotals[["Size (MB)", "Size %"]] = df_format_subtotals[["Size (MB)", "Size %"]].round(1)
    df_nara_risk_subtotals = pd.read_excel(xlsx, "NARA Risk Subtotals")
    df_nara_risk_subtotals[["Size (MB)", "Size %"]] = df_nara_risk_subtotals[["Size (MB)", "Size %"]].round(1)
    df_tech_appraisal_subtotals = pd.read_excel(xlsx, "Tech Appraisal Subtotals")
    df_other_risk_subtotals = pd.read_excel(xlsx, "Other Risk Subtotals")
    df_other_risk_subtotals[["Size (MB)", "Size %"]] = df_other_risk_subtotals[["Size (MB)", "Size %"]].round(1)
    df_media_subtotals = pd.read_excel(xlsx, "Media Subtotals")
    df_media_subtotals["Size (MB)"] = df_media_subtotals["Size (MB)"].round(1)
    df_nara_risk = pd.read_excel(xlsx, "NARA Risk")
    df_nara_risk = df_nara_risk.drop("FITS_MD5", axis=1)
    df_tech_appraisal = pd.read_excel(xlsx, "For Technical Appraisal")
    df_other_risk = pd.read_excel(xlsx, "Other Risks")
    df_multiple = pd.read_excel(xlsx, "Multiple Formats")
    df_multiple = df_multiple.drop("FITS_MD5", axis=1)
    df_duplicates = pd.read_excel(xlsx, "Duplicates")
    df_validation = pd.read_excel(xlsx, "Validation")
    xlsx.close()

    # Compares the expected values to the actual script values.
    compare_dataframes("Iteration_Subtotals_Format", df_format_subtotals, df_format_subtotals_expected)
    compare_dataframes("Iteration_Subtotals_Tech_Appraisal", df_tech_appraisal_subtotals, df_tech_appraisal_subtotals_expected)
    compare_dataframes("Iteration_Subtotals_NARA_Risk", df_nara_risk_subtotals, df_nara_risk_subtotals_expected)
    compare_dataframes("Iteration_Subtotals_Other_Risk", df_other_risk_subtotals, df_other_risk_subtotals_expected)
    compare_dataframes("Iteration_Subtotals_Media", df_media_subtotals, df_media_subtotals_expected)
    compare_dataframes("Iteration_Subset_NARA_Risk", df_nara_risk, df_nara_risk_expected)
    compare_dataframes("Iteration_Subset_Tech_Appraisal", df_tech_appraisal, df_for_technical_appraisal_expected)
    compare_dataframes("Iteration_Subset_Other_Risk", df_other_risk, df_other_risks_expected)
    compare_dataframes("Iteration_Subset_Multiple_IDs", df_multiple, df_multiple_formats_expected)
    compare_dataframes("Iteration_Subset_Duplicates", df_duplicates, df_duplicates_expected)
    compare_dataframes("Iteration_Subset_Validation", df_validation, df_validation_expected)

    # Deletes the test files.
    shutil.rmtree("accession")
    shutil.rmtree("accession_FITS")
    os.remove("accession_fits.csv")
    os.remove("accession_format-analysis.xlsx")
    os.remove("accession_full_risk_data.csv")


# Makes the output directory (the only script argument) the current directory for easier saving.
# If the argument is missing or not a valid directory, ends the script.
try:
    output = sys.argv[1]
    os.chdir(output)
except (IndexError, FileNotFoundError):
    print("\nThe required script argument (output folder) is missing or incorrect.")
    sys.exit()

# Saves the path to the GitHub repo, which is used by a few of the tests.
# sys.argv[0] is the path to format_analysis_tests.py
repo = os.path.dirname(sys.argv[0])

# Makes counters for the number of passed and failed tests to summarize the results at the end.
PASSED_TESTS = 0
FAILED_TESTS = 0

# Calls each of the test functions, which either test a function in format_analysis.py or
# one of the analysis components, such as the duplicates subset or NARA risk subtotal.
# A summary of the test result is printed to the terminal and failed tests are saved to the output folder.

test_argument(repo)
test_check_configuration_function(repo)

test_csv_to_dataframe_function()
test_csv_to_dataframe_function_errors()
test_make_fits()
test_fits_class_error()
test_update_fits_function()
test_make_fits_csv()

test_match_nara_risk_function()
test_match_technical_appraisal_function()
test_match_other_risk_function()
test_deduplicating_results()

test_nara_risk_subset()
test_multiple_subset()
test_validation_subset()
test_tech_appraisal_subset()
test_other_risk_subset()
test_duplicates_subset()
test_empty_subset()

test_format_subtotal()
test_nara_risk_subtotal()
test_technical_appraisal_subtotal()
test_technical_appraisal_subtotal_empty()
test_other_risk_subtotal()
test_other_risk_subtotal_empty()
test_media_subtotal_function()

test_iteration(repo)

print("\nThe testing script is complete. Results:")
if FAILED_TESTS == 0:
    print(f"\t* All {PASSED_TESTS} tests passed.")
else:
    print(f"\t* {PASSED_TESTS} passed.")
    print(f"\t* {FAILED_TESTS} failed. See output folder for logs of each failed test.")
