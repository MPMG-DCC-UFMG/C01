# Binary File Extractor

This tool extracts textual and tabular content from binary files. It uses, basically:

- *Pandas*, for extracting data from Excel;
- *Tika-Python* (a Python port of the Apache Tika), for extracting textual content from binary files in general;
- *Tabula-Py* (a simple Python wrapper of tabula-java), for extracting tabular patterns from PDFs.

## Dependencies

The module uses the following packages:

- [**pandas**](https://pypi.org/project/pandas/)
- [**pathlib**](https://pypi.org/project/pathlib/)
- [**filetype**](https://pypi.org/project/filetype/)
- [**tabula-py**](https://pypi.org/project/tabula-py/)
- [**tika-python**](https://github.com/chrismattmann/tika-python)

For information about the libraries installation, you can follow the links above.
Note that using **Tika** and **Tabula** require **Java** (**8+**). Tika also requires a **Tika Server**.

## Usage

### Executing the tool on the command line ###
In binary_extractor directory, run:
`python -m binary.extractor path`

where path is the **absolute path** from the root of your file system.
**Example:** `'/home/user/files/text.pdf'`.

### Executing the unit tests ###
In tests directory, run:
`python -m unittest test_binary.test_binary`


The module will guess the type of your file and use the best extracting modules for the content.

## To Do

[ ] Write more information about the modules, the next features
[ ] Link this file with a complete documentation
