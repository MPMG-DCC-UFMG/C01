from binary_extractor import *

class ExcelExtractor(BinaryExtractor):
    def __init__(self, path):
        super().__init__(path)
        self.sheets = pd.ExcelFile(self.path).sheet_names

    def read(self):
        df = pd.read_excel(self.path, sheet_name = None)
        return df

    def process(self):
        pass

    def output(self):
        self.content = self.read()

        for sheet in self.sheets:
            self.write(self.content[sheet], sheet)
