from info_extractor import InfoExtractor
import pandas as pd

class TablesExtractor(InfoExtractor):
    def __init__(self, path):
        InfoExtractor.__init__(self, path)

        self.output = 'table.csv'
        self.tables_df = None

    def extract(self):
        df = pd.read_excel(self.path, sheet_name = None)
        return df

    def process(self):
        pass

    def write(self):
        self.tables_df = TablesExtractor(self.path).extract()
        for sheet in self.tables_df:
            with open(self.output, 'w') as out_tab:
                self.tables_df.to_csv(self.output, encoding = 'utf-8')

def main():
    TablesExtractor('Files/energia-eletrica-industrial-usdbep-2020-04-05.xlsx').write()

if __name__ == '__main__':
    main()

#TODO:
#read all tabs
#display dates(?)
#extract metadata
#fix multiple tabs
