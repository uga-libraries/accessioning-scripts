"""File Manifest and Deletion Log Generator

This script generates a CSV manifest of all the digital files received in an accession,
including the file name, relevant dates, and MD5 hash. It also identifies file paths 
that may break other scripts and saves those paths to a separate log for review.

Using the "compare" argument compares the initial manifest to the files left in the 
accession after technical appraisal and generates an additional CSV log of any files 
that were deleted in the process. The script can be run multiple times with this 
argument and any additional deletions will be added to the existing log.

This script requires an installation of 'pandas' in your Python environment.

Script usage: python /path/to/script /path/to/accession/directory [compare]
"""

import os
import csv
import sys
import hashlib
import pandas as pd
from datetime import datetime

dir_to_log = sys.argv[1]
date = datetime.now().strftime("%Y%m%d")
header = ['File', 'SizeKB', 'DateCreated', 'DateModified', 'MD5', 'Notes']

def scan_full_dir(dirpath):
    """Scans a directory tree and gets os.DirEntry objects for all its files and subdirectories
    
    Adapted from code by Ben Hoyt on Stackoverflow: https://stackoverflow.com/a/33135143 

    Parameters
    -----------
    dirpath : str
        The file path of the directory to scan
    
    Returns
    -----------
    os.DirEntry object
        Inidividual os.DirEntry objects for each file or directory in the tree, as they are generated
        Description of os.DirEntry attributes: https://docs.python.org/3/library/os.html#os.DirEntry
    """
    not_found = []
    for entry in os.scandir(dirpath):
        try: 
            if entry.is_dir():
                yield from scan_full_dir(entry.path)
            else:
                yield entry
        except FileNotFoundError:
            print (entry)
            not_found.append(entry)
    
    for x in not_found:
        ext_path = (f'\\\\?\\{x.path}')
        if x.is_dir():
            yield from scan_full_dir(ext_path)
        else:
            yield ext_path

def find_init_manifest(dirpath):
    """Scans a directory and identifies a CSV file manifest created by this script
    
    Parameters
    -----------
    dirpath : str
        The file path of the directory to scan

    Returns
    -----------
    string
        The file path of the CSV file manifest in the directory
    """

    with os.scandir(dirpath) as d:
        for entry in d:
            fname = str(entry)
            if 'initialmanifest' in fname:
                init_manifest = entry.path
                return str(init_manifest)

def find_deletion_log(dirpath):
    """Scans a directory and identifies a CSV deletion log created by this script
    
    Parameters
    -----------
    dirpath : str
        The file path of the directory to scan

    Returns
    -----------
    string
        The file path of the CSV deletion log in the directory
    """

    with os.scandir(dirpath) as d:
        for entry in d:
            fname = str(entry)
            if 'deletionlog' in fname:
                del_log = entry.path
                return str(del_log)

def get_file_info(entry):
    """Aggregates relevant attributes from the os.DirEntry object for a file and generates its MD5 hash
        Description of the chained stat() method: https://docs.python.org/3/library/os.html#os.DirEntry.stat
    
    Parameters
    -----------
    entry : os.DirEntry object
        The object yielded by the scandir() iterator for the file

    Returns
    -----------
    list
        A list of the file's relevant attributes in str format
    """
    data = []

    path = entry.path
    size = entry.stat().st_size
    sizeKB = round((int(size)/1000), 1)
    modified = entry.stat().st_mtime
    date_modified = datetime.fromtimestamp(modified).strftime('%Y-%m-%d')
    created = entry.stat().st_ctime
    date_created = datetime.fromtimestamp(created).strftime('%Y-%m-%d')

    data.extend([path, sizeKB, date_modified, date_created])
    return data

