import os
from bs4 import BeautifulSoup
import errno
from src.parsing.html.parsing_html_table import *
from src.parsing.html.parsing_html_div import *


def clean_html(html_file, is_string):
    """
    Receives the html file and removes unnecessary parts, as header, footer, etc.
    """

    # List of elements that are going to be removed from the html
    remove_list = ["head", "header", "footer", "polygon", "path", "script",
                   "symbol", "meta", "link", "title", "style", "nav", "form"]
    remove_class = ["sidebar-inner", "breadcrumb", "share", "navegacao",
                    "skiptranslate", "goog-te-spinner-pos", "social-list",
                    "social-icon", "copyright", "id_assist_frame",
                    "fbc-badge-tooltip", "areaNaoImprimivel", "menu_container"]
    remove_id = ["boxes", "mySidenav", "chat-panel", "footer"]

    # Check if the html_file is a string with the page or a path to the file
    soup = ""
    if is_string:
        f = html_file
        soup = BeautifulSoup(f, 'html.parser')
    else:
        f = open(html_file, encoding="ISO-8859-1")
        soup = BeautifulSoup(f, 'html.parser')
        f.close()

    # Remove any tag present in remove_list
    for tag in soup.find_all():
        if tag.name.lower() in remove_list:
            tag.extract()
    # Remove any div with the class in remove_class
    for div in soup.find_all("div", {'class': remove_class}):
        div.extract()
    # Remove any div with the id in remove_id
    for div in soup.find_all("div", {'id': remove_id}):
        div.extract()
    # Remove any table with the id in remove_id (bad html construction)
    for tab in soup.find_all("table", {'id': remove_id}):
        tab.extract()

    html_file = str(soup)

    return html_file


def fix_links(html_file):
    """
    Receives the html file and return the same file with the value of the links
    as the text of the links
    """
    f = html_file
    soup = BeautifulSoup(f, 'html.parser')

    for a in soup.find_all('a', href=True):
        if "http" in a['href']:
            a.string = a['href']

    html_file = str(soup)

    return html_file


def check_div(html_file):
    """
    Receives a html file and returns booleans indicating if the content is in
    a table or div
    """
    # Boolean variables to indicate if the content is in table or div format
    table_content = False
    div_content = False

    # List of elements that are going to be removed from the html
    table_tag = ["table"]
    div_tag = ["p", "h1", "h2", "h3"]

    # Open the string with BeautifulSoup
    f = html_file
    soup = BeautifulSoup(f, 'html.parser')

    # Check the remaining tags
    for tag in soup.find_all():
        if tag.name.lower() in table_tag:
            table_content = True
        elif tag.name.lower() in div_tag:
            div_content = True

    return table_content, div_content


def html_detect_content(html_file, is_string=False, output_file='output',
                        match='.+', flavor=None, header=None, index_col=None, skiprows=None,
                        attrs=None, parse_dates=False, thousands=', ', encoding=None, decimal='.',
                        converters=None, na_values=None, keep_default_na=True, displayed_only=True):
    """
    Receives an html file path, converts the html and saves the file on
    disk.

    :param html_file : str (A file-like object, or a raw string containing
     HTML.)
    :param is_string : bool, default False (Whether the html file is passed as a
    string or as the path to the file)
    :param output_file: str (Name of the output file, default is output)
    :param match : str or compiled regular expression (The set of tables
    containing text matching this regex or string will be returned. )
    :param flavor : str or None, container of strings (The parsing engine to
    use.)
    :param header : int or list-like or None, optional (The row (or list of
    rows for a MultiIndex) to use to make the columns headers.)
    :param index_col : int or list-like or None, optional (The column (or list
    of columns) to use to create the index.)
    :param skiprows : int or list-like or slice or None, optional (0-based.
    Number of rows to skip after parsing the column integer.)
    :param attrs : dict or None, optional (This is a dictionary of attributes
    that you can pass to use to identify the table in the HTML.)
    :param parse_dates : bool, optional
    :param thousands : str, optional (Separator to use to parse thousands.
    Defaults to ','.)
    :param encoding : str or None, optional (The encoding used to decode the
    web page.)
    :param decimal : str, default ‘.’ (Character to recognize as decimal point)
    :param converters : dict, default None (Dict of functions for converting
     values in certain columns.)
    :param na_values : iterable, default None (Custom NA values)
    :param keep_default_na : bool, default True (If na_values are specified and
     keep_default_na is False the default NaN values are overridden)
    :param displayed_only : bool, default True (Whether elements with
     “display: none” should be parsed)
    """

    # Check if html file exists
    if (os.path.isfile(html_file)) or is_string:
        # Clean the html file
        html_file = clean_html(html_file, is_string)
        # Fix the links in the file
        html_file = fix_links(html_file)
        # Check the content
        table_content, div_content = check_div(html_file)
        # Call the indicated parsing
        if div_content:
            # HAS A DIV
            div_to_file(html_file, output_file)
        if table_content:
            # HAS A TABLE
            table_to_file(html_file, output_file, match, flavor, header, index_col, skiprows,
                          attrs, parse_dates, thousands, encoding, decimal,
                          converters, na_values, keep_default_na, displayed_only)
        # If the file has no table or div with content
        if not (table_content or div_content):
            raise ValueError('No content found.')

    else:
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT),
                                html_file)
