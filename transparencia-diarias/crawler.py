from selenium import webdriver
from selenium.webdriver.support.ui import Select
import time

chrome_options = webdriver.ChromeOptions()

# define o diretório no qual os arquivos baixados serão armazenados
prefs = {'download.default_directory' : '/home/lorena/Desktop/Lorena/Programming/C04/transparencia-diarias/csvs'}

chrome_options.add_experimental_option('prefs', prefs)
driver = webdriver.Chrome(chrome_options=chrome_options)

driver.get('http://transparencia.mg.gov.br/estado-pessoal/diarias')
time.sleep(2)

year_button = '//*[@id="jform_ano"]'
submit_button = '//*[@id="estado_despesadiarias-form"]/div[7]/div/button'
show_all = '//*[@id="DataTables_Table_0_wrapper"]/div[1]/ul/li[5]/a'
csv_button = '//*[@id="DataTables_Table_0_wrapper"]/div[1]/a[2]'

# relativos aos anos 2002 a 2020
for i in range(1, 20):
	driver.find_element_by_xpath(year_button).click()
	year = '//*[@id="jform_ano"]/option[' + str(i) + ']'
	driver.find_element_by_xpath(year).click()
	
	driver.find_element_by_xpath(submit_button).click()
	time.sleep(2)
	driver.find_element_by_xpath(show_all).click()
	driver.find_element_by_xpath(csv_button).click()