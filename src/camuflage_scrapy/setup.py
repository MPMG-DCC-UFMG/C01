import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='antiblock_scrapy',
    version='0.1',
    scripts=[],
    author="Elves Rodrigues",
    author_email="elvesmateusrodrigues@gmail.com",
    description="Mecanismos antibloqueios para o Scrapy",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    install_requires=["toripchanger", "scrapy-rotating-proxies"]
)
