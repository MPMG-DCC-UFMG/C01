from info_extractor import InfoExtractor
from tabula import read_pdf
import pandas as pd

class TabulaExtractor(InfoExtractor):

    def __init__(self, path):
        InfoExtractor.__init__(self, path)

        self.output = 'table.csv'
        self.tables_df = None

    def extract(self):
        df = pd.read_pdf(self.path, output_format = 'dataframe', multiple_tables = True)
        return df

    def process(self):
        extract = TabulaExtractor(self.path).extract()
        df = pd.DataFrame(extract)
        columns = df.shape[1]
        print(columns)
        #if columns > 1:
        return df

    def write(self):
        self.tables_df = TabulaExtractor(self.path).process()
        with open(self.output, 'w') as out_tab:
            print(self.path)
            self.tables_df.to_csv(self.output, encoding = 'utf-8')

#TODO:
#multiple_tables
#extract to DataFrame
#turn off verbose mode
#check if a valid table is ready
