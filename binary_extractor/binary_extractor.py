from tables_extractor import TablesExtractor
from texts_extractor import TextsExtractor

class BinaryExtractor():
    def __init__(self, path, output_dict):
        self.path = path
        self.table = output_dict.get('table')
        self.texts = output_dict.get('texts')
        self.meta = output_dict.get('meta')

    def output(self):
        if self.table == True:
            TablesExtractor(self.path).write()
        if self.texts == True:
            TextsExtractor(self.path).write()
        # if self.meta == True:
        #     TextsExtractor(self.path, only_metadata = True)
