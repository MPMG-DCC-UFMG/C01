from setuptools import setup, find_packages


with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='crawl_prioritizer',
    version='1.0',
    description='Crawl priority manager',
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    author='Elves Rodrigues',
    packages=find_packages(),
    install_requires=['numpy','psycopg2-binary','tldextract','ujson']
)
