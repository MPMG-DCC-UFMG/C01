import selenium
import os
import shutil
import sys
import time

from joblib import Parallel, delayed

import urllib.parse

from selenium import webdriver
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver import ActionChains
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

FOLDER_PATH = "coleta"

JTR_IDENTIFIER = 402
TRF2_URL = "http://portal.trf2.jus.br/portal/consulta/cons_procs.asp"

FIRST_YEAR = 2014
LAST_YEAR = 2020

ORIGINS = [0, 9999]
MAX_SEQ = 9999999

#DEBUG = True
#PRINTING_INTERVAL = 5000

MIN_MISS_SEQ = 100

RETRY_LIMIT = 100
WAIT_INTERVAL = 2

DOWNLOAD_ATTACHMENTS = True

DOWNLOAD_FOLDER = os.path.join("/datalake/ufmg/coletatrf2", FOLDER_PATH)
TMP_DOWNLOAD = os.path.join(os.getcwd(), "tmp")

### GENERAL UTILS

def wait_for_file(folder_path, pooling_interval):
    """
    Waits until a downloaded file shows up in the temporary folder

    :param folder_path: folder in which to search
    :return: the downloaded file name
    """
    downloaded_file = None

    time.sleep(10)

    while not downloaded_file:
        time.sleep(pooling_interval)
        for file in os.listdir(folder_path):
            # Don't consider Firefox temporary files
            if os.path.splitext(file)[1] != ".part":
                downloaded_file = file

    return downloaded_file


def download_page(driver, file_name):
    """
    Downloads the current page

    :param driver: a Firefox driver for Selenium inside the desired page
    :param file_name: name of the file to create
    """
    with open(file_name, 'wb') as html_file:
        html_file.write(driver.page_source.encode('iso-8859-1'))


def bin_search(driver, year, origin):
    """
    Checks how many entries we should "scan"

    :param driver: a Firefox driver for Selenium
    :param year: the year for which we're checking
    :param origin: the origin for which we're checking
    :return: last position which should be checked manually
    """
    begin = 0
    end = MAX_SEQ
    last_hit = -1
    while begin < end:
        mid = (begin + end) // 2
        # check at least MIN_MISS_SEQ entries before declaring a miss
        all_miss = True
        for i in range(mid, min(mid + MIN_MISS_SEQ, end + 1, MAX_SEQ + 1)):
            code = build_from_data(year, origin, i)
            if check_number(driver, code):
                all_miss = False
                last_hit = i
                # not worth checking all the rest to avoid using a break stmt
                break

        REVERSE = False
        if all_miss:
            if not REVERSE:
                end = mid - 1
            else:
                begin = i + 1
        else:
            if not REVERSE:
                begin = last_hit + 1
            else:
                end = mid - 1

    return last_hit + MIN_MISS_SEQ + 1


### DRIVER INITIALIZATION AND CONNECTION

def init_driver(tmp_folder, headless=True, timeout=30):
    """
    Initializes the Firefox Driver

    :param headless: temp folder used for downloads
    :param headless: if set to true, no window is rendered by Selenium
    :param timeout: number of seconds to wait for a page to load
    :return: the configured driver
    """

    if not os.path.exists(tmp_folder):
        os.makedirs(tmp_folder)

    # clear tmp directory
    for file in os.listdir(tmp_folder):
        os.remove(os.path.join(tmp_folder, file))

    fp = webdriver.FirefoxProfile()
    # Download files inside a folder called tmp in the current dir
    fp.set_preference("browser.download.folderList", 2)
    fp.set_preference("browser.download.dir", tmp_folder)
    fp.set_preference("browser.download.downloadDir", tmp_folder)
    fp.set_preference("browser.download.defaultFolder", tmp_folder)
    fp.set_preference("pdfjs.disabled", True)
    fp.set_preference("plugin.scan.Acrobat", "99.0");
    fp.set_preference("plugin.scan.plid.all", False);
    fp.set_preference("browser.download.manager.showWhenStarting", False)
    fp.set_preference("browser.download.manager.focusWhenStarting", False)
    fp.set_preference("browser.download.manager.closeWhenDone", True)
    fp.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/pdf");
    #fp.set_preference("dom.max_script_run_time", 1)

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
    :return: the driver in the desired url
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


