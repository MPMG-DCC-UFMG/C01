from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import hashlib
import os
import sys
from urllib.parse import urlparse
import requests
from datetime import datetime

SERVER_ADDRESS = os.getenv('SERVER_ADDRESS', 'http://localhost:8000')

SERVER_NEW_PAGE_FOUND_API = SERVER_ADDRESS + '/download/pages/found/{instance_id}/{num_pages}'
SERVER_PAGE_CRAWLED_API = SERVER_ADDRESS + '/download/page/{message}/{instance_id}'

SERVER_FILES_FOUND_API = SERVER_ADDRESS + '/download/files/found/{instance_id}/{num_files}'
SERVER_FILE_DOWNLOADED_API = SERVER_ADDRESS + '/download/file/{message}/{instance_id}'

SERVER_SESSION = requests.sessions.Session()

class StopDownload(Exception):
    """Used in func file_larger_than_giga"""
    pass


def file_larger_than_giga(url):
    # Mudar user-agent para evitar ser bloqueado por usar a biblioteca requests
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36'}

    # requisição apenas para obter o cabeçalho do conteúdo a ser baixado
    response = requests.head(url, allow_redirects=True, headers=headers)

    # obtem o tamanho do arquivo e converte para inteiro
    content_length = response.headers.get('Content-Length')
    if content_length is None:
        return True

    content_length = int(content_length)

    return content_length > 1e9


def get_url_domain(url):
    parsed_uri = urlparse(url)
    result = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
    return result


def hash(byte_content):
    """Returns the md5 hash of a bytestring."""
    return hashlib.md5(byte_content).hexdigest()


def notify_server(notification_url: str):
    req = SERVER_SESSION.get(notification_url)

    if req.status_code == 200:
        print(f'[{datetime.now()}] Server Crawled Data Notifier: Server notified successfully')

    else:
        print(f'[{datetime.now()}] Server Crawled Data Notifier: Error notifying server')


def notify_new_page_found(instance_id: str, num_pages: int = 1):
    server_notification_url = SERVER_NEW_PAGE_FOUND_API.format(
        instance_id=instance_id, num_pages=num_pages)
    notify_server(server_notification_url)


def notify_page_crawled_successfully(instance_id: str):
    server_notification_url = SERVER_PAGE_CRAWLED_API.format(
        message='success', instance_id=instance_id)
    notify_server(server_notification_url)

def notify_page_previously_crawled(instance_id: str):
    server_notification_url = SERVER_PAGE_CRAWLED_API.format(
        message='previously_crawled', instance_id=instance_id)
    notify_server(server_notification_url)

def notify_page_crawled_with_error(instance_id: str):
    server_notification_url = SERVER_PAGE_CRAWLED_API.format(
        message='error', instance_id=instance_id)
    notify_server(server_notification_url)


def notify_page_duplicated_found(instance_id: str):
    server_notification_url = SERVER_PAGE_CRAWLED_API.format(
        message='duplicated', instance_id=instance_id)
    notify_server(server_notification_url)


def notify_files_found(instance_id: str, num_files: int):
    server_notification_url = SERVER_FILES_FOUND_API.format(
        instance_id=instance_id, num_files=num_files)
    notify_server(server_notification_url)


def notify_file_downloaded_successfully(instance_id: str):
    server_notification_url = SERVER_FILE_DOWNLOADED_API.format(
        message='success', instance_id=instance_id)
    notify_server(server_notification_url)

def notify_file_previously_crawled(instance_id: str):
    server_notification_url = SERVER_FILE_DOWNLOADED_API.format(
        message='previously_crawled', instance_id=instance_id)
    notify_server(server_notification_url)

def notify_file_downloaded_with_error(instance_id: str):
    server_notification_url = SERVER_FILE_DOWNLOADED_API.format(
        message='error', instance_id=instance_id)
    notify_server(server_notification_url)


def system_is_deploying() -> bool:
    '''
    Check whether the system is running via Django's 'makemigrations',
    'migrate' or 'collectstatic' commands

    Returns:
        Returns True if the system is running via one of the aforementioned
        commands, False otherwise.
    '''
    return 'makemigrations' in sys.argv or 'migrate' in sys.argv or \
        'collectstatic' in sys.argv

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
