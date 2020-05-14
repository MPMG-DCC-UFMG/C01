from excel_extractor import ExcelExtractor
from texts_extractor import TextsExtractor
from tabula_extractor import TabulaExtractor
#from errors import *

import sys
from pathlib import Path
from xlrd import open_workbook, XLRDError

class Factory():

    def __init__(self, path):
        self.path = path

    def type_of_binary(self):
        try:
            open_workbook(self.path)
        except XLRDError:
            return TextsExtractor(self.path)
        else:
            return ExcelExtractor(self.path)

    def extractor(self):
        Extractor = self.type_of_binary()
        Extractor.output()
        Extractor.metadata()

        if Path(self.path).suffix == '.pdf':
            TabulaExtractor(self.path).output()


def main():
    filepath = sys.argv[1]

    if Path(filepath).is_absolute():
        current = Path(__file__).absolute()

        basepath = current.parents[len(current.parents) - 1]
        path = basepath.joinpath(filepath)

        extractor = Factory(str(path)).extractor()

    else:
        raise FileNotFoundError('o caminho {} não é absoluto.'.format(filepath))

if __name__ == '__main__':
    main()
