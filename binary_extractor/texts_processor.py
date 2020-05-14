import pandas as pd
from tika import parser

end_punctuation = ['.', '?', '!', ';']

def is_title(i, lines):
    line = lines[i]

    if not between_parenthesis(line):
        if len(lines) > i + 1:
            next = lines[i + 1]

            if not final_sentence(line) and not (line[-1:] == ','):
                if line.isupper() and not final_sentence(next):
                    return True
                elif line.istitle():
                    return True
                elif line[0].isupper() and line[-1:] == ':':
                    if not next[0].isupper():
                        return True
    return False

def between_parenthesis(line):
    if line[0] == '(' and line[-1:] == ')':
        return True
    return False

def final_sentence(line):
    if line[-1:] in end_punctuation:
        return True
    return False

def process_text(content):
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
    content = []
    title = []

    for text in texts:
        title.append(text.split('-', 1)[1])
        title.extend([''] * (len(texts[text]) - 1))

        for paragraph in texts[text]:
            content.append('\n'.join(paragraph))

    return title, content

def columns_to_dataframe(keys, values, kname, vname):
    dict = {
        kname: keys,
        vname: values
    }

    columns = [kname, vname]
    return pd.DataFrame(dict, columns = columns)
