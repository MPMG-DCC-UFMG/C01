import logging

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions


BASE_FOLDER = "/br.gov.mg.pocosdecaldas/licitacoes"
DOWNLOAD_DIR = "/Volumes/Work HD/MPMG"

PROFILE_PATH = "/Users/work/Library/Application Support/Firefox/Profiles/yde1eaqi.mpmg"

START_PROCESS = 39
MAX_PROCESSES = 4000

MAX_SKIPPED_IDS = 20

START_URL = "http://187.49.207.14:8081/portalcidadao/#78c3e513dd43cb27d8a3e2f376196ffc656d7ea577b2c6fbae696bb4f" \
            "e4e5639b796%C5%A690e87f4d63047fdd72ee224f99bf38dc8950906afc423ff6853c05e0a11a2f886c31119c58b6298c4" \
            "2fc9af04c84c6f1a52a741a1e66bf2e691388cd2a945d3362feb4b2aa570e068e90a9b811d197c088f07777e90419980e4" \
            "93642fbe6a4b75e31164bb2c70f08f308f28a9ad1142ec1a016f8453ed9c18ec7d19212daad26019a707cedb449c83bfc1" \
            "b3f31ad3d609ad126923dc87f6a4ea6a6c438e38107134f58a903a4ab4b9da16a974c4907e8c179e545586"

MAX_RETRIES = 10
WAIT_INTERVAL = 30
WEBDRIVER_DELAY = 90

MAX_RESULTS_FIELD = '/html/body/div[5]/div[1]/div[1]/div[2]/div/div[2]/div[10]/input'
SORT_BUTTON = '//*[@id="gwt-uid-122"]'
SUBMIT_BUTTON = '/html/body/div[5]/div[1]/div[1]/div[2]/div/div[2]/div[11]/button'
FIRST_RESULT = "/html/body/div[5]/div[1]/div[1]/div[2]/div/div[3]/table/tbody/tr[2]/" \
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
