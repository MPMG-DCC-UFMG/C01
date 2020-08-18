import logging

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions


BASE_FOLDER = "/br.gov.mg.lavras/licitacoes"
DOWNLOAD_DIR = "/Volumes/Work HD/MPMG"

PROFILE_PATH = "/Users/work/Library/Application Support/Firefox/Profiles/" \
               "yde1eaqi.mpmg"

# 1721 - 1729
# 1916 - 1919
# 2023 - 2029
START_PROCESS = 1
MAX_PROCESSES = 5000

MAX_SKIPPED_IDS = 20

START_URL = "http://187.60.128.132:8082/portalcidadao/#78c3e513dd43cb27d8a" \
            "3e2f376196ffc656d7ea577b2c6fb4e0e266bf16d9ca2233%C4%B63605504" \
            "ffedd94fb65b8146c82bd22841763a4457569e937a8372cb01473df21c376" \
            "fcceb58f3c2a07c1a18048a34dd85fb547eb77f9cfe8123884287156ef4c6" \
            "6513f9dd55741dff02ac39faa0c7f257690651bc53f168a95a8bb14e2600e" \
            "c0564398cdd0e93fadc74b9102fed15d79c04b0eeac5a935504dc8bb3f02b8" \
            "0e8b451373f5417be3badcdf8dc1deb1cb477bacd9b3d345d3cb7a24cbf7ec" \
            "4b73a9596f32054958f18eff757f4ad647a17a3e6ae51059e1"

MAX_RETRIES = 10
WAIT_INTERVAL = 30
WEBDRIVER_DELAY = 90

MAX_RESULTS_FIELD = '/html/body/div[7]/div[1]/div[1]/div[2]/div/div[2]/div[10]/input'
SORT_BUTTON = '//*[@id="gwt-uid-127"]'
SUBMIT_BUTTON = '/html/body/div[7]/div[1]/div[1]/div[2]/div/div[2]/div[11]/button'
FIRST_RESULT = "/html/body/div[7]/div[1]/div[1]/div[2]/div/div[3]/table/tbody/tr[2]/" \
               "td/div/table/tbody/tr/td/table/tbody/tr[2]/td[1]/a"


def set_options_firefox():
    firefox_options = FirefoxOptions()
    firefox_options.add_argument("--headless")
    firefox_options.add_argument("--window-size=1920x1080")
    firefox_options.add_argument("--disable-notifications")
    firefox_options.add_argument('--no-sandbox')
    firefox_options.add_argument('--verbose')
    firefox_options.add_argument('--disable-gpu')
    firefox_options.add_argument('--disable-software-rasterizer')
    firefox_options.set_preference("browser.download.manager.showWhenStarting", False)
    firefox_options.set_preference('browser.helperApps.neverAsk.openFile', "application/pdf")
    firefox_options.set_preference('browser.helperApps.neverAsk.saveToDisk', "application/pdf")
    firefox_options.set_preference('browser.helperApps.neverAsk.openFile', "application/zip")
    firefox_options.set_preference('browser.helperApps.neverAsk.saveToDisk', "application/zip")
    firefox_options.set_preference('browser.helperApps.neverAsk.openFile', "application/msword")
    firefox_options.set_preference('browser.helperApps.neverAsk.saveToDisk', "application/msword")
    firefox_options.set_preference("pdfjs.disabled", "true")
    return firefox_options


def set_options_chrome():
    chrome_options = ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--verbose')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument("user-agent=python3.6")
    chrome_options.add_argument('--disable-software-rasterizer')
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": DOWNLOAD_DIR,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing_for_trusted_sources_enabled": False,
        "safebrowsing.enabled": False
    })
    return chrome_options


def get_driver(profile_path=PROFILE_PATH, browser='firefox'):
    if browser == 'firefox':
        firefox_options = set_options_firefox()
        if profile_path:
            return webdriver.Firefox(firefox_profile=profile_path, options=firefox_options)
        else:
            return webdriver.Firefox(options=firefox_options)
    elif browser == 'chrome':
        chrome_options = set_options_chrome()
        return webdriver.Chrome(chrome_options=chrome_options, executable_path="/usr/local/bin/chromedriver")
    else:
        return None


def set_logging():
    logging.basicConfig(level=logging.INFO)
