import csv
import xml
from xml.etree import ElementTree
import json


def extract_div(html_file):
    """
    Receives a html file and creates a list of elements with the content of the
    page
    """
    # List to store the content of the page
    csv_list_all = []
    # Extract all the text in the page, ignoring tags and hierarchy
    for i, val in enumerate(xml.etree.ElementTree.fromstring(html_file).itertext()):
        val.replace('\n', ' ')
        if val != '\n' and not val.isspace():
            csv_list_all.append(val)
    # Returns a list of list, with all the content
    return csv_list_all


def write_file(list_content, output_name, to_csv):
    """
    Receives a list of content and the name of the output file, saves the file
    """
    if to_csv:
        output_name += '.csv'
        with open(output_name, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(list_content)
    else:
        with open(output_name, "a", newline="") as f:
            json.dump(list_content, f)


def div_to_file(html_file_path, output_file='output', to_csv=False):
    """
    Receives an html file path, converts the html to csv and saves the file on
    disk.

    :param html_file_path : str (A file-like object, or a raw string containing
    HTML.)
    :param output_file : str, optional (Name and path of the output file,
    default is output)
    :param to_csv : bool, default False (Whether the output file is csv or json)
    """
    # Extract the content
    list_content = extract_div(html_file_path)
    # Saves the content in a file
    write_file(list_content, output_file, to_csv)
