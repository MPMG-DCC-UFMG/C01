import pandas as pd
import os
from bs4 import BeautifulSoup
import csv
import xml
import re
import errno


def clean_html(html_file, isString):
    '''
    Receives the html file and removes unecessery parts, as header, footer, etc.
    '''

    # List of elements that are going to be removed from the html
    remove_list = ["head", "header", "footer" , "polygon", "path", "script",
                    "symbol", "meta", "link", "title", "style", "nav", "table",
                    "form"]
    remove_class = ["sidebar-inner","breadcrumb", "share", "navegacao",
                    "skiptranslate", "goog-te-spinner-pos","social-list",
                    "social-icon", "copyright", "id_assist_frame",
                    "fbc-badge-tooltip"]
    remove_id = ["boxes", "mySidenav", "chat-panel"]

    # Check if the html_file is a string with the page or a path to the file
    if isString:
        f = html_file
        soup = BeautifulSoup(f, 'html.parser')
    else:
        soup = ""
        f = open(html_file, encoding="ISO-8859-1")
        soup = BeautifulSoup(f, 'html.parser')
        f.close()


    # Remove any tag present in remove_list
    for tag in soup.find_all():
        if tag.name.lower() in remove_list:
            tag.extract()
    # Remove any div with the class in remove_class
    for div in soup.find_all("div", {'class':remove_class}):
        div.extract()
    # Remove any div with the id in remove_id
    for div in soup.find_all("div", {'id':remove_id}):
        div.extract()

    html_file = str(soup)



    return html_file

def fix_links(html_file):
    '''
    Receives the html file and return the same file with the value of the links
    as the text of the links
    '''
    f = html_file
    soup = BeautifulSoup(f, 'html.parser')

    for a in soup.find_all('a', href=True):
        if "http" in a['href']:
            a.string = a['href']

    html_file = str(soup)



    return html_file

def extrac_div(html_file):
    '''
    Receives a html file and creates a list of elements with the content of the
    page
    '''
    # List to store the content of the page
    csv_list_all = []
    # Extract all the text in the page, ignoring tags and hierarchy
    for i, val in enumerate(xml.etree.ElementTree.fromstring(html_file).itertext()):
        val.replace('\n',' ')
        if val != '\n' and not val.isspace():
            csv_list_all.append(val)

    # Returns a list of list, with all the content
    return csv_list_all


def write_csv(csv_list, csv_output_name):
    '''
    Receives a list of content and the name of the csv file, saves the csv file
    '''
    with open(csv_output_name, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(csv_list)


def html_to_csv(html_file_path, is_string=False, output_file='output.csv'):
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

    # # Check if html file exists
    # if (os.path.isfile(html_file)):
    #     # Create output file based on the input file name
    #     output_file = html_file.split('.html')[0]+".csv"
    #     # set isString to false, since the HTML is in a html_file
    #     isString = False
    # # Ckeck if the html was passed as string
    # elif (' ' in html_file) and (len(html_file)>2):
    #     # If a name for the output is not given, the file is set to output.csv
    #     if output_path is None:
    #         output_file = "output.csv"
    #     # set isString to true, since the HTML is in a string
    #     isString = True
    # # If the file does not exist and is not a raw string
    # else:
    #     raise Exception('The given HMTL file does not exist.')
    #
    # # Clean the html file
    # html_file = clean_html(html_file,isString)
    # # Fix the links in the file
    # html_file = fix_links(html_file)
    # # Extract the content
    # csv_list_all = extrac_div(html_file)
    # # Saves the content in a csv file
    # write_csv(csv_list_all, output_file)

    # Check if html file exists
    if (os.path.isfile(html_file_path)) or is_string:

        # Clean the html file
        html_file = clean_html(html_file_path,is_string)
        # Fix the links in the file
        html_file = fix_links(html_file)
        # Extract the content
        csv_list_all = extrac_div(html_file)
        # Saves the content in a csv file
        write_csv(csv_list_all, output_file)

    else:
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT),
        html_file_path)
