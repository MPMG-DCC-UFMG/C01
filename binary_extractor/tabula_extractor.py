from tabula import read_pdf
from binary_extractor import BinaryExtractor

class TabulaExtractor(BinaryExtractor):

    def __init__(self, path):
        super().__init__(path)

    def read(self):
        df = read_pdf(self.path, pages = 'all', multiple_tables = True, silent = True)
        return df

    def process(self):
        pass

    def output(self):
        self.extra = self.read()
        for i in range(len(self.extra)):
            self.write(self.extra[i], 'table' + str(i))
