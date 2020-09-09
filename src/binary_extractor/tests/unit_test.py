"""
This module tests the extractors and the processing of binary file contents.

"""

import unittest
import csv

from pathlib import Path

import tika
tika.initVM()
from tika import parser

import pandas as pd

from binary import Extractor
from binary import ExcelExtractor
from binary import TextsExtractor
from binary import TabulaExtractor
from binary import between_parenthesis, final_sentence, is_title
from binary import process_text, texts_to_columns, columns_to_dataframe

# global variables for file paths in each class test.
image =  str(Path.cwd().joinpath('tests/test_files/files/Trees.jpg'))
edital = str(Path.cwd().joinpath('tests/test_files/files/Edital.pdf'))
cotacao = str(Path.cwd().joinpath('tests/test_files/files/Cotacao.xlsx'))

class TestExtractor(unittest.TestCase):
    """
    This class tests the Extractor class (extractor.py).

    """

    def test_absolute_path(self):
        """
        This method tests the use of absolute path of files.

        """

        path = str(Path.cwd().joinpath('tests/test_files/files/Edital.pdf'))
        Extractor(path)

    def test_guess_extractor(self):
        """
        This method tests the guessing of the extractor.

        """

        text = edital
        excl = cotacao

        self.assertIsInstance(Extractor(text).guess_extractor(), TextsExtractor)
        self.assertIsInstance(Extractor(excl).guess_extractor(), ExcelExtractor)

    def test_extra(self):
        """
        This method tests the adequate use of the extra content extractor.

        """

        path1 = edital
        path2 = cotacao

        self.assertIsInstance(Extractor(path1).extra(), TabulaExtractor)
        self.assertEqual(Extractor(path2).extra(), None)

    # Exceptions

    def test_invalid_path(self):
        """
        This method tests if the class raises exception for wrong paths.

        """

        path = str(Path.cwd().joinpath('Files/Edital.pdf'))
        self.assertRaises(FileNotFoundError, Extractor, path)

    def test_directory(self):
        """
        This method tests if the class raises exception for directory paths.

        """

        path = str(Path.cwd().joinpath('tests/test_files/'))
        self.assertRaises(IsADirectoryError, Extractor, path)


class TestTextProcessing(unittest.TestCase):
    """
    This class tests the text processing (texts_processor.py).

    """

    with open(str(Path.cwd().joinpath('tests/test_files/files/lines'))) as example:
        texts = example.read()
        lines = texts.splitlines()

    def test_process_text(self):
        """
        This method checks if the content is complete after the processing.

        """
        path = edital
        file = parser.from_file(path)
        split = file['content'].splitlines()
        safe = [i for i in split if i]

        with open('tests/test_files/csv/Edital/Edital.csv') as outcsv:
            product = csv.reader(outcsv)
            content = []
            for row in product:
                content.append(row[0])
                content.append(row[1])

        text = [i for i in content if i]
        assert text, safe

    def test_between_parenthesis(self):
        """
        This method checks the behavior of between_parenthesis function.

        """

        assert between_parenthesis('(Parenthesis)')
        assert not between_parenthesis('No Parenthesis')
        assert not between_parenthesis('(Half Parenthesis')

    def test_final_sentence(self):
        """
        This method checks the behavior of final_sentence function.

        """

        assert final_sentence('Punctuation.')
        assert not final_sentence('No Punctuation')

    def test_titles(self):
        """
        This method checks the behavior of is_title function.

        """

        assert is_title(1, self.lines)
        assert is_title(5, self.lines)
        assert is_title(6, self.lines)
        assert not is_title(0, self.lines)
        assert not is_title(2, self.lines)
        assert not is_title(3, self.lines)
        assert not is_title(4, self.lines)
        assert not is_title(7, self.lines)
        assert not is_title(8, self.lines)
        assert not is_title(9, self.lines)
        assert not is_title(10, self.lines)

    def test_texts_to_columns(self):
        """
        This method checks the behavior of texts_to_columns function.

        """

        new = process_text(self.texts)
        col1, col2 = texts_to_columns(new)

        assert len(col1), len(col2)

    def test_columns_to_dataframe(self):
        """
        This method checks the behavior of columns_to_dataframe function.

        """

        new = process_text(self.texts)
        keys, values = texts_to_columns(new)
        dataframe = columns_to_dataframe(keys, values, 'keys', 'values')

        self.assertIsInstance(dataframe, pd.DataFrame)


class TestBinaryExtractor(unittest.TestCase):
    """
    Tests the BinaryExtractor (binary_extractor.py) and the child classes.

    The child-classes: ExcelExtractor (excel_extractor.py), TextsExtractor
    (texts_extractor.py) and TabulaExtractor (tabula_extractor.py).

    """

    def test_read(self):
        """
        This method tests the behavior of each concrete read methods.

        """

        text = edital
        excl = cotacao

        self.assertIsInstance(TextsExtractor(text).read(), str)
        self.assertIsInstance(TabulaExtractor(text).read()[0], pd.DataFrame)
        self.assertIsInstance(ExcelExtractor(excl).read(), dict)

    def test_process(self):
        """
        This method tests the behavior of the TextsExtractor process method.

        """

        text = edital
        self.assertIsInstance(TextsExtractor(text).process(), pd.DataFrame)

    def test_output(self):
        """
        This method tests the behavior of each concrete output methods.

        It checks if the method runs and if the output files exist as expected.

        """

        text = edital
        excl = cotacao

        TextsExtractor(text).output()
        ExcelExtractor(excl).output()
        TabulaExtractor(text).output()

        assert Path('tests/test_files/csv/Edital/Edital.csv').exists()
        assert Path('tests/test_files/csv/Cotacao/Original.csv').exists()
        assert Path('tests/test_files/csv/Edital/table0.csv').exists()

    def test_metadata(self):
        """
        This method tests the behavior of extracting and writing metadata.

        It checks if the method runs and if the output files exist as expected.

        """

        text = edital
        excl = cotacao

        TextsExtractor(text).metadata()
        ExcelExtractor(excl).metadata()

        assert Path('tests/test_files/csv/Edital/metadata.csv').exists()
        assert Path('tests/test_files/csv/Cotacao/metadata.csv').exists()

    # Exceptions

    def test_exception_text(self):
        """
        This method checks the raising exception for no getting text from file.

        """

        path = image
        self.assertRaises(TypeError, Extractor(path).extractor)

    def test_exception_tabula(self):
        """
        This method checks the raising exception for tabula errors.

        """

        path = image
        self.assertRaises(TypeError, TabulaExtractor, path)

    def test_exception_excel(self):
        """
        This method checks the raising exception for excel extractor errors.

        """

        path = edital
        self.assertRaises(TypeError, ExcelExtractor, path)

if __name__ == '__main__':
    unittest.main()
