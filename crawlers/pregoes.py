import requests
import logging
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException    

options = webdriver.ChromeOptions()
# options.add_argument("--headless")
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
not_found = "entidadeNaoEncontrada"
for i in range(800,50000):
    url = base + str(i)
    response = requests.get(url)
    content = response.text
    if not_found in content or "Continue acessando: PRODEMGE" in content:
        continue
    logging.info("Coletando pregao de ID: " + str(i))
    folder = "pregao" + str(i%100)
    destination_dir = "pregoes/" + folder + "/" + str(i)
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)
    with open(destination_dir + "/pregao_id" + str(i), "w") as f:
        f.write(content)
    driver.get(url)
    command = "exibirRelatorioQuadroAvisos();"
    driver.execute_script(command)
    if os.path.isfile("/home/rennan/Downloads/relatorioConsultaQuadroAvisos.pdf"):
        os.rename("/home/rennan/Downloads/relatorioConsultaQuadroAvisos.pdf",
              destination_dir + "/relatorioConsultaQuadroAvisos.pdf")
