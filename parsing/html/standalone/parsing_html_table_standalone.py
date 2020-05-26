import pandas as pd
import os
import sys
from bs4 import BeautifulSoup


def print_params(list_params):
    print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
    print('Parameters: ')
    for i in range(1, len(sys.argv)):
        print(list_params[i - 1] + ' = ' + sys.argv[i])
    print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')

def html_to_df(html_file, match, flavor, header, index_col, skiprows, attrs, parse_dates, thousands, encoding, decimal, converters, na_values, keep_default_na, displayed_only, isString):
    '''
    Receives the html file path and reads into a DataFrame structure using the Pandas module.
    This function also converts the link element attribute to it's value
    '''
    try:
        if not isString:
            soup = ""
            f = open(html_file, encoding="ISO-8859-1")
            soup = BeautifulSoup(f, 'html.parser')
            f.close()

            for a in soup.find_all('a', href=True):
                a.string = a['href']

            html_file = str(soup)

        dfs = pd.read_html(html_file, match, flavor, header, index_col, skiprows, attrs, parse_dates, thousands, encoding, decimal, converters, na_values, keep_default_na, displayed_only)
    except:
        raise Exception("The table could not be found in the HTML file.")

    return dfs

def df_to_csv(dfs, output_file, index = False):
    '''
    Receives a list of DataFrames and write them to a csv file (output_file).
    '''
    for i in range(0, len(dfs)):
        try:
            dfs[i].to_csv(output_file, index = index, mode='a', quoting =1)
        except:
            raise Exception("The system could not save the CSV file.")
    
    
def html_to_csv(html_file_path, match='.+', flavor=None, header=None, index_col=None, skiprows=None, attrs=None, parse_dates=False, thousands=', ', encoding=None, decimal='.', converters=None, na_values=None, keep_default_na=True, displayed_only=True):
    '''
    Receives an html file path, converts the html to csv and saves the file on disk.

    :param html_file : str (A file-like object, or a raw string containing HTML.)
    :param match : str or compiled regular expression (The set of tables containing text matching this regex or string will be returned. )
    :param flavor : str or None, container of strings (The parsing engine to use.)
    :param header : int or list-like or None, optional (The row (or list of rows for a MultiIndex) to use to make the columns headers.)
    :param index_col : int or list-like or None, optional (The column (or list of columns) to use to create the index.)
    :param skiprows : int or list-like or slice or None, optional (0-based. Number of rows to skip after parsing the column integer.)
    :param attrs : dict or None, optional (This is a dictionary of attributes that you can pass to use to identify the table in the HTML.)
    :param parse_dates : bool, optional
    :param thousands : str, optional (Separator to use to parse thousands. Defaults to ','.)
    :param encoding : str or None, optional (The encoding used to decode the web page.)
    :param decimal : str, default ‘.’ (Character to recognize as decimal point )
    :param converters : dict, default None (Dict of functions for converting values in certain columns.)
    :param na_values : iterable, default None (Custom NA values)
    :param keep_default_na : bool, default True (If na_values are specified and keep_default_na is False the default NaN values are overridden)
    :param display_only : bool, default True (Whether elements with “display: none” should be parsed)
    '''

    
    # Check if html file exists
    if (os.path.isfile(html_file_path)):
        # Create output file based on the input file name
        output_file = html_file_path.split('.html')[0]+".csv"
        # set isString to false, since the HTML is in a html_file
        isString = False
    # Ckeck if the html was passed as string
    elif (' ' in html_file_path) and len(html_file_path)>2:
        # Create output file based on the input file name
        output_file = "output.csv"
        # set isString to true, since the HTML is in a string
        isString = True

    else:
        raise Exception('The given HMTL file does not exist.')

    # Convert html do Pandas DataFrame
    dfs = html_to_df(html_file_path, match, flavor, header, index_col, skiprows, attrs, parse_dates, thousands, encoding, decimal, converters, na_values, keep_default_na, displayed_only, isString)

    # Save the Pandas DataFrame to a csv file
    df_to_csv(dfs, output_file)
        
        
def main():
	"""Main method for the standalone version, receives html file path and parameters as arguments and calls the functions.
	"""
	# Get the parameters displayed if needed and stored
	list_params = ['<HTML_file>', '<match>', '<flavor>', '<header>', '<index_col>', '<skiprows>', '<attrs>', '<parse_dates>', '<thousands>', '<encoding>', '<decimal>', '<converters>','< na_values>', '<keep_default_na>', '<displayed_only>']

	# If it is missing any parameter, print the parameter list
	if len(sys.argv) < 2:
			sys.exit('Usage: ' + sys.argv[0] + ' ' + ' '.join(list_params))
	print_params(list_params)

	# Get the parameters
	html_file = sys.argv[1]

	# Calls the core method
	if len(sys.argv) == 1:
		html_to_csv(html_file_path)
	else:
		html_to_csv(*sys.argv[1:])


	# If everything went fine
	print('The HTML to CSV convertion finished!')

if __name__ == "__main__":
    main()
