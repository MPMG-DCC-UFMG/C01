import setuptools
from setuptools import setup


with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='crawled_request_filter',
    version='0.1',
    description='Module to filter duplicated requests',
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    author='Elves Rodrigues',
    packages=setuptools.find_packages(),
    # In production we may want to use the psycopg2 package itself, I'm using
    # the psycopg2-binary package here to avoid problems with external
    # libraries
    install_requires=["psycopg2-binary", "redis"]
)
