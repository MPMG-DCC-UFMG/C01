import os
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.firefox.options import Options

for i in range(2020, 2021):

    directory = "/mnt/louise/diario-oficial-uberaba/" + str(i)
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    fp = webdriver.FirefoxProfile()

    mime_types = "application/pdf, application/zip"
    fp.set_preference("browser.download.folderList", 2)
    fp.set_preference("browser.download.dir", directory)
    fp.set_preference("browser.download.downloadDir", directory)
    fp.set_preference("browser.download.defaultFolder", directory)
    fp.set_preference("pdfjs.disabled", True)
    fp.set_preference("plugin.scan.Acrobat", "99.0");
    fp.set_preference("plugin.scan.plid.all", False);
    fp.set_preference("browser.download.manager.showWhenStarting", False)
    fp.set_preference("browser.download.manager.focusWhenStarting", False)
    fp.set_preference("browser.download.manager.closeWhenDone", True)
    fp.set_preference("browser.helperApps.neverAsk.saveToDisk", mime_types)

    options = Options()
    options.headless = True
    driver = webdriver.Firefox(options=options, firefox_profile=fp, service_log_path = os.path.join(os.getcwd(), "geckodriver.log"))
    
    driver.get("http://www.uberaba.mg.gov.br/portal/galeriaarquivosd,portavoz,arquivos,{}".format(i))
    WebDriverWait(driver, 60).until(ec.presence_of_element_located((By.CSS_SELECTOR, "div.claGaleriaBoxFileTable")))
    
    pages = driver.find_elements_by_css_selector("div.claGaleriaPaginas:first-of-type a")
    npages = len(pages)

    for p in range(npages):
        pages = driver.find_elements_by_css_selector("div.claGaleriaPaginas:first-of-type a")
        pages[p].click()
        time.sleep(10)
        WebDriverWait(driver, 60).until(ec.presence_of_element_located((By.CSS_SELECTOR, "img.claCursorPointer")))

        elem = driver.find_elements_by_css_selector("img.claCursorPointer")
        for i in range(len(elem)):
            time.sleep(2)
            elem[i].click()

        time.sleep(20)

    time.sleep(60)

    driver.quit()

driver.close()
