import setuptools
from setuptools import setup

setup(
    name='messenger',
    version='1.0',
    description="Module to send and receives messages from Kafka",
    license="MIT",
    author='Elves Rodrigues',
    packages=setuptools.find_packages(),
    install_requires=['kafka-python==1.4.3', 'typing-extensions==4.3.0', 'ujson==5.1.0', 'scutils==1.3.0dev6']
)
