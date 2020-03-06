import logging

from selenium import webdriver
from selenium.webdriver.firefox.options import Options


BASE_FOLDER = "/br.gov.mg.compras/processocompra/"
PROFILE_PATH = "/Users/work/Library/Application Support/Firefox/Profiles/yde1eaqi.mpmg"
DOWNLOAD_DIR = "/Volumes/Work HD/MPMG"
PROCESS_NOT_FOUND = 'O(A) "Processo Compra" não pode ser alterado(a), pois foi excluído(a) por outro usuário, ' \
                    'em acesso concorrente, enquanto esta tela era visualizada.'

RELATORIO_DETALHES = 'https://www1.compras.mg.gov.br/processocompra/processo/relatoriodetalhes/' \
      'relatorioDetalhesProcessoCompra.html?id='
MAX_RETRIES = 10
WAIT_INTERVAL = 30
START_PROCESS = 3030
MAX_PROCESSES = 1000000
MAX_SKIPPED_IDS = 5000
BASE = "https://www1.compras.mg.gov.br/processocompra/processo/visualizacaoArquivosProcesso.html?id="
FILE_EXTENSIONS = [".pdf", ".doc", ".docx", ".zip", ".odt", ".eml"]
MAX_THREADS = 4


def set_options():
    firefox_options = Options()
    firefox_options.add_argument("--headless")
    firefox_options.add_argument("--window-size=1920x1080")
    firefox_options.add_argument("--disable-notifications")
    firefox_options.add_argument('--no-sandbox')
    firefox_options.add_argument('--verbose')
    firefox_options.add_argument('--disable-gpu')
    firefox_options.add_argument('--disable-software-rasterizer')
    firefox_options.set_preference("browser.download.manager.showWhenStarting", False)
    firefox_options.set_preference('browser.helperApps.neverAsk.openFile', "application/pdf")
    firefox_options.set_preference('browser.helperApps.neverAsk.saveToDisk', "application/pdf")
    firefox_options.set_preference('browser.helperApps.neverAsk.openFile', "application/zip")
    firefox_options.set_preference('browser.helperApps.neverAsk.saveToDisk', "application/zip")
    firefox_options.set_preference('browser.helperApps.neverAsk.openFile', "application/msword")
    firefox_options.set_preference('browser.helperApps.neverAsk.saveToDisk', "application/msword")
    firefox_options.set_preference("pdfjs.disabled", "true")
    return firefox_options


def get_driver(profile_path=PROFILE_PATH):
    firefox_options = set_options()
    driver = webdriver.Firefox(firefox_profile=profile_path,
                               options=firefox_options)
    return driver


def set_logging():
    logging.basicConfig(level=logging.INFO)