if __name__ == "__main__":

    log_docs = ['deletionlog_', 'initialmanifest_', 'filestoreview_']
    
    # Check for a "compare" arugment provided by the user
    try:
        if sys.argv[2].lower() == "compare":
            start_compare = sys.argv[2]
        else:
            start_compare = None
            print(f'\nERROR: "{sys.argv[2]}" is an unrecognized argument\n\nScript usage: python /path/to/script /path/to/accession/directory [compare]')
            quit()

    except IndexError: 
        start_compare = None
    
    # If no "compare" argument, check for an existing manifest
    if start_compare == None: 
        man = find_init_manifest(dir_to_log)

        # Alert the user if one is found with the same date and give them the option to cancel the process and prevent overwriting
        if man:
            if date in man:
                todaysfile = man.rsplit('\\', 1)[-1]
                check = input(f'\nA file called "{todaysfile}" already exists in this location. Do you wish to overwrite it? Type Y or N: ')
                if check.lower() in ['n', 'no']:
                    print(f'\nProcess cancelled. \n\nTo create a log of deleted files, run this script again with the "compare" parameter: python /path/to/script /path/to/accession/directory compare')
                    quit()
                if check.lower() in ['y', 'yes']:
                    print('\nFile manifest will be saved to the accession folder. Working...')

        # Create the manifest CSV and a log of files to review
        with open(f'{dir_to_log}\\initialmanifest_{date}.csv', "w", encoding="utf-8", newline='') as manifest, open(f'{dir_to_log}\\filestoreview_{date}.csv', "w", encoding="utf-8", newline='') as review_log:
            wr_initman = csv.writer(manifest)
            wr_revlog = csv.writer(review_log)
            wr_initman.writerow(header)
            wr_revlog.writerow(header)

            # Scan through the full directory tree and write the relevant file information to the manifest
            
            for entry in scan_full_dir(dir_to_log):
                try:
                    data = get_file_info(entry)

                    # Skip over log documents
                    if any(x in data[0] for x in log_docs):
                        continue
                    else:
                        # Generate MD5 checksum for each file in initial manifest
                        path = data[0]
                        with open(path, 'rb') as f:
                            file_data = f.read()
                            md5 = hashlib.md5(file_data).hexdigest()
                            md5_generated = md5.upper()
                            data.append(md5_generated)
                            wr_initman.writerow(data)
                    # Look at the file path and check for any problematic characters
                    filepath = data[0]
                    path = str(filepath)

                    tempfiles = ['~', '._']
                    probchars = ['&', '$', '*', '?']
                    smartquotes = ['“', '”', '’']

                    # If the path contains any of these substrings, write the relevant file info to the review log and include the reason
                    if any (t in path for t in tempfiles):
                        data.append("Potential temp file")
                        wr_revlog.writerow(data)
                    if any (c in path for c in probchars):
                        data.append("Path contains special characters")
                        wr_revlog.writerow(data)
                    if any (q in path for q in smartquotes):
                        data.append("Path contains smart quotes or apostrophes")
                        wr_revlog.writerow(data)

                    # Check the path length to see if it exceeds the Windows max path length
                    path.replace('\\', '\\\\')
                    if len(path) > 260:
                        data.append("Path exceeds 260 characters")
                        wr_revlog.writerow(data)
                except FileNotFoundError:
                    data = ["Path not found", None, None, None, "FileNotFoundError"]
                    wr_initman.writerow(data)
                    continue
    
    # If there's a "compare" argument, scan the directory and put current file information into a new dataframe
    if start_compare == "compare":
        new_df = pd.DataFrame(columns=header[:-1])
        for entry in scan_full_dir(dir_to_log):
            data = get_file_info(entry)

            # Skip over log docs
            if any(x in data[0] for x in log_docs):
                    continue
            else:
                new_df.loc[len(new_df)] = data

        print('\nDeletion log will be saved to the accession folder. Working...')

        # Find the initial file manifest and read it to a pandas dataframe
        man_df = pd.DataFrame(columns = header)
        man = find_init_manifest(dir_to_log)
        df = pd.read_csv(man)
        man_df = pd.concat([man_df, df], axis=0)

        # Concatenate the two dataframes and exclude logs
        deleted = pd.concat([man_df, new_df], ignore_index=True)
        deleted[~deleted['File'].str.contains('|'.join(log_docs))]
        
        # Compare the file name and parent folder from the file paths in each dataframe to identify and drop any duplicates
        deleted['FName'] = deleted['File'].astype(str).str.split('\\', -2).str[-1].str.strip()
        deleted = deleted.drop_duplicates('FName', keep=False)

        # Add a "Date Deleted" column with today's date
        deleted.drop(['DateModified'], axis=1, inplace=True)
        deleted.insert(3, 'DateDeleted', datetime.now().strftime("%Y-%m-%d"))
        deleted.drop(['FName'], axis=1, inplace=True)

        # Check to see if a deletion log already exists
        del_log = find_deletion_log(dir_to_log)
        if del_log:
            logfile = del_log.rsplit('\\', 1)[-1]
            print(f'\nA file called "{logfile}" already exists in this location. If any additional deletions are found, they will be added to this file.')
            del_df = pd.read_csv(del_log)

            # Concatenate the two dataframes and exlude logs
            new_deletions = pd.concat([deleted,del_df], ignore_index=True)
            new_deletions[~new_deletions['File'].str.contains('|'.join(log_docs))]

            # Compare the file name and parent folder from the file paths in each dataframe to identify and drop any duplicates
            new_deletions['FName'] = new_deletions['File'].astype(str).str.split('\\', -2).str[-1].str.strip()
            new_deletions = new_deletions.drop_duplicates('FName', keep=False)
            new_deletions['DateDeleted'] = datetime.now().strftime("%Y-%m-%d")
            new_deletions.drop(['FName'], axis=1, inplace=True)

            # Append new deletion information to the existing CSV
            new_deletions.to_csv(del_log, mode='a', header=False, index=False)

            # Update CSV file name with today's date
            split_fn = del_log.rsplit('_', 1)[0]
            updated_fn = (f'{split_fn}_{date}.csv')
            os.rename(del_log, updated_fn)
        
        # If no existing deletion log, write the dataframe of deleted files to a new CSV
        else:
            deleted.to_csv(f'{dir_to_log}\\deletionlog_{date}.csv', encoding="utf-8", index=False)

    print(f'\nScript is finished running.')