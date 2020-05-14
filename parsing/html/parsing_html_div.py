import pandas as pd
import os
from bs4 import BeautifulSoup
import csv


def clean_html(html_file, isString):
    '''
    Receives the html file and removes unecessery parts, as header, footer, etc.
    '''

    # List of elements that are going to be removed from the html
    remove_list = ["head", "header", "footer" , "polygon", "path", "script", "symbol"]

    # Check if the html_file is a string with the page or a path to the file
    if not isString:
        soup = ""
        f = open(html_file, encoding="ISO-8859-1")
        soup = BeautifulSoup(f, 'html.parser')
        f.close()
    if isString:
        f = html_file
        soup = BeautifulSoup(f, 'html.parser')

    for tag in soup.find_all():
        if tag.name.lower() in remove_list:
            tag.extract()

    html_file = str(soup)

    return html_file

def fix_links(html_file):
    '''
    Receives the html file and return the same file with the value of the links as the text of the links
    '''
    f = html_file
    soup = BeautifulSoup(f, 'html.parser')

    for a in soup.find_all('a', href=True):
        a.string = a['href']

    html_file = str(soup)

    return html_file

def extrac_div(html_file):
    '''
    Receives a html file and creates a list of elements with the content of the page
    '''

    # Only elements in this list are going to be saved
    keep_list = ["h1", "h2", "h3" , "p", "path", "script", "symbol"]

    csv_list_all = []
    found_text = False

    f = html_file
    soup = BeautifulSoup(f, 'html.parser')

    for div in soup.find_all('div'):
        csv_list = []
        for tag in div.find_all():
            if tag.name.lower() in keep_list:
                csv_list.append(tag.text)
                found_text = True
        if found_text:
            csv_list_all.append(csv_list)

    # Returns a list of list, with all the content
    return csv_list_all


def write_csv(csv_list, csv_output_name):
    '''
    Receives a list of content and the name of the csv file, saves the csv file
    '''
    with open(csv_output_name, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(csv_list)


def html_to_csv(html_file, output_file = None):
    '''
    Receives an html file path, converts the html to csv and saves the file on disk.

    :param html_file : str (A file-like object, or a raw string containing HTML.)
    :param output_file : str, optional (Name and path of the output csv file)
    '''

    # Check if html file exists
    if (os.path.isfile(html_file)):
        # Create output file based on the input file name
        output_file = html_file.split('.html')[0]+".csv"
        # set isString to false, since the HTML is in a html_file
        isString = False
    # Ckeck if the html was passed as string
    elif (' ' in html_file) and (len(html_file)>2):
        # If a name for the output is not given, the file is set to output.csv
        if output_path is None:
            output_file = "output.csv"
        # set isString to true, since the HTML is in a string
        isString = True
    # If the file does not exist and is not a raw string
    else:
        raise Exception('The given HMTL file does not exist.')

    # Clean the html file
    html_file = clean_html(html_file,isString)
    # Fix the links in the file
    html_file = fix_links(html_file)
    # Extract the content
    csv_list_all = extrac_div(html_file)
    csv_list_all = [x for x in csv_list_all if x != []]
    # Saves the content in a csv file
    write_csv(csv_list_all, output_file)
