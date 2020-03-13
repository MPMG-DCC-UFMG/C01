import selenium
import os
import time

from selenium import webdriver
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

DOC_URL = "https://pocosdecaldas.mg.gov.br/transparencia/diario-oficial-do-municipio/"

DEBUG = True

RETRY_LIMIT = 10

def init_driver(headless=True, timeout=30):
    """
    Initializes the Firefox Driver

    :param headless: if set to true, no window is rendered by Selenium
    :param timeout: number of seconds to wait for a page to load
    :return: the configured driver
    """

    fp = webdriver.FirefoxProfile()
    # Download files inside a folder called tmp in the current dir
    fp.set_preference("browser.download.folderList", 2)
    fp.set_preference("browser.download.dir", os.path.join(os.getcwd(), 'tmp'))
    fp.set_preference("browser.download.defaultFolder", os.path.join(os.getcwd(), 'tmp'))
    fp.set_preference("pdfjs.disabled", True)
    fp.set_preference("plugin.scan.Acrobat", "99.0");
    fp.set_preference("plugin.scan.plid.all", False);
    fp.set_preference("browser.download.manager.showWhenStarting", False)
    fp.set_preference("browser.download.manager.focusWhenStarting", False)
    fp.set_preference("browser.download.manager.closeWhenDone", True)
    fp.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/pdf");
    fp.set_preference("dom.max_script_run_time", 1)

    options = Options()
    options.headless = headless

    driver = webdriver.Firefox(options=options, firefox_profile=fp)
    driver.set_page_load_timeout(timeout)
    return driver


def load_or_retry(driver, url):
    """
    Tries to GET the supplied url using the driver

    :param driver: the driver to access the page from
    :param url: url to load
    :returns: the driver in the desired url
    """
    tries = 0

    # tries the required number of times
    while tries < RETRY_LIMIT:
        try:
            # leaves the loop if URL is correctly loaded
            driver.get(url)
            break
        except:
            tries += 1

    if tries >= RETRY_LIMIT:
        raise Exception("Couldn't reach {}".format(url))

    return driver


def download_pdfs_url(driver, url):
    """
    Downloads the PDF files for the given url

    :param driver: a Firefox driver for Selenium
    :param url: the url to get the files from
    """

    driver = load_or_retry(driver, url)

    main_page_sel = "article > .inner-article > .entry-text > p a"

    driver.find_element_by_css_selector(main_page_sel).click()

    time.sleep(10)

    entry_limit_formset = driver.\
        find_elements_by_css_selector(".form-horizontal .form-group")[4]
    entry_limit_form = entry_limit_formset.\
        find_element_by_css_selector(".form-control")
    entry_limit_form.clear()
    entry_limit_form.send_keys("100000")

    send_button = driver.find_element_by_css_selector(".form-horizontal button")
    send_button.click()

    time.sleep(5)

    down_btn_selector = ".main .main-body table table .link i.fa.fa-download"

    WebDriverWait(driver, 30).until(\
        EC.presence_of_element_located((By.CSS_SELECTOR, down_btn_selector))\
        ) 

    down_btns = driver.find_elements_by_css_selector(down_btn_selector)

    for btn in down_btns:
        btn.click()
        time.sleep(2)

    time.sleep(60)


def main():
    driver = init_driver(True, 30)

    download_pdfs_url(driver, DOC_URL)

    driver.close()

if __name__ == "__main__":
    main()
