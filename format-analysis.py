"""
Purpose: generate format identification and create reports to support:
    1. Appraisal (technical and content based)
    2. Assigning processing tiers
    3. Identify risks to address immediately.
"""
import os
import subprocess
import sys
import xml.etree.ElementTree as ET

import configuration as c


def fits_to_csv(fits_xml):
    """Extracts desired fields from a FITS XML file, reformats when necessary,
    and saves each format identification as a separate row in a CSV. Returns nothing."""

    def get_text(parent, element):
        """Returns a single value, regardless of if the element is missing, appears once, or repeats.
        For a missing element (some are optional), returns None.
        For an element that appears once, returns a string with the value of the text.
        For an element that repeats, returns a string with the text of every instance separated by semicolons.

        The parent element does not need to be a child of root.
        This function cannot be used if the desired value is an attribute instead of element text."""

        # If one or more instances of the element are present, returns the text.
        # For multiple instances, puts a semicolon between the text for each instance.
        try:
            value = ""
            value_list = parent.findall(f"fits:{element}", ns)
            for item in value_list:
                if value == "":
                    value += item.text
                else:
                    value += f"; {item.text}"
            return value
        # If the element is missing, item.text raises an AttributeError.
        except AttributeError:
            return None

    # Read the fits.xml file.
    tree = ET.parse(fits_xml)
    root = tree.getroot()

    # FITS namespace. All elements in the fits.xml are part of this namespace.
    ns = {"fits": "http://hul.harvard.edu/ois/xml/ns/fits/fits_output"}

    # Get the data from the desired elements.
    # Selects the parent element from root first to have consistent paths regardless of XML hierarchy.
    for identity in root.find("fits:identification", ns):
        format_name = identity.get("format")
        mimetype = identity.get("mimetype")
        format_version = get_text(identity, "version")
        puid = get_text(identity, "externalIdentifier[@type='puid']")

        # For each tool, need to combine attributes with the name and version.
        tools = ""
        tools_list = identity.findall("fits:tool", ns)
        for tool in tools_list:
            tool_name = f"{tool.get('toolname')} version {tool.get('toolversion')}"
            if tools == "":
                tools += tool_name
            else:
                tools += f"; {tool_name}"

    for fileinfo in root.find("fits:fileinfo", ns):
        path = get_text(fileinfo, "filepath")
        name = get_text(fileinfo, "filename")
        date = get_text(fileinfo, "fslastmodified")
        size = get_text(fileinfo, "size")
        md5 = get_text(fileinfo, "md5checksum")
        creating = get_text(fileinfo, "creatingApplicationName")

    for filestatus in root.find("fits:filestatus", ns):
        valid = get_text(filestatus, "valid")
        well_formed = get_text(filestatus, "well-formed")
        message = get_text(filestatus, "message")


# Get accession folder path from script argument, verify it is correct, and make it the current directory.
# If there is an error, ends the script.
try:
    accession_folder = sys.argv[1]
    os.chdir(accession_folder)
except IndexError:
    print("\nThe required script argument is missing.")
    print("Please run the script again.")
    print("Script usage: python path/format-analysis.py path/accession_folder")
    sys.exit()
except FileNotFoundError:
    print(f"\nThe provided accession folder '{accession_folder}' is not a valid directory.")
    print("Please run the script again.")
    print("Script usage: python path/format-analysis.py path/accession_folder")
    sys.exit()

# Calculates the accession number, which is the name of the last folder in the accession_folder path.
accession_number = os.path.basename(accession_folder)

# Makes a folder for format identification information in the parent directory of the accession folder.
# If this folder already exists, prints an error and ends the script.
try:
    os.mkdir(f"{accession_folder}_FITS")
except FileExistsError:
    print(f"There is already FITS data for accession {accession_folder}.")
    print(f"Delete or move the '{accession_folder}_FITS' folder and run the script again.")
    sys.exit()

# Generates the format identification information for the accession using FITS
subprocess.run(f'"{c.FITS}" -r -i "{accession_folder}" -o "{f"{accession_folder}_FITS"}"', shell=True)

# Extract select format information for each file, with some data reformatting (PRONOM URL, date, size unit),
# and save to a CSV.
for fits_xml in os.listdir(f"{accession_folder}_FITS"):
    print(f"\nReading {fits_xml}")
    fits_to_csv(f"{accession_folder}_FITS/{fits_xml}")

# Add additional information (file extension, parent folder).

# Add risk information.

# Summarize: by format identification.
# Summarize: by risk.
# Summarize: by parent.

# Make subsets based on different risk factors.

# Save reports.
