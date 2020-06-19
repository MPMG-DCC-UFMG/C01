from util import *
import os
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import speech_recognition as sr

browser = webdriver.Chrome(executable_path=r'chromedriver.exe')

browse.get('https://www4.tjmg.jus.br/juridico/sf/proc_resultado.jsp?comrCodigo=24&numero=1&listaProcessos=13108047')

botao_baixar_audio = browser.find_element_by_link_text("Baixar o áudio")
botao_baixar_audio.click()

