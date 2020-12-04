import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='antiblock_drivers',
    version='0.1',
    scripts=[],
    author="Lucas Augusto",
    author_email="luc.aug.freire@gmail.com",
    description=("A general request wrapper for antiblock mechanisms"),
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3"
    ],
    install_requires=['requests'],
)
