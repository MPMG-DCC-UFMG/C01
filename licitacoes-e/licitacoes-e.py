from selenium import webdriver
from selenium.webdriver.support.ui import Select
import datetime
import time
import os

from PIL import Image
import cv2
import pytesseract

import speech_recognition as sr
from os import remove
from os import path
from pydub import AudioSegment


# Quebra captcha de audio
def transcribe(audio, limit = 5):
    sound = AudioSegment.from_mp3(audio)
    AUDIO_FILE = "audio.wav"
    sound.export(AUDIO_FILE, format="wav")
    r = sr.Recognizer()
    resposta = ""
    attempts = 0
    with sr.AudioFile(AUDIO_FILE) as source:
        while attempts < limit:
            try:
                audio = r.record(source)  # read the entire audio file                  
                resposta = r.recognize_google(audio)
                attempts = limit + 1
            except:
                attempts += 1
        remove(AUDIO_FILE)
    return resposta, attempts

#Qubra captcha de imagem
def solve_captcha(img_path):
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    img[img>110] = 240
    img[img<30] = 240
    img = img[:,20:150]
    return pytesseract.image_to_string(img)


url = "https://www.licitacoes-e.com.br/aop/pesquisar-licitacao.aop?opcao=preencherPesquisar"

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

driver = webdriver.Chrome(options=options)
driver.get(url)
print("Pagina carregada")

# Prenche formulario
# option = input("Situação da licitação: ")
option = "Publicada"
situacao = driver.find_element_by_xpath("""//*[@id="licitacaoPesquisaSituacaoForm"]/div[5]/span/input""")
situacao.clear()
situacao.send_keys(option)

#Pede para usuario preencher o captcha
while True:
    resposta = input("Captcha: ")
    driver.find_element_by_xpath("""//*[@id="pQuestionAvancada"]""").send_keys(resposta)
    driver.find_element_by_xpath("""//*[@id="licitacaoPesquisaSituacaoForm"]/div[14]/input""").click()
    try: 
        Select(driver.find_element_by_xpath('//*[@id="tCompradores_length"]/label/select')).select_by_visible_text("Todos")
        break
    except:
        continue

# Para cada linha da tabela
table =  driver.find_element_by_xpath("""//*[@id="tCompradores"]""")
for row in table.find_elements_by_xpath(".//tr/td[5]/img"):
    
    #abrindo nova janela
    row.click()
    time.sleep(2)
    driver.switch_to_window(driver.window_handles[1])
    
    # Passando por captcha
    #clica no botao do captcha
    time.sleep(2)
    frame = driver.find_element_by_xpath('//*[@id="html_element"]/div/div/iframe')
    driver.switch_to.frame(frame)
    driver.find_element_by_xpath("//*[@id='recaptcha-anchor']").click()
    driver.switch_to.default_content()
    #escolhe audio
    time.sleep(5)
    frame = driver.find_element_by_xpath('//*[@id="bodyPrincipal"]/div[3]/div[4]/iframe')
    driver.switch_to.frame(frame)
    driver.find_element_by_xpath('//*[@id="rc-imageselect"]/div[3]/div[2]/div[1]/div[1]/div[2]').click()
    driver.switch_to.default_content()

    #recupera dados para aquela tabela
    # ...   

    # Fecha aba atual
    driver.close()
    driver.switch_to_window(driver.window_handles[0])

# Fecha janelas
print("Dados recolhidos")
time.sleep(5)
driver.close()
