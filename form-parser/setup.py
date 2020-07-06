from setuptools import setup


with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='Form Parser',
    version='1.0',
    description='Module for parsing HTML forms',
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    author='Rubia Guerra',
    author_email='rubia-rg@users.noreply.github.com',
    packages=['formparser'],
    install_requires=['lxml', 'requests', 'selenium', 'entry_probing']
)
