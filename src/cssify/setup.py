from setuptools import setup


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='cssify',
    version='1.1',
    description='Convert XPATH locators to CSS',
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    author='Santiago Suarez Ordonez',
    author_email='santiycr@gmail.com',
    packages=['cssify'],
)