### CODE PROCESSING

def verif_code(num_proc):
    """
    Calculates the verificaton code for a given process number

    :param num_proc: the process number for which to generate the code
    :return: the verif number for the supplied code
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
    :return: the corresponding process with its verifying digits
    """

    p_fmt = "{:07d}{:04d}{:03d}{:04d}"
    ver_code = verif_code(p_fmt.format(sequence, year, JTR_IDENTIFIER, origin))

    res_fmt = "{:07d}{:02d}{:04d}{:03d}{:04d}"
    return res_fmt.format(sequence, ver_code, year, JTR_IDENTIFIER, origin)


def generate_codes(first_year, last_year):
    """
    Generates all the codes to be downloaded

    :return: a generator instance which iterates over all possible codes
    """
    for year in range(first_year, last_year + 1):
        for origin in ORIGINS:
            for n in range(0, MAX_SEQ + 1):
                yield build_from_data(year, origin, n)



### INTERACTION WITH TRF2 WEBPAGE

def load_process_page(driver, num_proc):
    """
    Fills in the form and submits it to go to a desired process

    :param driver: a Firefox driver for Selenium
    :param num_proc: the process number to try
    :return: the driver in the desired location
    """
    driver = load_or_retry(driver, TRF2_URL)
    
    # process number input
    loaded = False
    while not loaded:
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.NAME, "NumProc")
                )
            )
            elem = driver.find_element_by_name("NumProc")
            loaded = True
        except:
            # there has been some internal server error, try again
            print("Server error, trying again")
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
    WebDriverWait(driver, 20).until(EC.staleness_of(elem))

    return driver


def process_page(driver, num_proc, tmp_folder, down_folder):
    """
    Processes a hit page to download all iframes

    :param driver: a Firefox driver for Selenium, in a process detail page
    :param num_proc: the process number for the open page
    :param tmp_folder: folder for temporary downloads
    :param down_folder: folder for collection storage
    """

    # Creates a folder for this process' files
    proc_folder = os.path.join(down_folder, str(num_proc))
    if not os.path.exists(proc_folder):
        os.mkdir(proc_folder)

    # list with attachment links
    att_links = []

    print("Selecting iframe links")
    # selects all iframe links
    iframe_sel = "/html/body/form/center/div/table[3]/tbody/tr[1]/td/table/tbody/tr/td[2]/p/font/span/a"
    els = driver.find_elements_by_xpath(iframe_sel)
    counter = 0
    for el in els:
        # open the iframe
        el.click()
        counter += 1

        # wait for it to load and then switch into it
        time.sleep(2)
        driver.switch_to.frame("dir")
        print("Tab number {}".format(counter))

        if counter == 1:
            # the first iframe has paging in it

            prev_btn = driver.find_elements_by_link_text("Anterior")
            # rewind to first page
            while len(prev_btn) > 0:
                button = prev_btn[0]
                button.click()
                WebDriverWait(driver, 10).until(EC.staleness_of(button))
                prev_btn = driver.find_elements_by_link_text("Anterior")

            # now we're at the first page
            file_name = str(counter) + "-1.html"
            file_name = os.path.join(proc_folder, file_name)
            download_page(driver, file_name)

            next_btn = driver.find_elements_by_link_text("Próxima")
            # follow to next pages
            page_counter = 1
            while len(next_btn) > 0:
                page_counter += 1
                button = next_btn[0]
                button.click()
                WebDriverWait(driver, 10).until(EC.staleness_of(button))
                file_name = str(counter) + "-" + str(page_counter) + ".html"
                file_name = os.path.join(proc_folder, file_name)
                download_page(driver, file_name)
                next_btn = driver.find_elements_by_link_text("Próxima")

        elif counter == 6:
            # the sixth frame has attachments, save its links if needed
            inner_frame = driver.find_elements_by_css_selector("iframe")
            driver.switch_to.frame(inner_frame[0])

            # Download page
            file_name = str(counter) + ".html"
            file_name = os.path.join(proc_folder, file_name)
            download_page(driver, file_name)

            if DOWNLOAD_ATTACHMENTS:
                attachments = driver.find_elements_by_css_selector("a.link-under")

                if len(attachments) > 0:
                    # create folder for attachments
                    att_folder = os.path.join(proc_folder, "attachments")
                    if not os.path.exists(att_folder):
                        os.mkdir(att_folder)

                    # save each attachment
                    for i in attachments:
                        i.click()
                        time.sleep(2) ################################# LEFT

                        window_before = driver.window_handles[0]
                        window_after = driver.window_handles[-1]
                        driver.switch_to.window(window_after)

                        downloaded_file = wait_for_file(tmp_folder, 2)
                        driver.close()

                        new_location = os.path.join(att_folder, downloaded_file)
                        previous_location = os.path.join(tmp_folder, downloaded_file)
                        shutil.move(previous_location, new_location)

                        # Wait for file to be removed
                        #wait = WebDriverWait(driver, 30)
                        #wait.until(lambda _: len(os.listdir(tmp_folder)) == 0)

                        driver.switch_to.window(window_before)

                    time.sleep(10) # wait for all files to be available
                    # check if all attachments were downloaded
                    #print("Assert for {} ".format(num_proc))
                    assert len(os.listdir(att_folder)) == len(attachments)

        else:
            # Just download the inner iframe's contents
            inner_frame = driver.find_elements_by_css_selector("iframe")
            if len(inner_frame) > 0:
                driver.switch_to.frame(inner_frame[0])
                file_name = str(counter) + ".html"
                file_name = os.path.join(proc_folder, file_name)
                download_page(driver, file_name)

        driver.switch_to.default_content()
        #time.sleep(2) ###################### REMOVED

    """if not DOWNLOAD_ATTACHMENTS:
        # save links in a text file
        file_name = os.path.join(proc_folder, "attachments.txt")
        with open(file_name, 'w') as txt_file:
            txt_file.write("\n".join(att_links))"""


