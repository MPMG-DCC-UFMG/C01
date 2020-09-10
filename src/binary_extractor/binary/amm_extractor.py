"""
This module extracts and processes the content from PDFs from 'Diário Oficial
dos Municípios Mineiros': http://www.diariomunicipal.com.br/amm-mg/

"""
from pathlib import Path

from .texts_extractor import TextsExtractor
from .texts_processor import process_DOMM, texts_to_columns, columns_to_dataframe

class AMMExtractor(TextsExtractor):
    """
    This child class specifically extracts textual content of the documents from
    the site mentioned above.

    """

    def process(self):
        """
        This method processes the textual content.

        Returns:
            pd.DataFrame: Content separated in titles and texts.

        """

        content = self.read()
        texts = process_DOMM(content)
        title, content = texts_to_columns(texts)

        return columns_to_dataframe(title, content, 'Título', 'Texto')

def main():

    filepath = '/home/loui/C04/binary_extractor/tests/test_files/AMM/2768.pdf'

    current = Path(__file__).absolute()
    basepath = current.parents[len(current.parents) - 1]
    path = basepath.joinpath(filepath)

    AMMExtractor(str(path)).output()

if __name__ == '__main__':
    main()
