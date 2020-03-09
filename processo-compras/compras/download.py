import threading
import logging
import time
import wget
import requests
import os

from compras import config
from selenium.common import exceptions


from random import randint


def progress_information(current_id, start_time):
    if not current_id % 100:
        wait_time = randint(1, 30)
        e = int(time.time() - start_time)
        elapsed_time = f'{e // 3600:02d}:{(e % 3600 // 60):02d}:{e % 60:02d}'
        percentage = (current_id // config.MAX_PROCESSES) * 100
        logging.info("Elapsed time " + elapsed_time + " sec, " + str(percentage) + "% of all IDs covered")
        logging.info("Waiting " + str(wait_time) + " sec")
        time.sleep(wait_time)


def get_base_url(current_id):
    return config.BASE + str(current_id)


def get_html_contents(current_id):
    """
    Returns HTML content in binary code
    - Preserves text encoding
    :param current_id: current process
    :return: url contents
    """
    url = get_base_url(current_id)
    response = requests.get(url)
    return response.content


def get_html_text(current_id):
    url = get_base_url(current_id)
    response = requests.get(url)
    return response.text


def get_html(current_id):
    return get_html_contents(current_id), get_html_text(current_id)


def check_process_exists(current_id):
    text = get_html_text(current_id)
    if config.PROCESS_NOT_FOUND in text or "Acesso negado" in text:
        logging.info("Processo de compra ID " + str(current_id) + ": nothing to download")
        return False
    else:
        return True


def check_max_skipped_ids(skipped_ids):
    if skipped_ids > config.MAX_SKIPPED_IDS:
        logging.info(skipped_ids + " consecutive void IDs. Nothing else to download")
        return True
    else:
        return False


def get_output_dir(current_id):
    current_id_range = current_id // 100
    return config.DOWNLOAD_DIR + config.BASE_FOLDER + str(current_id_range) + "/" + str(current_id)


def get_page(driver, current_id):
    url = get_base_url(current_id)
    driver.get(url)
    return driver


def download_html(current_id):
    content = get_html_contents(current_id)
    output_dir = get_output_dir(current_id)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        logging.info("Creating directory: " + str(output_dir))
    with open(output_dir + "/" + str(current_id) + ".html", "wb") as f:
        f.write(content)


def get_relatorio_detalhes(current_id):
    output_dir = get_output_dir(current_id)
    try:
        relatorio_detalhes_url = config.RELATORIO_DETALHES + str(current_id)
        wget.download(relatorio_detalhes_url, out=output_dir)
        time.sleep(1.5)
    except:
        logging.info('Relatorio de Detalhes not available for ID ' + str(current_id))


def expand_file_section(driver):
    try:
        search_input = driver.find_element_by_id('painelArquivosEdital')
        search_input.click()
        return True
    except exceptions.NoSuchElementException:
        return False


def download_edital(driver, current_id):
    download_files_threads(driver, 'visualizar_idArquivoDocumentoEdital', 'Edital', current_id)


def download_publicacao(driver, current_id):
    download_files_threads(driver, 'visualizar_idArquivoPublicJornalGraCirc', 'PublicJornalGrandeCirculacao',
                           current_id)


def download_extrato(driver, current_id):
    download_files_threads(driver, 'visualizar_idArquivoExtratoPublicEdital', 'ExtratoPublicacaoEdital', current_id)


def download_files_threads(driver, method, filename, current_id):
    try:
        download_thread = threading.Thread(target=download_files, args=(driver, method))
        download_thread.start()
        move_files_thread = threading.Thread(target=move_files, args=(filename, current_id, download_thread))
        move_files_thread.start()
        logging.info('Downloaded ' + filename + ' for ' + str(current_id))
    except exceptions.NoSuchElementException:
        logging.info(filename + ' not available for ID ' + str(current_id))


def download_files(driver, element_id):
    search_input = driver.find_element_by_id(element_id)
    search_input.click()
    time.sleep(1.5)


def move_files(filename, current_id, download_thread):
    download_thread.join()
    output_dir = get_output_dir(current_id)
    for file_extension in config.FILE_EXTENSIONS:
        downloaded_file = config.DOWNLOAD_DIR + "/" + filename + file_extension
        if os.path.isfile(downloaded_file):
            os.rename(downloaded_file, output_dir + "/" + filename + file_extension)


def check_max_retries(retries):
    retries += 1
    retry_time = config.WAIT_INTERVAL * retries
    logging.info("TimeoutError, retrying in" + str(retry_time) + " sec")
    time.sleep(retry_time)
    if retries > config.MAX_RETRIES:
        logging.info("Max retries reached, terminating crawler")
        return True


def check_max_threads():
    if threading.active_count() > config.MAX_THREADS:
        time.sleep(2)
