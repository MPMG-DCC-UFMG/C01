"""
This module extracts and processes non-tabular binary files.

"""

from .binary_extractor import BinaryExtractor
from .texts_processor import process_text, texts_to_columns, columns_to_dataframe

class TextsExtractor(BinaryExtractor):
    """
    Child Class: This class extracts non-tabular contents.

    """

    __doc__ = BinaryExtractor.__doc__ + __doc__

    def read(self):
        """
        This method reads the main content of the file.

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
        This method processes the textual content.

        Returns:
            pd.DataFrame: Content separated in titles and texts.

        """
        content = self.read()
        texts = process_text(content)
        title, content = texts_to_columns(texts)

        return columns_to_dataframe(title, content, 'Título', 'Texto')

    def output(self):
        """
        This method calls the writing of the output table.

        """
        self.content = self.process()
        self.write(self.content, self.name)
