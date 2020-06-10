"""
This module calls the extraction of a binary file.

"""

import sys
from pathlib import Path
import filetype

from xlrd import open_workbook, XLRDError

from excel_extractor import ExcelExtractor
from texts_extractor import TextsExtractor
from tabula_extractor import TabulaExtractor

class Extractor():
    """
    This class chooses the right binary extractor for the file.

    If the type of the file is an Excel, uses the ExcelExtractor; Otherwise, it
    uses the TextsExtractor. Also, if the file has extra tables, other type of
    extractor can be used.

    Args:
        path (str): Absolute file path.

    Attributes:
        path (str): Absolute file path.
        type (str): File extension.

    Raises:
        FileNotFoundError: The type of the file could not be identified.

    """

    def __init__(self, path):
        self.path = path

        try:
            filetype.guess(path)
        except FileNotFoundError:
            raise FileNotFoundError('o caminho {} é inválido.'.format(path))
        else:
            self.type = filetype.guess(path).extension

    def guess_extractor(self):
        """
        Method that chooses the right extractor for the document.

        Returns:
            BinaryExtractor: The extractor.

        """

        try:
            open_workbook(self.path)
        except XLRDError:
            return TextsExtractor(self.path)
        else:
            return ExcelExtractor(self.path)

    def extra(self):
        """
        Method that verifies the existence of a extractor for extra contents.

        Note:
            For now, it only can look for tables in pdf files.

        Returns:
            TabulaExtractor, if the file is a pdf, None otherwise.

        """

        if self.type == 'pdf':
            return TabulaExtractor(self.path)
        return None

    def extractor(self):
        """
        This method calls the output methods for the chosen extractors.

        It calls the extraction of main contents, extra contents and metadata.

        """

        extractor = self.guess_extractor()
        extra = self.extra()

        extractor.output()
        extractor.metadata()

        if not extra is None:
            extra.output()

def main():
    """
    This function instantiates and calls the extraction.

    Note:
        There is a processing of the file path and the construction of a relati-
        ve path between the file path and the current work directory.

    Args:
        argv[1] (str): File path.

    Raises:
        IsADirectoryError: The path is a directory path.

    """

    filepath = sys.argv[1]

    current = Path(__file__).absolute()
    basepath = current.parents[len(current.parents) - 1]
    path = basepath.joinpath(filepath)

    if Path.is_dir(path):
        raise IsADirectoryError('o caminho {} é um diretório.'.format(path))

    Extractor(str(path)).extractor()

if __name__ == '__main__':
    main()
