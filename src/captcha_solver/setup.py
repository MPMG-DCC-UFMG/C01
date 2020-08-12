import setuptools
from setuptools import setup


with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='captcha_solver',
    version='1.0',
    description='Module to solver captchas',
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    author='Rennan Cordeiro',
    author_email='rennanl@ufmg.br',
    packages=setuptools.find_packages(),
    install_requires=["certifi", "chardet", "cycler", "decorator", "idna",
                      "imagecodecs", "imageio", "kiwisolver", "lxml", "matplotlib",
                      "networkx", "numpy", "opencv-python", "Pillow", "pyparsing",
                      "pytesseract", "python-dateutil", "PyWavelets", "requests",
                      "scikit-image", "scipy", "selenium", "six", "SpeechRecognition",
                      "tifffile", "urllib3", "validators"]
)
