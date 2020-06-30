"""
This module extracts contents from binary files.

"""

from pathlib import Path
import abc

from tika import parser
from .texts_processor import columns_to_dataframe

class BinaryExtractor():
    """
    This class extracts the content of binary files.

    Args:
        path (str): File path.

    Attributes:
        path (str): File path.
        meta (None/pd.DataFrame): Metadata of the document.
        content(None/dict/pd.DataFrame): Main content of the document.
        name (str): File name, without its extension.
        directory (Path): Created directory for saving the outputs.

    Raises:
        TypeError: The file can't be parsed.

    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, path):

        # initial important variables
        self.path = path
        self.meta = None
        self.content = None

        # create directory for outputs
        pure = Path(self.path)
        self.name = pure.stem
        self.directory = pure.parent.joinpath(self.name)
        Path.mkdir(self.directory, exist_ok=True)

        # file parsing
        try:
            self.open = parser.from_file(self.path)
        except:
            raise TypeError('O arquivo não pôde ser extraído.')

    @abc.abstractmethod
    def read(self):
        """
        Abstract Method: Reads the file content.

        """

        raise AssertionError

    @abc.abstractmethod
    def output(self):
        """
        Abstract Method: Prepares the processed content for writing.

        """

        raise AssertionError

    def write(self, dataframe, name):
        """
        This method writes the output in csv format.

        Args:
            dataframe (pd.DataFrame): table to be writen.
            name (str): name of the csv file.

        """

        file = self.directory.joinpath(name + '.csv')
        with open(file, 'w') as out:
            dataframe.to_csv(out, encoding='utf-8', index=None)

    def read_metadata(self):
        """
        dict: This method accesses and returns the metadata.

        """

        return self.open['metadata']

    def process_metadata(self):
        """
        This method processes the metadata.

        Returns:
            pd.DataFrame: table with the metadata properties and their values.

        """

        metadata = self.read_metadata()
        keys = list(metadata.keys())
        values = list(metadata.values())

        return columns_to_dataframe(keys, values, 'Propriedade', 'Valor')

    def metadata(self):
        """
        This method writes the metadata table in csv.

        Attributes:
            meta (pd.DataFrame): metadata dataframe.

        """

        self.meta = self.process_metadata()
        self.write(self.meta, 'metadata')
