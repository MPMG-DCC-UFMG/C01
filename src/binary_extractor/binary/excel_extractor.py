"""
This module extracts the content from Excel files.

"""

import pandas as pd

from .binary_extractor import BinaryExtractor

class ExcelExtractor(BinaryExtractor):
    """
    Child Class: This class extracts tabular contents from an Excel file.

    Attributes:
        sheets (list): List of sheet names.

    Raises:
        TypeError: The file is not an Excel file.

    """

    __doc__ = BinaryExtractor.__doc__ + __doc__

    def __init__(self, path):
        super().__init__(path)

        try:
            self.sheets = pd.ExcelFile(self.path).sheet_names
        except:
            raise TypeError('O arquivo não foi reconhecido como Excel.')


    def read(self):
        """
        This method gets all of the spreadsheets of the file.

        Returns:
            dict: the keys are the names of the sheet, the values are dataframes
                with the content of the spreadsheets.

        """

        tables = pd.read_excel(self.path, sheet_name=None)

        return tables

    def output(self):
        """
        This method calls the writing for each spreadsheet.

        """
        self.content = self.read()

        for sheet in self.sheets:
            self.write(self.content[sheet], sheet)
