import pandas as pd
from bs4 import BeautifulSoup


def html_to_df(html_file, match, flavor, header, index_col, skiprows, attrs,
               parse_dates, thousands, encoding, decimal, converters, na_values,
               keep_default_na, displayed_only):
    """
    Receives the html file path and reads into a DataFrame structure using the
    Pandas module.
    This function also converts the link element attribute to it's value
    """
    try:
        f = html_file
        soup = BeautifulSoup(f, 'html.parser')

        for a in soup.find_all('a', href=True):
            a.string = a['href']

        html_file = str(soup)

        dfs = pd.read_html(html_file, match=match, flavor=flavor, header=header,
                           index_col=index_col, skiprows=skiprows, attrs=attrs,
                           parse_dates=parse_dates, thousands=thousands,
                           encoding=encoding, decimal=decimal,
                           converters=converters, na_values=na_values,
                           keep_default_na=keep_default_na,
                           displayed_only=displayed_only)
    except:
        raise Exception("The table could not be found in the HTML file.")

    return dfs


def df_to_file(dfs, output_file, to_csv, index=False):
    """
    Receives a list of DataFrames and write them to a csv file (output_file).
    """
    for i in range(0, len(dfs)):
        if to_csv:
            try:
                dfs[i].to_csv(output_file, index=index, mode='a', quoting=1)
            except:
                raise Exception("The system could not save the CSV file.")
        else:
            try:
                with open(output_file, "a", newline="") as f:
                    dfs[i].to_json(f)
            except:
                raise Exception('The system could not save the JSON file.')


def table_to_file(html_file_path, output_file='output',
                  match='.+', flavor=None, header=None, index_col=None, skiprows=None,
                  attrs=None, parse_dates=False, thousands=', ', encoding=None, decimal='.',
                  converters=None, na_values=None, keep_default_na=True, displayed_only=True, to_csv=False):
    """
    Receives an html file path, converts the html to csv and saves the file on
    disk.

    :param html_file_path : str (A file-like object, or a raw string containing
     HTML.)
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
    :param to_csv : bool, default False (Whether the output file should be csv or json)
    """

    # Convert html do Pandas DataFrame
    dfs = html_to_df(html_file_path, match, flavor, header, index_col,
                     skiprows, attrs, parse_dates, thousands, encoding, decimal, converters,
                     na_values, keep_default_na, displayed_only)
    # Save the Pandas DataFrame to a file
    df_to_file(dfs, output_file, to_csv)
