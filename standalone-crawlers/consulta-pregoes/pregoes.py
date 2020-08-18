import requests
import logging
import os
import re
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException    

def getPDF(driver, command, name):
    try:
        driver.execute_script(command)
        if os.path.isfile("/home/rennan/Downloads/" + name):
            os.rename("/home/rennan/Downloads/" + name,
                  destination_dir + "/" + name)
    except:
        pass

def download(driver, i, retries=0):
    if retries > 10:
        logging.info("Nao foi possivel coletar pregao de id:" + str(i))
        return
    try:
        logging.info("Tentativa de número: " + str(retries))
        url = base + str(i)
        response = requests.get(url)
        content = response.text
        if not_found in content or "Continue acessando: PRODEMGE" in content:
            return
        logging.info("Coletando pregao de ID: " + str(i))
        folder = "pregao" + str(i%100)
        destination_dir = "pregoes/" + folder + "/" + str(i)
        if not os.path.exists(destination_dir):
            os.makedirs(destination_dir)
        with open(destination_dir + "/pregao_id" + str(i) + ".html", "w") as f:
            f.write(content)

        content = requests.get(url_ata + str(i)).text
        if not(chat_not_found in content or "Continue acessando: PRODEMGE" in content):
            driver.get(url_ata + str(i))
            logging.info("Coletando atas pregao de ID: " + str(i))
            atas = re.findall(r"habilitarComandoVisualizarAta\('(.*?)'\)", content)
            for ata in atas:
                print(ata)
                time.sleep(.5)
                url_down = "https://www1.compras.mg.gov.br/processocompra/pregao/consulta/dados/atas/atasGeraisPregao.html?id=" + ata +"&idPregao=801&metodo=visualizarAta"
                driver.get(url_down)
                if os.path.isfile("/home/rennan/Downloads/ataPregao.pdf"):
                    os.rename("/home/rennan/Downloads/ataPregao.pdf", destination_dir + "/ataPregao.pdf" + ata)

        content = requests.get(url_ata_especifica + str(i) + "&metodo=visualizar").text
        if not(chat_not_found in content or "Continue acessando: PRODEMGE" in content):
            driver.get(url_ata + str(i))
            logging.info("Coletando atas pregao de ID: " + str(i))
            atas = re.findall(r"habilitarComandoVisualizarAta\('(.*?)'\)", content)
            for ata in atas:
                print(ata)
                time.sleep(.5)
                url_down = "https://www1.compras.mg.gov.br/processocompra/pregao/consulta/dados/atas/atasEspecificasLote.html?id=" + ata +"&idPregao=15000&metodo=visualizarAta"
                driver.get(url_down)
                if os.path.isfile("/home/rennan/Downloads/ataPregao.pdf"):
                    os.rename("/home/rennan/Downloads/ataPregao.pdf", destination_dir + "/ataPregaoEspecifica.pdf" + ata)

        driver.get(url)
        getPDF(driver, "exibirRelatorioQuadroAvisos();", "relatorioConsultaQuadroAvisos.pdf")
        getPDF(driver, "exibirRelatorioTermoConclusao();", "termoConclusao.pdf")

        driver.get(url_chat + str(i))
        time.sleep(1)
        content = driver.page_source
        if not(chat_not_found in content or "Continue acessando: PRODEMGE" in content):
            logging.info("Coletando chat pregao de ID: " + str(i))
            folder = "pregao" + str(i%100)
            with open(destination_dir + "/pregao_id_chat" + str(i) + ".html", "w") as f:
                f.write(content)
    except:
        retries+=1
        download(driver, i, retries)

options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_experimental_option("prefs", {
        "download.default_directory": "/home/rennan/Downloads/",
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing_for_trusted_sources_enabled": False,
        "safebrowsing.enabled": False
})
options.add_argument('window-size=1920x1080')
driver = webdriver.Chrome("/usr/bin/chromedriver", chrome_options=options)

logging.basicConfig(level=logging.INFO)

base = "https://www1.compras.mg.gov.br/processocompra/pregao/consulta/dados/abaDadosPregao.html?interfaceModal=true&metodo=visualizar&idPregao="
url_ata = "https://www1.compras.mg.gov.br/processocompra/pregao/consulta/dados/atas/atasGeraisPregao.html?interfaceModal=true&idPregao="
url_ata_especifica = "https://www1.compras.mg.gov.br/processocompra/pregao/consulta/dados/atas/atasEspecificasLote.html?aba=abaAtasEspecificasLote&idPregao="
url_chat = "https://www1.compras.mg.gov.br/processocompra/pregao/consulta/dados/pregao/visualizacaoChatPregao.html?interfaceModal=true&idPregao="
not_found = "entidadeNaoEncontrada"
chat_not_found = 'O(A) "Pregão" não pode ser alterado(a), pois foi excluído(a) por outro usuário, em acesso concorrente, enquanto esta tela era visualizada.'

for i in range(120000,200000):
    download(driver, i)