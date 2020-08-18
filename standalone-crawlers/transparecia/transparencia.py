from selenium import webdriver
from selenium.webdriver.support.ui import Select
import time
import argparse
import selenium
import os
import urllib.request

# Abre o chromedriver com a url dada e retorna o driver
def carrega_pagina(url, path = '/mnt/ssd0/luiznery/Documentos/mpmg/remuneracao'):
    path += "/chromedriver"
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    driver = webdriver.Chrome(path, options=options)
    driver.get(url)
    print("Pagina carregada")
    return driver

#Define argumentos - URL dos dados a serem coletados
parser = argparse.ArgumentParser(description='Baixa arquivos do portal transparencia.')
parser.add_argument("url", help="Url da qual se deseja baixar os arquivos.")
# parser.add_argument("path", help="Url da qual se deseja baixar os arquivos.")

args = vars(parser.parse_args())
url = args["url"]
# path = args["path"]
path = url.split("/")[-1:][0]

driver = carrega_pagina(url)

#cria diretorio
if not os.path.exists(path):
    os.makedirs(path)

print("Baixando arquivos:")
skillsSection = driver.find_element_by_xpath("""//*[@id="dataset-resources"]/ul""")
for child in skillsSection.find_elements_by_xpath(".//li/div/ul/li[2]/a"):
    link = child.get_attribute("href")
    print(link.split("/")[-1:][0])
    urllib.request.urlretrieve(link, path + "/" + link.split("/")[-1:][0])

driver.close()
