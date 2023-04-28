import setuptools
from setuptools import setup


with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='schedule',
    version='1.0',
    description='',
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    author='Elves Rodrigues',
    packages=setuptools.find_packages(),
    install_requires=[
        'mock-alchemy==0.2.6',
        'psycopg2-binary==2.9.6',
        'python-environ==0.4.54',
        'pytz==2023.3',
        'SQLAlchemy==2.0.10',
        'typing_extensions==4.5.0',
    ]
)
