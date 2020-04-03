# -*- coding: utf-8 -*-
"""
Rúbia Reis Guerra
rubia-rg@github
Crawler for 'Licitações' at https://pocosdecaldas.mg.gov.br/
"""
import logging
import time
from licitacoes import config, form, utils, process
from selenium.common import exceptions

config.set_logging()
driver = config.get_driver()
time.sleep(5)

browser = utils.load_page(driver)

logging.info('Filling search form')

SearchForm = form.SearchForm()
search_results = SearchForm.fill_form(browser)

process_count = config.START_PROCESS
start_time = time.time()
skipped_ids = 0

while process_count < config.MAX_PROCESSES:
    try:
        Process = process.BiddingProcess(process_count, search_results)
        logging.info('Download search result ' + str(process_count))
    except exceptions.NoSuchElementException:
        logging.error('Process does not exist')
        process_count += 1
        skipped_ids += 1
        utils.check_max_skipped_ids(skipped_ids)
        continue

    utils.progress_information(process_count, start_time)
    Process.extract_process_data()
    process_count += 1

driver.close()
