# -*- coding: utf-8 -*- 
import os
from datetime import datetime
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import csv


driver = webdriver.Firefox()
driver.get("http://www.itabirito.mg.gov.br/oficio/")
assert "Prefeitura" in driver.title

elements = driver.find_elements_by_class_name('clr-prefeitura')
links_pgs = []
for elem in elements:
    try:
        link = driver.find_element_by_link_text(elem.text)
        if link:
            links_pgs.append(link.get_attribute("href"))
    except:
        pass

numeroRegistros = len(links_pgs)-1

pbar = tqdm(total=numeroRegistros)

registrosSalvos = 1
title_list=[]
paragraphs_list=[]
external_links_list=[]
pdfs_list=[]

dataConsulta = datetime.today().strftime('%Y_%m_%d')

if not os.path.exists(dataConsulta):
    os.makedirs(dataConsulta)
    
if not os.path.exists(dataConsulta):
    os.makedirs(dataConsulta)
    
while(registrosSalvos<=numeroRegistros):
    
    # print('links_pgs[registrosSalvos]: ', links_pgs[registrosSalvos])
    
    driver.get(links_pgs[registrosSalvos])
    
    title = driver.find_elements_by_class_name('clr-prefeitura')[1].text
    
    paragraphs = driver.find_element_by_xpath("//div[@class='content col-xs-12 col-sm-12 col-md-12 col-lg-12']//p").text
    
    links = driver.find_elements_by_xpath("//div[@class='content col-xs-12 col-sm-12 col-md-12 col-lg-12']//a")
    pdfs=""
    external_links=""
    for link in links:
        if ('.pdf' in str(link.get_attribute("href")) ):
            pdfs+=link.get_attribute("href")+"\n"
        else:
            external_links+=link.get_attribute("href")+"\n"
            
    title_list.append(title)
    paragraphs_list.append(paragraphs)
    external_links_list.append(external_links)
    pdfs_list.append(pdfs)
    
    registrosSalvos+=1
    pbar.update(1)
    
if os.path.exists('diario-oficial-itabirito.csv'):
    append_write = 'a' # append if already exists
else:
    append_write = 'w' # make a new file if not

with open('diario-oficial-itabirito.csv', append_write) as csvfile:
    fieldnames = ['titulo', 'paragrafo','links_externos', 'pdfs_anexos']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for i in range(0, registrosSalvos-1):
        writer.writerow({'titulo': title_list[i], 'paragrafo': paragraphs_list[i], 'links_externos':external_links_list[i], 'pdfs_anexos':pdfs_list[i]})
        

pbar.close()
driver.close()
driver.quit()