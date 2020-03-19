# -*- coding: utf-8 -*-
import time
import logging

from requests.exceptions import ConnectionError
from http.client import RemoteDisconnected
from compras import config
from compras import download


download_dir = config.DOWNLOAD_DIR
config.set_logging()

current_id = config.START_PROCESS
start_time = time.time()
retries = 0
skipped_ids = 0

while current_id < config.MAX_PROCESSES:
    try:
        # time information
        download.progress_information(current_id, start_time)

        # process not found
        if download.check_access_forbidden(current_id):
            logging.info("Processo de compra ID " + str(current_id) + ": 403 Forbidden")
            skipped_ids += 1
            current_id = current_id + 1
            if download.check_max_skipped_ids(skipped_ids):
                break
            else:
                continue
        elif download.check_process_exists(current_id):
            logging.info("Processo de compra ID " + str(current_id) + ": nothing to download")
            skipped_ids += 1
            current_id = current_id + 1
            if download.check_max_skipped_ids(skipped_ids):
                break
            else:
                continue
        else:
            skipped_ids = 0
            logging.info("Downloading processo de compra ID: " + str(current_id))

        # fetching html
        download.download_html(current_id)

        # fetching relatorio_de_detalhes
        download.get_relatorio_detalhes(current_id)

        # download edital files

        download.download_process_files(current_id)

        current_id = current_id + 1
        retries = 0

    # Check for timeout and retry download
    except (TimeoutError, ConnectionError, RemoteDisconnected):
        if download.check_max_retries(retries):
            break
