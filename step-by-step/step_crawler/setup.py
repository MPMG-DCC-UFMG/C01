from setuptools import setup


with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='Step Crawler',
    version='1.0',
    description='Module creating step by step crawlers',
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    author='Tales Panoutsos',
    author_email='TalesPanoutsos@users.noreply.github.com',
    packages=['step_crawler'],
    install_requires=['inspect', 'cssify', 'selenium', 'asyncio', 'copy',
                      'pyppeteer']
)
