from setuptools import setup, find_packages


with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='formparser',
    version='1.0',
    description='Module for parsing HTML forms',
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    author='Rubia Guerra',
    author_email='rubia-rg@users.noreply.github.com',
    packages=find_packages(),
    install_requires=['lxml', 'requests', 'selenium', 'entry_probing',
                      'asyncio', 'pyppeteer']
)
