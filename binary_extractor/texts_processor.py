"""
This module processes the text content, separing the text and their titles.

"""

import pandas as pd

END_PUNCTUATION = ['.', '?', '!', ';']
"""list: used for mark the final_sentence interpretation."""

def is_title(i, lines):
    """
    This function tries to determine if a line is a title or a part of a text.

    Args:
        i (int): Index of the line.
        lines (list): List of all the text lines.

    Return:
        boolean: True if the line can be a title, False otherwise.

    """

    line = lines[i]

    if not between_parenthesis(line):
        if len(lines) > i + 1:
            nextline = lines[i + 1]

            if not final_sentence(line) and not line[-1:] == ',':
                if line.isupper() and not final_sentence(nextline):
                    return True
                if line.istitle():
                    return True
                if line[0].isupper() and line[-1:] == ':':
                    if nextline[0].isupper():
                        return True
    return False

def between_parenthesis(line):
    """
    This function determines if a line from the content is between parenthesis.

    Args:
        line (str): The line from the content.

    Returns:
        boolean: True, if the line is between parenthesis, False otherwise.

    """

    if line[0] == '(' and line[-1:] == ')':
        return True
    return False

def final_sentence(line):
    """
    Determines if a line from the content looks like a final sentence line.

    Args:
        line (str): The line from the content.

    Returns:
        boolean: True, if it looks final, False otherwise.

    """

    if line[-1:] in END_PUNCTUATION:
        return True
    return False

def process_text(content):
    """
    This function processes the content.

    It cleans empty lines, and the lines from the content are splited for separa
    tion between texts and titles.

    Note:
        The titles are enumerated, for distinction.

    Args:
        content(str): The extracted textual content of the file.

    Returns:
        dict: The keys are the titles; the values are the core texts.

    """

    lines = content.splitlines()
    lines = [i for i in lines if i]

    texts = {}
    text = []
    paragraph = []
    title = '0- ' + lines[0]
    texts[title] = text

    for i in range(len(lines)):
        if not is_title(i, lines):
            paragraph.append(lines[i])

            if final_sentence(lines[i]):
                text.append(paragraph)
                paragraph = []
        else:
            text.append(paragraph)
            title = str(i) + '-' + lines[i]
            text = []
            texts[title] = text
            paragraph = []

    text.append(paragraph)

    return texts

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
