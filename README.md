# accessioning-scripts

Scripts used for accessioning born-digital archives at the UGA Special Collections Libraries.


## find-long-paths.py

Script usage: `python /path/to/script /path/to/accession/directory`

This script identifies and creates a CSV log of all the files in an accession with file paths that exceed the Windows maximum of 260 characters. 
These long file paths need to be identified and shortened prior to bagging the accession, otherwise they will raise permissions errors from bagit.py. 
The CSV can then be used as a change log to document the new shortened paths.


## format-analysis.py

Script usage: `python path/to/format-analysis.py path/to/accession_folder`

Before running the script, download [NARA's Preservation Action Plans CSV](https://github.com/usnationalarchives/digital-preservation/tree/master/Digital_Preservation_Plan_Spreadsheet) 
and create a file named configuration.py from the configuration_template.py in the accessioning-scripts repo.

This script extracts technical metadata from files in the accession folder, compares it to multiple risk criteria, 
and produces a summary report to use for appraisal and evaluating an accession's complexity.

The script is designed to run repeatedly as the archivist makes changes based on the information,
such as deleting unwanted files or editing the risk assigned to each file. 
The script adjusts how it works based on the files in the parent directory of the accession folder, 
reusing information from previous script iterations where it will save time or allow manual updates. 

1. If there are no script-generated files present, the script creates FITS XML for every file in the accession folder, 
   and the FITS summary spreadsheet, risk spreadsheet and analysis spreadsheet.
   

2. If there is a folder of FITS XML, the script updates the FITS XML and the FITS summary spreadsheet to match the files in the accession folder, 
   creates the risk spreadsheet (if one is not already present), and makes the analysis spreadsheet.


3. If there is a risk spreadsheet, the script uses it to make the analysis spreadsheet. 
   The risk spreadsheet is not automatically updated based on changes to the FITS summary spreadsheet. 
   The risk spreadsheet needs to be deleted if there are changes made to the files in the accession folder before running the script again 
   so that the risk spreadsheet can be updated with the current formats.


## format_analysis_tests.py

Script usage: `python path/to/format_analysis_tests.py path/to/output_folder`

For any tests that do not import the function from format_analysis_functions.py, sync the code before running the test. 
If the input for any function or analysis changes, edit the test input and expected results.
To test a FITS class error, save the fits.bat or fits.sh file to a different letter directory than the output folder and
update the fits_path variable in test_fits_class_error().

This script tests each function and analysis component (each subset and subtotal) in the format_analysis.py script. 
Each test creates simplified input, runs the code, and compares it to the expected output.
Tests include all known input data variations and function error handling.
Results for failed tests are saved to a directory specified with the script argument.
There are 49 tests organized into 28 functions.


## technical-appraisal-logs.py

Script usage: `python /path/to/script /path/to/accession/directory [compare]`

This script requires an installation of 'pandas' in your Python environment.

This script generates a CSV manifest of all the digital files received in an accession. 
It also identifies file paths that may break other scripts and saves those paths to a 
separate log for review.

Using the "compare" argument compares the initial manifest to the files left in the 
accession after technical appraisal and generates an additional CSV log of any files 
that were deleted in the process.
