import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='entry_probing',  
    version='0.1',
    scripts=[] ,
    author="Lucas Augusto",
    author_email="luc.aug.freire@gmail.com",
    description="A probing module for HTTP pages",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3"
    ],
 )
