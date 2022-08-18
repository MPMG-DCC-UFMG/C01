from setuptools import setup, find_packages

setup(
    name='LinkFinder',
    version='1.0',
    description="Module to find links in pages.",
    license="MIT",
    packages=find_packages(),
    install_requires=['scrapy', 'playwright']
)
