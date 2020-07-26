import pandas as pd
import os
from bs4 import BeautifulSoup
import csv
import xml
import re
import errno

def extrac_div(html_file):
    '''
    Receives a html file and creates a list of elements with the content of the
    page
    '''
    # List to store the content of the page
    csv_list_all = []
    # Extract all the text in the page, ignoring tags and hierarchy
    for i, val in enumerate(xml.etree.ElementTree.fromstring(html_file).itertext()):
        val.replace('\n', ' ')
        if val != '\n' and not val.isspace():
            csv_list_all.append(val)

    # Returns a list of list, with all the content
    return csv_list_all


def write_csv(csv_list, csv_output_name):
    '''
    Receives a list of content and the name of the csv file, saves the csv file
    '''
    with open(csv_output_name, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(csv_list)


def div_to_csv(html_file_path, is_string=False, output_file='output.csv'):
    '''
    Receives an html file path, converts the html to csv and saves the file on
    disk.

    :param html_file_path : str (A file-like object, or a raw string containing
    HTML.)
    :param is_string : bool, default False (Wheter the html file is passed as a
string or as the path to the file)
    :param output_file : str, optional (Name and path of the output csv file,
    default is output.csv)
    '''
    # Check if html file exists
    if (os.path.isfile(html_file_path)) or is_string:
        # Extract the content
        csv_list_all = extrac_div(html_file_path)
        # Saves the content in a csv file
        write_csv(csv_list_all, output_file)

    else:
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT),
        html_file_path)
