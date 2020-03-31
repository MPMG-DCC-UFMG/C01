import selenium
import os
import time

import urllib.parse

from selenium import webdriver
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

FOLDER_PATH = "coleta"

JTR_IDENTIFIER = 402
TRF2_URL = "http://portal.trf2.jus.br/portal/consulta/cons_procs.asp"

FIRST_YEAR = 1989
LAST_YEAR = 2019

ORIGINS = [0, 9999]
MAX_SEQ = 9999999

DEBUG = True
PRINTING_INTERVAL = 5000

RETRY_LIMIT = 100
WAIT_INTERVAL = 2


def init_driver(headless=True, timeout=30):
    """
    Initializes the Firefox Driver

    :param headless: if set to true, no window is rendered by Selenium
    :param timeout: number of seconds to wait for a page to load
    :return: the configured driver
    """

    if not os.path.exists(FOLDER_PATH):
        os.makedirs(FOLDER_PATH)

    fp = webdriver.FirefoxProfile()
    # Download files inside a folder called tmp in the current dir
    fp.set_preference("browser.download.dir", os.path.join(os.getcwd(), 'tmp'))
    fp.set_preference("browser.download.defaultFolder", os.path.join(os.getcwd(), 'tmp'))

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
            time.sleep(WAIT_INTERVAL * tries)

    if tries >= RETRY_LIMIT:
        raise Exception("Couldn't reach {}".format(url))

    return driver


def verif_code(num_proc):
    """
    Calculates the verificaton code for a given process number

    :param num_proc: the process number for which to generate the code
    :returns: the verif number for the supplied code
    """
    num_proc = int(num_proc)
    val = 98 - ((num_proc * 100) % 97)

    return val


def build_from_data(year, origin, sequence):
    """
    Generates a process code from its parameters

    :param year: year of the related process
    :param origin: identifier for the originating unit for this process
    :param sequence: sequential identifier for the process
    :returns: the corresponding process with its verifying digits
    """

    p_fmt = "{:07d}{:04d}{:03d}{:04d}"
    ver_code = verif_code(p_fmt.format(sequence, year, JTR_IDENTIFIER, origin))

    res_fmt = "{:07d}{:02d}{:04d}{:03d}{:04d}"
    return res_fmt.format(sequence, ver_code, year, JTR_IDENTIFIER, origin)


def generate_codes(first_year, last_year):
    """
    Generates all the codes to be downloaded

    :returns: a generator instance which iterates over all possible codes
    """

    for year in range(first_year, last_year + 1):
        for origin in ORIGINS:
            for n in range(0, MAX_SEQ + 1):
                yield build_from_data(year, origin, n)


def check_number(driver, num_proc):
    """
    Checks if a given number is a hit or a miss

    :param driver: a Firefox driver for Selenium
    :param num_proc: the process number to try
    :returns: true if the checked number was hit, false if it missed
    """

    driver = load_or_retry(driver, TRF2_URL)
    
    # process number input
    loaded = False
    while not loaded:
        try:
            elem = driver.find_element_by_name("NumProc")
            loaded = True
        except:
            # there has been some internal server error, try again
            driver = load_or_retry(driver, TRF2_URL)

    elem.clear()
    elem.send_keys(num_proc)

    # Checks the box to download everything
    elem = driver.find_element_by_name("baixado")
    elem.click()
    
    # CAPTCHA "solving"
    elem = driver.find_element_by_id("gabarito")
    catpcha_sol = elem.get_attribute("value")

    # Entering the CAPTCHA result
    if len(catpcha_sol) > 0:
        # Writes the result
        elem = driver.find_element_by_name("captchacode")
        elem.send_keys(catpcha_sol)
    else:
        # Checks the "none" box
        elem = driver.find_element_by_name("nenhum")
        elem.click()

    # Search
    elem = driver.find_element_by_name("Pesquisar")
    elem.click()

    if "cons_procs" in driver.current_url:
        return False
    else:
        return True


