from util import *
import os
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import speech_recognition as sr

#### MAIN ####

browser = webdriver.Chrome(executable_path=r'chromedriver.exe')

anexos_txt = open('urls_de_anexos_em_pdf.txt','w')
anexos_txt.write('')
anexos_txt.close()


comarca_arq =  open("comarcas.txt", 'r')
comarcas_vet = []
for i in comarca_arq:
   comarcas_vet.append(int(i))
comarca_arq.close()


continuar(comarcas_vet, browser)

#minera(range(19,0,-1), comarcas_vet)