def check_number(driver, num_proc):
    """
    Checks if a given number is a hit or a miss

    :param driver: a Firefox driver for Selenium
    :param num_proc: the process number to try
    :return: true if the checked number was hit, false if it missed
    """

    driver = load_process_page(driver, num_proc)

    if "cons_procs" in driver.current_url:
        return False
    else:
        return True


def access_process_url(driver, num_proc, tmp_folder, down_folder):
    """
    Checks if it hit a detail page, and if so, download the iframes

    :param driver: a Firefox driver for Selenium
    :param num_proc: the process number to try
    :param tmp_folder: folder for temporary downloads
    :param down_folder: folder for collection storage
    :return: true if the checked number was hit, false if it missed
    """

    print("Loading process page")
    driver = load_process_page(driver, num_proc)

    if "cons_procs" in driver.current_url:
        return False
    else:
        print("Entry found, processing page")
        #print("*** Found process for {}".format(num_proc))
        process_page(driver, num_proc, tmp_folder, down_folder)
        return True


def run_year(year):
    print("Begin year {}".format(year))
    tmp_folder = os.path.join(TMP_DOWNLOAD, str(year))
    down_folder = os.path.join(DOWNLOAD_FOLDER, str(year))

    if not os.path.exists(down_folder):
        os.makedirs(down_folder)

    driver = init_driver(tmp_folder, True)

    hit = 0
    for origin in ORIGINS:
        #print("* Year {}:".format(year))
        upper_lim = bin_search(driver, year, origin)
        #print("** Verify from 0 to {}".format(upper_lim))
        for i in range(0, upper_lim):
            code = build_from_data(year, origin, i)
            processed = False
            while not processed:
                try:
                    print("{} --- Begin processing {}".format(year, code))
                    if access_process_url(driver, code, tmp_folder, down_folder):
                        hit += 1
                        print("{} --- Done processing {}".format(year, code))
                    processed = True
                except:
                    print("Error at {}, retrying...".format(year, code))
                    pass
            sys.stdout.flush()

    print("Year {} had {} hits".format(year, hit))
    sys.stdout.flush()

    time.sleep(5)

    driver.close()

def main():
    if not os.path.exists(DOWNLOAD_FOLDER):
        os.makedirs(DOWNLOAD_FOLDER)
    #run_year(2019)
    #Parallel(n_jobs=-1)(delayed(run_year)(year) for year in reversed(range(FIRST_YEAR, LAST_YEAR + 1) ))
    for year in reversed(range(FIRST_YEAR, LAST_YEAR + 1)):
        run_year(year)

if __name__ == "__main__":
    main()
