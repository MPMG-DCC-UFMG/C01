"""This module contains the packaging routine for the pybook package"""
import pathlib
import pkg_resources

from setuptools import setup, find_packages
try:
    # pip >=20
    from pip._internal.network.session import PipSession
    from pip._internal.req import parse_requirements
except ImportError:
    try:
        # 10.0.0 <= pip <= 19.3.1
        from pip._internal.download import PipSession
        from pip._internal.req import parse_requirements
    except ImportError:
        # pip <= 9.0.3
        from pip.download import PipSession
        from pip.req import parse_requirements


def get_requirements(source):
    """Get the requirements from the given ``source``

    Parameters
    ----------
    source: str
        The filename containing the requirements

    """
    with pathlib.Path(source).open() as requirements_txt:
        install_requires = [
            str(requirement)
            for requirement
            in pkg_resources.parse_requirements(requirements_txt)
        ]
    return install_requires


setup(
    packages=find_packages(),
    install_requires=get_requirements('requirements/requirements.txt'),
    entry_points={
        'console_scripts': [
            'scrapyp = scrapy_puppeteer.cli:__main__',
        ],
    }
)


