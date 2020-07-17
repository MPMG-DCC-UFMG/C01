"""
This module extracts tables from pdf files, using tabula-java.

"""

from tabula import read_pdf
from .binary_extractor import BinaryExtractor

class TabulaExtractor(BinaryExtractor):
    """
    Child Class: This class extracts tabular contents from a PDF file.

    Attributes:
        extra (None/list/pd.DataFrame): Extra contents of the document.

    Raises:
        TypeError: The tabula-java couldn't work in this file.

    """

    def __init__(self, path):
        super().__init__(path)
        self.extra = None

        try:
            read_pdf(self.path, pages=1, silent=True)
        except:
            raise TypeError('As tabelas não puderam ser acessadas.')

    def read(self):
        """
        This method reads the pdf file and possibly gets its tables.

        Returns:
            list: List of pd.DataFrame, each item is a extracted table.

        """

        content = read_pdf(self.path, pages='all', multiple_tables=True,
                           silent=True)

        return content

    def output(self):
        """
        This method calls the writing for each table.

        """

        self.extra = self.read()
        for i in range(len(self.extra)):
            self.write(self.extra[i], 'table' + str(i))
