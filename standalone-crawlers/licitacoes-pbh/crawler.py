# -*- coding: utf-8 -*-
"""
Rúbia Reis Guerra
rubia-rg@github
Crawler for 'Licitações' at https://prefeitura.pbh.gov.br/licitacoes
"""
import time
import logging

from requests.exceptions import ConnectionError
from http.client import RemoteDisconnected
from licitacoes import config
from licitacoes import download


download_dir = config.DOWNLOAD_DIR
config.set_logging()

current_page = config.START_PAGE
start_time = time.time()
retries = 0
skipped_pages = 0

while current_page < config.MAX_PAGES:
    try:
        # time information
        download.progress_information(current_page, start_time)

        # process not found
        if download.check_access_forbidden(current_page):
            logging.info("Page " + str(current_page) + ": 403 Forbidden")
            skipped_pages += 1
            current_page += 1
            if download.check_max_skipped_pages(skipped_pages):
                break
            else:
                continue
        elif download.check_page_exists(current_page):
            logging.info("Page " + str(current_page) + ": nothing to download")
            skipped_pages += 1
            current_page += 1
            if download.check_max_skipped_pages(skipped_pages):
                break
            else:
                continue
        else:
            skipped_pages = 0
            logging.info("Crawling files on page " + str(current_page))

        # fetching html
        download.crawl_search_page(current_page)

        current_page = current_page + 1
        retries = 0

    # Check for timeout and retry download
    except (TimeoutError, ConnectionError, RemoteDisconnected):
        if download.check_max_retries(retries):
            break
