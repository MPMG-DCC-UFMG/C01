"""
This module contains the processing-helpers functions.

"""

END_PUNCTUATION = ['.', '?', '!', ';']
"""list: used for mark the final_sentence interpretation."""

import pandas as pd

def pdf_to_docx(file):
    """
    This function converts .pdf files in .docx files.

    It calls a shell process for pandoc converter.

    Args:
        file(Path): the file path of a pdf document.
    """

    pass

def texts_to_columns(texts):
    """
    This function prepares the content dictionary for writing in tabular form.

    Args:
        texts (dict): The content dictionary, enumerated titles and texts.

    Returns:
        (list, list): two same-size lists, that will be two columns in a table.

    """

    content = []
    title = []

    for text in texts:
        title.append(text.split('-', 1)[1])
        title.extend([''] * (len(texts[text]) - 1))

        for paragraph in texts[text]:
            content.append('\n'.join(paragraph))

    return title, content

def columns_to_dataframe(keys, values, kname, vname):
    """
    This function transforms two lists in a two-columns dataframe.

    Args:
        kname (str): Name for the first column.
        vname (str): Name for the second column.
        keys (list): The first column content.
        values (list): The second column content.

    Returns:
        pd.DataFrame: the dataframe of the contents.

    """

    dcontent = {
        kname: keys,
        vname: values
    }

    columns = [kname, vname]
    return pd.DataFrame(dcontent, columns=columns)
