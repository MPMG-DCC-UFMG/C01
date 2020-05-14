from texts_processor import *

from pathlib import Path
import abc
import csv

class BinaryExtractor():

    __metaclass__ = abc.ABCMeta

    def __init__(self, path):
        self.path = path
        self.open = parser.from_file(self.path)

        self.content = None
        self.extra = None
        self.meta = None

        pure = Path(self.path)
        self.name = pure.stem
        parent = pure.parent

        self.directory = parent.joinpath(self.name)
        Path.mkdir(self.directory, exist_ok = True)

    @abc.abstractmethod
    def read(self):
        raise AssertionError

    @abc.abstractmethod
    def process(self):
        raise AssertionError

    @abc.abstractmethod
    def output(self):
        raise AssertionError

    def write(self, dataframe, name):
        file = self.directory.joinpath(name + '.csv')
        with open(file, 'w') as out:
            dataframe.to_csv(out, encoding = 'utf-8', index = None)

    def extract_metadata(self):
        return self.open['metadata']

    def process_metadata(self):
        metadata = self.extract_metadata()
        keys = list(metadata.keys())
        values = list(metadata.values())

        return columns_to_dataframe(keys, values, 'Propriedade', 'Valor')

    def metadata(self):
        self.meta = self.process_metadata()
        self.write(self.meta, 'metadata')
