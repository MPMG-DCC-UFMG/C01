# -*- coding: utf-8 -*-
"""
Rúbia Reis Guerra
rubia-rg@github
Crawler for 'Licitações' at https://prefeitura.pbh.gov.br/licitacoes
"""
import logging
import time
import wget
import requests
import os
import random
import mimetypes

from licitacoes import config
from bs4 import BeautifulSoup
from random import randint


def progress_information(current_page, start_time):
    if not current_page % 100:
        wait_time = randint(1, 30)
        e = int(time.time() - start_time)
        elapsed_time = f'{e // 3600:02d}:{(e % 3600 // 60):02d}:{e % 60:02d}'
        percentage = (current_page / config.MAX_PAGES) * 100
        logging.info("Elapsed time " + elapsed_time + " sec, " + str(percentage) + "% of all pages covered")
        logging.info("Waiting " + str(wait_time) + " sec")
        time.sleep(wait_time)


def get_url(link):
    return config.BASE + str(link)


def get_search_url(current_page):
    return config.SEARCH_PAGE + str(current_page)


def get_html_contents(link):
    """
    Returns HTML content in binary code
    - Preserves text encoding
    :param link: current process
    :return: url contents
    """
    user_agent = random.choice(config.USER_AGENT_LIST)
    headers = {'User-Agent': user_agent}
    url = get_url(link)
    response = requests.get(url, headers=headers)
    return response.content


def get_html_text(link=None, url=None):
    if url is None:
        url = get_url(link)
    user_agent = random.choice(config.USER_AGENT_LIST)
    headers = {'User-Agent': user_agent}
    response = requests.get(url, headers=headers)
    return response.text


def check_page_exists(current_page):
    url = get_search_url(current_page)
    text = get_html_text(url=url)
    return config.INVALID_PAGE_MESSAGE in str(text) or "Acesso negado" in str(text)


def check_access_forbidden(current_page):
    url = get_search_url(current_page)
    text = get_html_text(url=url)
    return config.NO_PERMISSION_MESSAGE in str(text)


def check_max_skipped_pages(skipped_ids):
    if skipped_ids > config.MAX_SKIPPED_PAGES:
        logging.info(str(skipped_ids) + " consecutive void pages. Nothing else to download")
        return True
    else:
        return False


def check_max_retries(retries):
    retries += 1
    retry_time = config.WAIT_INTERVAL * retries
    logging.info("TimeoutError, retrying in " + str(retry_time) + " sec")
    time.sleep(retry_time)
    if retries > config.MAX_RETRIES:
        logging.info("Max retries reached, terminating crawler")
        return True


def get_output_dir(link):
    return config.DOWNLOAD_DIR + config.BASE_FOLDER + link + '/'


def crawl_search_page(current_page):
    search_url = get_search_url(current_page)
    html_text = get_html_text(url=search_url)
    links = get_links(html_text, config.CSS_SELECTOR_LINKS)
    for link in set(links):
        logging.info("Crawling " + str(link))
        download_html(link)
        get_files_links(link)


def download_html(link):
    content = get_html_contents(link)
    output_dir = get_output_dir(link)
    _, filename = parse_link(link)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        logging.info("Creating directory: " + str(output_dir))
    with open(output_dir + filename + ".html", "wb") as f:
        f.write(content)


def download_process_files(base_link, url):
    output_dir = get_output_dir(base_link)
    try:
        wget.download(url, out=output_dir)
        time.sleep(1.5)
    except:
        logging.info('File not available at ' + str(url))


def save_process_links(base_link, url):
    output_dir = get_output_dir(base_link)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        logging.info("Creating directory: " + str(output_dir))
    with open(output_dir + "links.txt", "a") as f:
        f.write(str(url))


def get_files_links(base_link):
    html_text = get_html_text(base_link)
    links = get_links(html_text, config.CSS_SELECTOR_FILES)
    for link in set(links):
        if is_file(link):
            logging.info("Downloading file from " + str(link))
            download_process_files(base_link, link)
        else:
            logging.info("Appending " + str(link) + " to links.txt")
            save_process_links(base_link, link)


def is_file(url):
    return mimetypes.guess_type(url)[0]


def get_links(html_text, css_element=config.CSS_SELECTOR_LINKS):
    soup = BeautifulSoup(html_text, features='lxml')
    links = []
    for link in soup.select(css_element):
        links.append(link['href'])
    return links


def parse_link(link):
    return link.rsplit('/', 1)

