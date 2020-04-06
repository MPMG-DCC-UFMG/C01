# -*- coding: utf-8 -*-
"""
Rúbia Reis Guerra
rubia-rg@github
Crawler for 'Processos de Compra' at https://www1.compras.mg.gov.br/processocompra/processo/consultaProcessoCompra.html
"""
import logging

BASE_FOLDER = "/br.gov.mg.compras/processocompra/"
PROFILE_PATH = "/Users/work/Library/Application Support/Firefox/Profiles/yde1eaqi.mpmg"
DOWNLOAD_DIR = "/Volumes/Work HD/MPMG"
NO_PERMISSION_MESSAGE = "You don't have permission to access"
PROCESS_NOT_FOUND_MESSAGE = 'O(A) "Processo Compra" não pode ser alterado(a), pois foi excluído(a) por outro usuário, ' \
                    'em acesso concorrente, enquanto esta tela era visualizada.'
RELATORIO_DETALHES = 'https://www1.compras.mg.gov.br/processocompra/processo/relatoriodetalhes/' \
                     'relatorioDetalhesProcessoCompra.html?id='
MAX_RETRIES = 10
WAIT_INTERVAL = 30
START_PROCESS = 3030
MAX_PROCESSES = 1000000
MAX_SKIPPED_IDS = 5000
BASE = "https://www1.compras.mg.gov.br/processocompra/processo/visualizacaoArquivosProcesso.html?id="
FORM_DATA = {"idArquivo": '', "nomeArquivo": '', "chaveAberturaArquivo": ''}
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

STRING_PATTERN = '\(([^)]+)\)'
JS_METHOD = 'visualizarArquivo'


def set_logging():
    logging.basicConfig(level=logging.INFO)