def download_page(driver, num_proc, counter):
    """
    Downloads the page for a given process if it hits a detail page

    :param driver: a Firefox driver for Selenium
    :param num_proc: the process number to try
    :returns: true if the checked number was hit, false if it missed
    """

    driver = load_or_retry(driver, TRF2_URL)
    
    # process number input
    loaded = False
    while not loaded:
        try:
            elem = driver.find_element_by_name("NumProc")
            loaded = True
        except:
            # there has been some internal server error, try again
            driver = load_or_retry(driver, TRF2_URL)

    elem.clear()
    elem.send_keys(num_proc)

    # Checks the box to download everything
    elem = driver.find_element_by_name("baixado")
    elem.click()
    
    # CAPTCHA "solving"
    elem = driver.find_element_by_id("gabarito")
    catpcha_sol = elem.get_attribute("value")

    # Entering the CAPTCHA result
    if len(catpcha_sol) > 0:
        # Writes the result
        elem = driver.find_element_by_name("captchacode")
        elem.send_keys(catpcha_sol)
    else:
        # Checks the "none" box
        elem = driver.find_element_by_name("nenhum")
        elem.click()

    # Search
    elem = driver.find_element_by_name("Pesquisar")
    elem.click()

    if "cons_procs" in driver.current_url:
        return False
    else:
        els = driver.find_elements_by_xpath("/html/body/form/center/div/table[3]/tbody/tr[1]/td/table/tbody/tr/td[2]/p/font/span/a")
        counter = 0
        for el in els:
            el.click()
            counter += 1

            time.sleep(2)
            driver.switch_to.frame("dir")

            is_nested = False

            if counter == 1:
                prev_btn = driver.find_elements_by_link_text("Anterior")
                # rewind to first page
                while len(prev_btn) > 0:
                    button = prev_btn[0]
                    button.click()
                    time.sleep(1)
                    prev_btn = driver.find_elements_by_link_text("Anterior")

                # now we're at the first page
                file_name = os.path.join(FOLDER_PATH, str(num_proc) + "-" + str(counter) + "-1.html")
                with open(file_name, 'w') as html_file:
                    html_file.write(driver.page_source)

                next_btn = driver.find_elements_by_link_text("Próxima")
                # follow to next pages
                page_counter = 1
                while len(next_btn) > 0:
                    page_counter += 1
                    button = next_btn[0]
                    button.click()
                    time.sleep(1)
                    file_name = os.path.join(FOLDER_PATH, str(num_proc) + "-" + str(counter) + "-" + str(page_counter) + ".html")
                    with open(file_name, 'w') as html_file:
                        html_file.write(driver.page_source)
                    next_btn = driver.find_elements_by_link_text("Próxima")


            else:
                inner_frame = driver.find_elements_by_css_selector("iframe")
                if len(inner_frame) > 0:
                    driver.switch_to.frame(inner_frame[0])
                    file_name = os.path.join(FOLDER_PATH, str(num_proc) + "-" + str(counter) + ".html")
                    with open(file_name, 'w') as html_file:
                        html_file.write(driver.page_source)

            driver.switch_to.default_content()
            time.sleep(2)

        return True


def main():
    driver = init_driver(True)

    """for year in range(FIRST_YEAR, LAST_YEAR + 1):
        hits = 0
        misses = 0
        last_working = 0
        print("{}:\n\n".format(year))
        for origin in ORIGINS:
            origin_hits = 0
            origin_misses = 0
            origin_last_working = 0
            for n in range(0, MAX_SEQ + 1):
                code = build_from_data(year, origin, n)
                was_hit = check_number(driver, code)

                if n % PRINTING_INTERVAL == 0 and DEBUG:
                    print(code)

                if was_hit:
                    origin_hits += 1
                    origin_last_working = code
                else:
                    origin_misses += 1

            hits += origin_hits
            misses += origin_misses
            if origin_hits > 0:
                last_working = origin

            fmt_str = "--- Status for origin {}: H: {} / M: {}, LW: {} "

            print(fmt_str.format(origin, origin_hits, origin_misses,
                    origin_last_working))

        fmt_str = "H: {} / M: {}, LW: {} "
        print("\nData for {}:".format(year))
        print(fmt_str.format(hits, misses, last_working))
        print("\n")"""


    hit = 0
    miss = 0
    counter = 0
    for code in generate_codes(FIRST_YEAR, LAST_YEAR):
        if download_page(driver, code, counter):
            hit += 1
        else:
            miss += 1

        if counter % PRINTING_INTERVAL == 0:
            print("{}".format(code))
            print("H {} / M {}".format(hit, miss))

        counter += 1

    time.sleep(5)

    driver.close()

if __name__ == "__main__":
    main()
