from setuptools import setup

setup(
    name='CrawlingUtils',
    version='1.0',
    description="Module with useful functions when working with scrapy and"
    " scrapy selenium",
    license="MIT",
    author='Gabriel Cardoso',
    author_email='gabrielcrds@users.noreply.github.com',
    packages=['crawling_utils'],
    install_requires=['selenium', 'requests']
)
