from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import hashlib
import os
from urllib.parse import urlparse
import requests


class StopDownload(Exception):
    """Used in func file_larger_than_giga"""
    pass

def file_larger_than_giga(url):
    # Mudar user-agent para evitar ser bloqueado por usar a biblioteca requests
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36'}
    
    # requisição apenas para obter o cabeçalho do conteúdo a ser baixado
    response = requests.head(url, allow_redirects=True, headers=headers)

    # obtem o tamanho do arquivo e converte para inteiro
    content_length = int(response.headers['Content-Length'])

    return content_length > 1e9


def get_url_domain(url):
    parsed_uri = urlparse(url)
    result = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
    return result


def hash(byte_content):
    """Returns the md5 hash of a bytestring."""
    return hashlib.md5(byte_content).hexdigest()

# leave as 'chromedriver' if driver is on path
CHROME_WEBDRIVER_PATH = 'chromedriver'
# CHROME_WEBDRIVER_PATH = "D:/Users/gabri/Documents/GitHub/C04/src/" \
#   "crawling_utils/crawling_utils/chromedriver_win32_chr_83.exe"
# leave as 'geckodriver' if driver is on path
FIREFOX_WEBDRIVER_PATH = 'geckodriver'
# FIREFOX_WEBDRIVER_PATH = "D:/Users/gabri/Documents/GitHub/C04/src/" \
#   "crawling_utils/crawling_utils/geckodriver_v0_27_0_win_64.exe"


def check_file_path(path):
    """Makes sure that folders in path exist."""
    try:
        os.makedirs(path)
    except FileExistsError:
        pass


def init_webdriver(
    driver_type: str = "chrome",
    headless: bool = True,
    arguments: list = ['--window-size=1420,1080'],
) -> webdriver.chrome.webdriver.WebDriver:

    if driver_type == "chrome":
        options = webdriver.ChromeOptions()
        if headless:
            for args in ['--no-sandbox', '--headless', '--disable-gpu']:
                arguments.append(args)

    elif driver_type == "firefox":
        options = webdriver.firefox.options.Options()
        if headless:
            pass

    else:
        raise ValueError("Invalid driver type")

    for argument in arguments:
        options.add_argument(argument)

    if driver_type == "chrome":
        return webdriver.Chrome(
            executable_path=CHROME_WEBDRIVER_PATH,
            options=options
        )

    else:
        return webdriver.Firefox(
            executable_path=FIREFOX_WEBDRIVER_PATH,
            options=options
        )


def test_webdriver(driver):
    driver.get("http://www.python.org")
    assert "Python" in driver.title
    elem = driver.find_element_by_name("q")
    elem.clear()
    elem.send_keys("pycon")
    elem.send_keys(Keys.RETURN)
    assert "No results found." not in driver.page_source
    time.sleep(5)
    driver.close()


def test_init_firefox_webdriver():
    test_webdriver(init_webdriver("firefox"))


def test_init_chrome_webdriver():
    test_webdriver(init_webdriver("chrome"))


if __name__ == "__main__":
    test_webdriver(init_webdriver("firefox", headless=False))
    test_webdriver(init_webdriver("chrome", headless=False))
