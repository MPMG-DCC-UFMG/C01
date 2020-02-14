
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import datetime
import time
import os


from PIL import Image
import cv2
import pytesseract

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

def solve_captcha(img_path):
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    # img[img>110] = 240
    # img[img<30] = 240
    img[img>53]=250 
    img = img[:,20:150]
    return pytesseract.image_to_string(img)


def preenche_form(driver,option):
    same_page = True
    while same_page:
        try:
            wait = WebDriverWait(driver, 5)
            wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="licitacaoPesquisaSituacaoForm"]/div[14]/input')))
        except TimeoutException:
            return

        try:    
            situacao = driver.find_element_by_xpath("""//*[@id="licitacaoPesquisaSituacaoForm"]/div[5]/span/input""")
            situacao.clear()
            situacao.send_keys(option)

            with open('captcha.png', 'wb') as file:
                file.write(driver.find_element_by_xpath('//*[@id="img_captcha"]').screenshot_as_png)
            resposta = solve_captcha('captcha.png')

            while resposta == "":
                driver.find_element_by_xpath("""//*[@id="licitacaoPesquisaSituacaoForm"]/div[13]/div[2]/img[2]""").click()
                print("recarregando imagem")
                time.sleep(1)
                with open('captcha.png', 'wb') as file:
                    file.write(driver.find_element_by_xpath('//*[@id="img_captcha"]').screenshot_as_png)

                resposta = solve_captcha('captcha.png')

            print(resposta)

            driver.find_element_by_xpath("""//*[@id="pQuestionAvancada"]""").send_keys(resposta)
            driver.find_element_by_xpath("""//*[@id="licitacaoPesquisaSituacaoForm"]/div[14]/input""").click()
            try:
                if driver.find_element_by_xpath("""//*[@id="msgs_fechar"]""").get_attribute('innerHTML') == X:
                    same_page = False
            except:
                continue
        except:
            continue
            
            


url = "https://www.licitacoes-e.com.br/aop/pesquisar-licitacao.aop?opcao=preencherPesquisar"

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")

driver = webdriver.Chrome(options=options)
driver.get(url)

print("Pagina carregada")
time.sleep(2)

preenche_form(driver, "Publicada")
print("cabo")
driver.close()


    






# situacao.submit()



# situacao = Select(driver.find_element_by_name('select0'))
# select.select_by_visible_text("Publicada")

# select = Select(driver.find_element_by_id('situacoes'))
# select.select_by_visible_text("Publicada")

# select by visible text
# select.select_by_visible_text('Selecione a situação')

