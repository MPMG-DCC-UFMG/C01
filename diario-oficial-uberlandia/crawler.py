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

DOC_URL_BEFORE_2018 = "https://www.uberlandia.mg.gov.br/{}/{}/?post_type=diario_oficial"
DOC_URL_AFTER_2018 = "https://www.uberlandia.mg.gov.br/{}/{}/?post_type=diariooficial"

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


def generate_urls(first_year, last_year):
    """
    Generates all the urls to be downloaded

    :returns: a generator instance which iterates over all possible urls
    """

    # The urls for before and after 2018 are different
    for year in range(first_year, 2018):
        for month in range(1, 13):
            yield DOC_URL_BEFORE_2018.format(year, month)


    for year in range(2018, last_year + 1):
        for month in range(1, 13):
            yield DOC_URL_AFTER_2018.format(year, month)


def download_pdfs_url(driver, url):
    """
    Downloads the PDF files for a given url (which is given by a month/year
    combination)

    :param driver: a Firefox driver for Selenium
    :param url: the url to get the files from
    :return: True if there was data for this period, False otherwise
    """

    driver = load_or_retry(driver, url)

    finished = False

    while True:
        # Get all the PDF links in page
        elems = driver.find_elements_by_css_selector(\
            "section article a.elementor-post__read-more")

        num_elems = len(elems)

        if len(elems) == 0:
            return False

        list_url = driver.current_url
        for el in range(num_elems):
            # Get all the PDF links in page again (page might have been
            # refreshed)
            elems = driver.find_elements_by_css_selector(\
                "section article a.elementor-post__read-more")
            link_href = elems[el].get_attribute("href")
            try:
                # This should download the file, but this url also hangs the
                # driver, so we wrap it around a try/except block to catch the
                # timeout exception
                driver.get(link_href)
            except:
                pass

            load_or_retry(driver, list_url)
            time.sleep(1)

        next_button = driver.find_elements_by_css_selector("a.page-numbers.next")
        if len(next_button) != 0:
            # go to next page
            curr_url = driver.current_url
            next_button[0].click()
            wait = WebDriverWait(driver, 10)
            wait.until(lambda driver: driver.current_url != curr_url)
        else:
            # there is no next page, finish
            return True

def countEntries(driver, url):
    """
    Counts the amount of PDF files for a given url

    :param driver: a Firefox driver for Selenium
    :param url: the url in which to look for the files
    :return: Number of entries for this period
    """

    driver = load_or_retry(driver, url)

    finished = False

    total = 0

    while True:
        # Get all the PDF links in page
        elems = driver.find_elements_by_css_selector(\
            "section article a.elementor-post__read-more")

        total += len(elems)
        time.sleep(1)

        if len(elems) == 0:
            return total

        next_button = driver.find_elements_by_css_selector("a.page-numbers.next")
        if len(next_button) != 0:
            # go to next page
            next_button[0].click()
        else:
            # there is no next page, finish
            return total



def main():
    driver = init_driver(True, 30)

    for url in generate_urls(2005, 2020):
        download_pdfs_url(driver, url)
        print(url)

    driver.close()

if __name__ == "__main__":
    main()
