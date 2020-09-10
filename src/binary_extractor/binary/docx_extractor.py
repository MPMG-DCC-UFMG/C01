"""
This module extracts and processes the content from .docx files.

"""
from pathlib import Path

from .texts_extractor import TextsExtractor
from .docx_processor import process_docx,
from .text_processor import texts_to_columns, columns_to_dataframe

class DOCXExtractor(TextsExtractor):
    """
    This child class specifically extracts textual and tabular contents of docx
    files given.

    """

    __doc__ = BinaryExtractor.__doc__ + __doc__

    def read(self):
        """
        This method opens the main content of the docx file.

        Returns:
            str: textual extracted content.

        Raises:
            TypeError: The method couldn't extract text from the file.

        """

        content = self.open['content']
        if content is None:
            raise TypeError('Não foi possível detectar texto no arquivo.')

        return content

    def process(self):
        """
        This method processes the content.

        Returns:
            pd.DataFrame: Content separated in titles and texts.

        """

        content = self.read()
        texts = process_DOMM(content)
        title, content = texts_to_columns(texts)

        return columns_to_dataframe(title, content, 'Título', 'Texto')

def main():

    filepath = '/home/loui/C04/binary_extractor/tests/test_files/AMM/2768.docx'

    current = Path(__file__).absolute()
    basepath = current.parents[len(current.parents) - 1]
    path = basepath.joinpath(filepath)

    DOCXExtractor(str(path)).output()

if __name__ == '__main__':
    main()
