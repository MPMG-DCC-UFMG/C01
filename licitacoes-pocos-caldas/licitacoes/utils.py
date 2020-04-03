import logging
import time
import os

from licitacoes import config
from random import randint
from selenium.common import exceptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By


def progress_information(current_id, start_time):
    if not current_id % 50:
        wait_time = randint(1, 30)
        e = int(time.time() - start_time)
        elapsed_time = f'{e // 3600:02d}:{(e % 3600 // 60):02d}:{e % 60:02d}'
        percentage = (current_id // config.MAX_PROCESSES) * 100
        logging.info("Elapsed time " + elapsed_time + " sec, " + str(percentage) + "% of all IDs covered")
        logging.info("Waiting " + str(wait_time) + " sec")
        time.sleep(wait_time)


def check_max_skipped_ids(skipped_ids):
    if skipped_ids > config.MAX_SKIPPED_IDS:
        logging.info(str(skipped_ids) + " consecutive void IDs. Nothing else to download")
        return True
    else:
        return False


def get_output_dir(process_id):
    process_number, process_year = parse_process_id(process_id)
    return config.DOWNLOAD_DIR + config.BASE_FOLDER + "/" + process_year + "/" + str(process_number)


def check_max_retries(retries):
    retries += 1
    retry_time = config.WAIT_INTERVAL * retries
    logging.info("TimeoutError, retrying in" + str(retry_time) + " sec")
    time.sleep(retry_time)
    if retries > config.MAX_RETRIES:
        logging.info("Max retries reached, terminating crawler")
        return True


def load_page(driver, url=config.START_URL):
    try:
        driver.get(url)
    except exceptions.WebDriverException:
        logging.error('Could not reach ' + url)

    logging.info("Waiting for page to load")
    wait_page_load(driver)

    return driver


def wait_page_load(driver, element_xpath=config.MAX_RESULTS_FIELD, delay=config.WEBDRIVER_DELAY):
    try:
        WebDriverWait(driver, delay).until(ec.presence_of_element_located((By.XPATH, element_xpath)))
    except exceptions.TimeoutException:
        logging.error("TimeoutException: Page not loaded correctly")


def get_process_id(process):
    process_id = str(process.get_attribute('innerHTML'))
    return process_id


def parse_process_id(process_id):
    process_number, process_year = process_id.split('/')
    return process_number, process_year


def save_html(html_text, process_id, filename):
    output_dir = get_output_dir(process_id)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        logging.info("Creating directory: " + str(output_dir))
    with open(output_dir + "/" + filename + ".html", "w+") as f:
        f.write(html_text)
