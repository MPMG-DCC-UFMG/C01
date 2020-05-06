from binary_extractor import *

class TextsExtractor(BinaryExtractor):

    def __init__(self, path):
        super().__init__(path)

    def read(self):
        return self.open['content']

    def process(self):
        content = self.read()
        texts = process_text(content)
        title, content = texts_to_columns(texts)

        return columns_to_dataframe(title, content, 'Título', 'Texto')

    def output(self):
        self.content = self.process()
        self.write(self.content, self.name)
