from setuptools import setup


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='step_crawler',
    version='1.0',
    description='Module creating step by step crawlers',
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    author='Tales Panoutsos',
    author_email='TalesPanoutsos@users.noreply.github.com',
    packages=['step_crawler'],
    install_requires=['selenium', 'asyncio', 'pyppeteer==0.2.6',
                      'pyext', 'pillow']
)
