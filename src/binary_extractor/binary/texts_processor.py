"""
This module processes the text content, separating the text and their titles.

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

def process_DOMM(content):
    """
    This function processes the  DOMM content.

    It cleans empty lines, the pages headers and footers. Also, the lines from
    the content are splited for separation of different 'Diários'.

    Note:
        The titles are enumerated, for distinction.

    Args:
        content(str): The extracted textual content of the file.

    Returns:
        dict: The keys are the titles; the values are the core texts.

    """

    lines = content.splitlines()
    head = find_header_DOMM(lines)
    process_header(head)
    lines = [i for i in lines if i and not(is_header(i, head) or is_footer(i))]

    texts = {}
    section = []
    text = []
    entity = '0-' + head
    texts[entity] = section

    for i, line in enumerate(lines):
        if i + 1 < len(lines):
            if not is_entity(line, lines[i+1]):
                if not is_entity(lines[i-1], line):
                    text.append(line)

                    if final_section(line):
                        section.append(text)
                        text = []
            else:
                section.append(text)
                entity = str(i) + '-' + line + lines[i+1]
                section = []
                texts[entity] = section
                text = []
    section.append(text)

    return texts

def find_header_DOMM(lines):
    """
    This function finds the header of the Diario Oficial document.

    Args:
        lines(str): the document textual content.

    Returns:
        line(None/str): the founded header, if it exists.

    """

    terms = '•   Diário Oficial dos Municípios Mineiros   •'

    for line in lines:
        if terms in line:
            return line
    return None

def process_header(header):
    """
    This function processes the document header.

    Args:
        header(str): the header line of the document.

    """

    pass

def is_header(line, header):
    """
    This function determines if a line is a header of the document.

    Args:
        line(str): a line of the document.
        header(str): the document header.

    Returns:
        True, if they are equal, False otherwise.

    """

    if line == header:
        return True
    return False

def is_footer(line):
    """
    This function determines if a line is a footer of a Diario Oficial.

    Args:
        line(str): a line of the document.

    Returns:
        True, if the line is a footer, False otherwise.
    """

    return line.startswith('www.diariomunicipal.com.br/amm-mg')

def is_entity(line, nextline):
    """
    This function determines if a line starts a Diario Oficial of a new entity.

    Args:
        line(str): a line of the document.
        nextline(str): the next line of the document.

    Returns:
        True, if the lines indicate a new entity, False otherwise.

    """

    result = line.startswith('ESTADO DE MINAS GERAIS') and nextline.isupper()
    return result

def final_section(line):
    """
    This function determines if a line ends a Diario Oficial section.

    Args:
        line(str): a line of the document.

    Returns:
        True, if the line indicates end the of the section, False otherwise.

    """

    return line.startswith('Código Identificador:')

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
