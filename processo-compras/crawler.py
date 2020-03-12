# -*- coding: utf-8 -*-
import time
import logging

from compras import config
from compras.config import MAX_PROCESSES, START_PROCESS
from compras import download


download_dir = config.DOWNLOAD_DIR
config.set_logging()
driver = config.get_driver()

base = config.BASE
process_not_found = config.PROCESS_NOT_FOUND

i = START_PROCESS
start_time = time.time()
retries = 0
skipped_ids = 0

driver = config.get_driver()

while i < MAX_PROCESSES:
    try:
        # time information
        download.progress_information(i, start_time)

        content, text = download.get_html(i)

        # process not found
        if download.check_process_exists(i):
            skipped_ids = 0
        else:
            skipped_ids += 1
            i = i + 1
            if download.check_max_skipped_ids(skipped_ids):
                break
            else:
                continue

        logging.info("Downloading processo de compra ID: " + str(i))

        # fetching html
        download.download_html(i)

        # fetching relatorio_de_detalhes
        download.get_relatorio_detalhes(i)

        # driver.get(url)
        loaded_driver = download.get_page(driver, i)

        # expanding files section
        if download.expand_file_section(loaded_driver):
            pass
        else:
            i = i + 1
            continue

        # download edital files
        download.download_edital(loaded_driver, i)

        # download extrato de publicacao files
        download.download_extrato(loaded_driver, i)

        download.check_max_threads()

        # download arquivo grande circulacao files
        download.download_publicacao(loaded_driver, i)

        i = i + 1
        retries = 0

    # Check for timeout and retry download
    except TimeoutError:
        if download.check_max_retries(retries):
            break
