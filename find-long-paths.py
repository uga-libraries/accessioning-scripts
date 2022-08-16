"""Long File Path Finder and Change Log Creator

This script identifies and creates a CSV log of all the files in an accession with
file paths that exceed the Windows maximum of 260 characters. These long file paths
need to be identified and shortened prior to bagging the accession, otherwise they
will raise permissions errors from bagit.py.

The CSV can then be used as a change log to document the new shortened paths.

Script usage: python /path/to/script /path/to/accession/directory

"""

import os
import sys
import csv

acc_dir = sys.argv[1]
header = ['Orig_path', 'Orig_path_len', 'New_path', 'Date_changed']

#Open a CSV to log all of the file paths that exceed the maximum length
with open("file-path-changes.csv", "w", encoding="utf-8", newline="") as log:
    writer = csv.writer(log)
    writer.writerow(header)

    #Iterate through the accession directory 
    for root, dirs, files in os.walk(acc_dir):
        for file in files:
            fullpath = str(os.path.join(root, file))
            
            #Log the path and character length of files exceeding 260 characters
            data = [fullpath, len(fullpath)]
            if len(fullpath) > 260:
                writer.writerow(data)
