import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='scrapy_puppeteer',
    version='1.0',
    description='Module that integrates Scrapy and Puppeteer',
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    author='Rennan Cordeiro',
    author_email='rennanl@ufmg.br',
    packages=setuptools.find_packages(),
    install_requires=['scrapy>=1.0.0', 'promise', 'pyppeteer==0.2.6',
                      'requests', 'twisted', 'python-magic',
                      'websockets==9.1', 'pyee==8.2.2'],
                     'requests', 'twisted', 'python-magic',
                     'websockets==9.1', 'pyee==8.2.2'],
    entry_points={
        'console_scripts': [
            'scrapyp = scrapy_puppeteer.cli:__main__',
        ],
    }
)
