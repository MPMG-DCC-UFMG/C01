from info_extractor import InfoExtractor
from texts_processor import *

class TextsExtractor(InfoExtractor):

    def __init__(self, path):
        InfoExtractor.__init__(self, path)

        self.output_text = 'text.csv'
        self.output_meta = 'meta.csv'
        self.content_df = None
        self.metadata_df = None

    def extract(self):
        file = parser.from_file(self.path)

        metadata = file['metadata']
        content = file['content']

        return content, metadata

    def process(self):
        content, metadata = TextsExtractor.extract(self)
        texts = process(content)
        print(texts)

        #self.metadata_df = to_dataframe(metadata)
        self.content_df = to_dataframe(texts)

    def write(self):
        TextsExtractor.process(self)
        # with open(self.output_meta, 'w') as out_meta:
        #     self.metadata_df.to_csv(out_csv, encoding = 'utf-8')
        with open(self.output_text, 'w') as out_cont:
            self.content_df.to_csv(out_cont, encoding = 'utf-8')

#TODO:
#process metadata
#lost of information =(
