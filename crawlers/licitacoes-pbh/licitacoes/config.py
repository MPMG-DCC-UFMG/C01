# -*- coding: utf-8 -*-
"""
Rúbia Reis Guerra
rubia-rg@github
Crawler for 'Licitações' at https://prefeitura.pbh.gov.br/licitacoes
"""
import logging

BASE_FOLDER = "/br.gov.pbh.prefeitura/licitacoes"
DOWNLOAD_DIR = "/Volumes/Work HD/MPMG"
NO_PERMISSION_MESSAGE = "You don't have permission to access"
INVALID_PAGE_MESSAGE = 'Uma escolha inválida foi detectada. Por favor entre em contato com o administrador do site.'
MAX_RETRIES = 10
WAIT_INTERVAL = 30
START_PAGE = 1
MAX_PAGES = 100
MAX_SKIPPED_PAGES = 5
BASE = "https://prefeitura.pbh.gov.br"
SEARCH_PAGE = "https://prefeitura.pbh.gov.br/licitacoes?field_situacao_value=1&page="
CSS_SELECTOR_FILES = '.field.field--name-field-icone.field--type-image.field--label-hidden.field__item a[href]'
CSS_SELECTOR_LINKS = '.item_ar_licitacao a[href]'
USER_AGENT_LIST = [
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/602.2.14 (KHTML, like Gecko) Version/10.0.1 Safari/602.2.14',
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0'
]


def set_logging():
    logging.basicConfig(level=logging.INFO)
