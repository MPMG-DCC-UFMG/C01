import logging
import time
import wget
import requests
import os
import re
import random

from compras import config
from bs4 import BeautifulSoup
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
    user_agent = random.choice(config.USER_AGENT_LIST)
    headers = {'User-Agent': user_agent}
    url = get_base_url(current_id)
    response = requests.get(url, headers=headers)
    return response.content


def get_html_text(current_id):
    url = get_base_url(current_id)
    user_agent = random.choice(config.USER_AGENT_LIST)
    headers = {'User-Agent': user_agent}
    response = requests.get(url, headers=headers)
    return response.text


def check_process_exists(current_id):
    text = get_html_text(current_id)
    return config.PROCESS_NOT_FOUND_MESSAGE in str(text) or "Acesso negado" in str(text)


def check_access_forbidden(current_id):
    text = get_html_text(current_id)
    return config.NO_PERMISSION_MESSAGE in str(text)


def check_max_skipped_ids(skipped_ids):
    if skipped_ids > config.MAX_SKIPPED_IDS:
        logging.info(skipped_ids + " consecutive void IDs. Nothing else to download")
        return True
    else:
        return False


def get_output_dir(current_id):
    current_id_range = current_id // 100
    return config.DOWNLOAD_DIR + config.BASE_FOLDER + str(current_id_range) + "/" + str(current_id)


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
        time.sleep(.5)
    except:
        logging.info('Relatorio de Detalhes not available for ID ' + str(current_id))


def check_max_retries(retries):
    retries += 1
    retry_time = config.WAIT_INTERVAL * retries
    logging.info("TimeoutError, retrying in" + str(retry_time) + " sec")
    time.sleep(retry_time)
    if retries > config.MAX_RETRIES:
        logging.info("Max retries reached, terminating crawler")
        return True


def download_process_files(current_id):
    html_text = get_html_text(current_id)
    params_list = parse_html(html_text)
    for params in params_list:
        form_data = fill_form_data(params)
        get_files(current_id, form_data)


def fill_form_data(params):
    form_data = config.FORM_DATA
    form_data['idArquivo'] = params[0]
    form_data['nomeArquivo'] = params[1]
    form_data['chaveAberturaArquivo'] = params[2]
    return form_data


def get_files(current_id, form_data):
    output_dir = get_output_dir(current_id)
    try:
        url = get_base_url(current_id) + '&versao=51&metodo=abrirArquivo&exibirMensagem=false&idArquivo=' \
              + form_data['idArquivo'] + '&nomeArquivo=' + form_data['nomeArquivo'] + \
              '&chaveAberturaArquivo=' + form_data['chaveAberturaArquivo']
        wget.download(url, out=output_dir)
        time.sleep(1.5)
    except:
        logging.info(form_data['nomeArquivo'] + ' not available for ID ' + str(current_id))


def parse_html(html_text):
    soup = BeautifulSoup(html_text, features='lxml')
    search_string = get_search_string()
    results = re.findall(search_string, str(soup))
    params_list = []
    for params in results:
        if 'idArquivo' in params:
            continue
        params = treat_params_string(params)
        params_list.append(params)
    return params_list


def treat_params_string(params):
    return params.replace("'", "").replace(" ", "").split(",")


def get_search_string(js_method=config.JS_METHOD, string_pattern=config.STRING_PATTERN):
    return js_method + string_pattern
