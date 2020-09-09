"""
This module puts everything together and calls the extractor.

"""

import sys

from pathlib import Path
from .extractor import Extractor


def main(filepath):
    """
    This function instantiates and calls the extraction.

    Note:
        There is a processing of the file path and the construction of a relati-
        ve path between the file path and the current work directory.

    Args:
        argv[1] (str): File path.

    Raises:
        IsADirectoryError: The path is a directory path.

    """

    #filepath = sys.argv[1]

    current = Path(__file__).absolute()
    basepath = current.parents[len(current.parents) - 1]
    path = basepath.joinpath(filepath)

    if Path.is_dir(path):
        raise IsADirectoryError('o caminho {} é um diretório.'.format(path))

    Extractor(str(path)).extractor()


if __name__ == '__main__':
    main()
