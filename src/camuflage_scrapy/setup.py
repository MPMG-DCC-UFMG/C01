import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='camuflage_scrapy',
    version='0.1',
    scripts=[],
    author="Elves Rodrigues",
    description=("A scrapy middleware implementing antiblock mechanisms"),
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3"
    ],
    install_requires=['scrapy', 'requests', 'stem'],
)
