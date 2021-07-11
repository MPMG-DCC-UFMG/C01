#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Chromium download module."""

""""

Light adaptation from https://github.com/pyppeteer/pyppeteer/blob/dev/pyppeteer/chromium_downloader.py
This was necessary because it is necessary to change the chromium version, which in pyppeter is via OS environment variable. 
However, it is not possible to do this automatically in python.

Pyppeteer uses chromium version incompatible 
"""

from io import BytesIO
import logging
import os
from pathlib import Path
import stat
import sys
from zipfile import ZipFile
from pyppeteer.launcher import executablePath

import urllib3
from tqdm import tqdm

from pyppeteer import __chromium_revision__, __pyppeteer_home__

logger = logging.getLogger(__name__)

DOWNLOADS_FOLDER = os.path.join(os.getcwd(), 'local-chromium') 

DOWNLOAD_HOST = 'https://storage.googleapis.com'

BASE_URL = f'{DOWNLOAD_HOST}/chromium-browser-snapshots'

REVISION = '898323'

NO_PROGRESS_BAR = False  # type: ignore

# Windows archive name changed at r591479.
windowsArchive = 'chrome-win' if int(REVISION) > 591479 else 'chrome-win32'

downloadURLs = {
    'linux': f'{BASE_URL}/Linux_x64/{REVISION}/chrome-linux.zip',
    'mac': f'{BASE_URL}/Mac/{REVISION}/chrome-mac.zip',
    'win32': f'{BASE_URL}/Win/{REVISION}/{windowsArchive}.zip',
    'win64': f'{BASE_URL}/Win_x64/{REVISION}/{windowsArchive}.zip',
}

chromiumExecutable = {
    'linux': f'{DOWNLOADS_FOLDER}/{REVISION}/chrome-linux/chrome',
    'mac': f'{DOWNLOADS_FOLDER}/{REVISION}/chrome-mac/Chromium.app/Contents/MacOS/Chromium',
    'win32': f'{DOWNLOADS_FOLDER}/{REVISION}/{windowsArchive}/chrome.exe',
    'win64': f'{DOWNLOADS_FOLDER}/{REVISION}/{windowsArchive}/chrome.exe',
}

def current_platform() -> str:
    """Get current platform name by short string."""
    if sys.platform.startswith('linux'):
        return 'linux'
    elif sys.platform.startswith('darwin'):
        return 'mac'
    elif (sys.platform.startswith('win') or
          sys.platform.startswith('msys') or
          sys.platform.startswith('cyg')):
        if sys.maxsize > 2 ** 31 - 1:
            return 'win64'
        return 'win32'
    raise OSError('Unsupported platform: ' + sys.platform)


def get_url() -> str:
    """Get chromium download url."""
    return downloadURLs[current_platform()]


def download_zip(url: str) -> BytesIO:
    """Download data from url."""
    logger.warning('Starting Chromium download. '
                   'Download may take a few minutes.')

    # Uncomment the statement below to disable HTTPS warnings and allow
    # download without certificate verification. This is *strongly* as it
    # opens the code to man-in-the-middle (and other) vulnerabilities; see
    # https://urllib3.readthedocs.io/en/latest/advanced-usage.html#tls-warnings
    # for more.
    # urllib3.disable_warnings()

    with urllib3.PoolManager() as http:
        # Get data from url.
        # set preload_content=False means using stream later.
        r = http.request('GET', url, preload_content=False)
        if r.status >= 400:
            raise OSError(f'Chromium downloadable not found at {url}: '
                          f'Received {r.data.decode()}.\n')

        # 10 * 1024
        _data = BytesIO()
        if NO_PROGRESS_BAR:
            for chunk in r.stream(10240):
                _data.write(chunk)
        else:
            try:
                total_length = int(r.headers['content-length'])
            except (KeyError, ValueError, AttributeError):
                total_length = 0
            process_bar = tqdm(total=total_length)
            for chunk in r.stream(10240):
                _data.write(chunk)
                process_bar.update(len(chunk))
            process_bar.close()

    logger.warning('\nChromium download done.')
    return _data


def extract_zip(data: BytesIO, path: Path) -> None:
    """Extract zipped data to path."""
    # On mac zipfile module cannot extract correctly, so use unzip instead.
    if current_platform() == 'mac':
        import subprocess
        import shutil
        zip_path = path / 'chrome.zip'
        if not path.exists():
            path.mkdir(parents=True)
        with zip_path.open('wb') as f:
            f.write(data.getvalue())
        if not shutil.which('unzip'):
            raise OSError('Failed to automatically extract chromium.'
                          f'Please unzip {zip_path} manually.')
        proc = subprocess.run(
            ['unzip', str(zip_path)],
            cwd=str(path),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        if proc.returncode != 0:
            logger.error(proc.stdout.decode())
            raise OSError(f'Failed to unzip {zip_path}.')
        if chromium_executable().exists() and zip_path.exists():
            zip_path.unlink()
    else:
        with ZipFile(data) as zf:
            zf.extractall(str(path))

    exec_path = chromium_executable()
    if not os.path.exists(exec_path):
        raise IOError('Failed to extract chromium.')

    os.chmod(exec_path, os.stat(exec_path).st_mode  | stat.S_IXOTH | stat.S_IXGRP | stat.S_IXUSR)

    logger.warning(f'chromium extracted to: {path}')

def download_chromium() -> None:
    """Download and extract chromium."""
    extract_zip(download_zip(get_url()), f'{DOWNLOADS_FOLDER}/{REVISION}')

def chromium_executable() -> Path:
    """Get path of the chromium executable."""

    executable = chromiumExecutable[current_platform()]

    if not os.path.exists(executable):
        download_chromium()    

    return executable
