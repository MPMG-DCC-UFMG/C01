import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='binary',
    version='0.1',
    scripts=[],
    author="louisesaturnino",
    author_email="louisesaturnino@dcc.ufmg.br",
    description="binary files content and metadata extractor and parser",
    classifiers=["Programming Language :: Python :: 3"],
    packages=setuptools.find_packages(),
    install_requires=['tika', 'tabula-py', 'pandas', 'pathlib', 'xlrd', 'filetype']
)
