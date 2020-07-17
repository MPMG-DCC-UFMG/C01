from util import *
import os
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import speech_recognition as sr

def dv10(pNumProc):
  vDigito = -1
  vSoma = 0
  v1NumProc = pNumProc[0:12]
  if v1NumProc=="":
    return 0
  vTamanho = len(v1NumProc)
  vMultiplicador = (vTamanho % 2) + 1 # 1 se par, 2 se impar
  for j in range(vTamanho):
    vParcela = int(v1NumProc[j:j+1]) * vMultiplicador
    if vParcela >= 10:
      vParcela = (vParcela % 10) + 1
    vMultiplicador = 3 - vMultiplicador # Alterna entre 1 e 2
    vSoma += vParcela
  vDigito = (10 - (vSoma % 10)) % 10
  return vDigito


def monta_cod_in(num):
  return str(num) + str(dv10(num))

def monta_num_unica(num_processo, ano, jtr, comarca):
  codigo_in = monta_cod_in(str(comarca)+str(ano)[-2:]+preencheZeros(num_processo,6))[-7:]
  dv_num_unica = calcula_mod97(codigo_in, ano, jtr, comarca)

  num_unica = codigo_in + '-'
  num_unica = num_unica + str(dv_num_unica)+'.'
  num_unica = num_unica + str(ano)+'.'+str(jtr)[0]+'.'+str(jtr)[1:]+'.'+preencheZeros(str(comarca),4)
  return num_unica


def calcula_mod97(NNNNNNN, AAAA, JTR, OOOO):
   valor1 = ""; 
   resto1 = 0; 
   valor2 = ""; 
   resto2 = 0; 
   valor3 = ""; 
   valor1 = preencheZeros(NNNNNNN, 7); 
   resto1 = int(valor1) % 97; 
   valor2 = preencheZeros(resto1, 2) + preencheZeros(AAAA, 4) + preencheZeros(JTR, 3); 
   resto2 = int(valor2) % 97; 
   valor3 = preencheZeros(resto2, 2) + preencheZeros(OOOO, 4) + "00"; 
   return preencheZeros(98 - (int(valor3) % 97), 2 ); 

def valida_mod97( NNNNNNN, DD, AAAA, JTR, OOOO):
   valor1 = ""; 
   resto1 = 0; 
   valor2 = ""; 
   resto2 = 0; 
   valor3 = ""; 
   valor1 = preencheZeros(NNNNNNN, 7); 
   resto1 = int(valor1) % 97; 
   valor2 = preencheZeros(resto1, 2) + preencheZeros(AAAA, 4) + preencheZeros(JTR, 3); 
   resto2 = int(valor2) % 97; 
   valor3 = preencheZeros(resto2, 2) + preencheZeros(OOOO, 4) + preencheZeros(DD, 2); 
   return ((int(valor3) % 97) == 1)

def preencheZeros(numero, quantidade):
   temp = str(numero); 
   retorno = ""; 
   if quantidade < len(temp):
         return temp
   else: 
      for i in range(quantidade - len(temp)):
         retorno = "0" + retorno; 
      return retorno + temp
def quebra_captcha(browser, time_sleep=2):
   captcha_chave = ""
   botao_baixar_audio = browser.find_element_by_link_text("Baixar o áudio")
   botao_baixar_audio.click()

   esperar_arquivo(r'C:\\Users\\Tales Panoutsos\\Downloads\\audio.wav', 2)
   captcha_chave = audio_to_frase('C:\\Users\\Tales Panoutsos\\Downloads\\audio.wav')
   captcha_form = browser.find_element_by_xpath("/html/body/table/tbody/tr[3]/td/table/tbody/tr[2]/td[2]/input")

   browser.execute_script("arguments[0].value='';", captcha_form)
   if len(captcha_chave)>4:
      browser.execute_script("arguments[0].value='"+captcha_chave[-5:]+"';", captcha_form)
   else:
      browser.execute_script("arguments[0].value='00000';", captcha_form)
   captcha_form.send_keys(Keys.ENTER)

   os.system('cd "C:/Users/Tales Panoutsos/Downloads" & del audio.wav')
   time.sleep(time_sleep)
   return


def descobrir_fim(browser, comarca, ano, tolerancia):
   cod_inicial_atual = 500000
   cod_inicial_a_somar = 250000
   while cod_inicial_a_somar>1:
      if cod_inicial_a_somar<100:
         tolerancia = cod_inicial_a_somar
      if verificar_paginas(browser, comarca, ano, cod_inicial_atual, tolerancia)==1:
         cod_inicial_atual = cod_inicial_atual + cod_inicial_a_somar
      else:
         cod_inicial_atual = cod_inicial_atual - cod_inicial_a_somar
      cod_inicial_a_somar = int(cod_inicial_a_somar/2)
   return cod_inicial_atual

def carregar_pagina(browser,url):
  browser.get(url)
    



def esperar_arquivo(path, time_sleep):
  while not os.path.exists(r""+path):
     print('Esperando arquivo')
     time.sleep(2)
   
   
def audio_to_frase(nome_audio):
  r = sr.Recognizer()
  with sr.WavFile(nome_audio) as source:              
      audio = r.record(source)                        
  try:
      return(r.recognize_google(audio, language = "pt-BR"))
  except LookupError:
    return("error")

def link_maker(ano, cod_unico, cod_comarca, tipo_pagina):
   link = 'www4.tjmg.jus.br/juridico/sf/proc_'+tipo_pagina+'.jsp?listaProcessos='+preencheZeros(ano,2)+preencheZeros(cod_unico,6)+'&comrCodigo='+str(int(cod_comarca))+'&numero=1'
   return link


def verificar_paginas(browser,comarca,ano,cod_inicial,num_pags):
   cod = 0
   while cod < num_pags:
      link = link_maker(ano, cod_inicial+cod, comarca, 'complemento')
      carregar_pagina(browser,"https://"+link)
      code_da_pag = browser.page_source

      verificar_exibição_da_pagina(browser, code_da_pag, link)

      if code_da_pag.find('NUMERAÇÃO ÚNICA:')!=-1:
         break
      cod = cod + 1

   if cod == num_pags:
      return 0
   else:
      return 1
def verificar_exibição_da_pagina(browser, code_da_pag, url):
    try:
      while browser.find_elements_by_xpath("/html/body/table/tbody/tr[3]/td/table/tbody/tr[2]/td[2]/input") != []:
        quebra_captcha(browser)
        code_da_pag = browser.page_source
    except:
      print('Captcha em pagina de download de pdf')

    while code_da_pag.find("A Consulta Processual aos processos de 1a. Instância encontra-se indisponível.") !=-1:
      print('Fora do ar')
      time.sleep(5)
      carregar_pagina(browser,url)
      code_da_pag = browser.page_source 

    while code_da_pag.find('Não é possível acessar esse site')!=-1:
      print('Não é possível acessar esse site')
      time.sleep(5)
      carregar_pagina(browser,url)
      code_da_pag = browser.page_source 

    while code_da_pag.find('ERR_INTERNET_DISCONNECTED')!=-1:
      print('Sem internet')
      time.sleep(5)
      carregar_pagina(browser,url)
      code_da_pag = browser.page_source 

def coleta_2(browser,ano,com,cod, instancia = 1, num_pagina = 0): 
   link = link_maker(ano, cod, com, 'resultado', instancia, num_pagina)
   carregar_pagina(browser,"https://"+link)

   verificar_exibição_da_pagina(browser, browser.page_source, link)
   code_da_pag = browser.page_source

   if code_da_pag.find('NUMERAÇÃO ÚNICA:')!=-1:
      tipos_paginas = []
      urls = []
      links_pag_para_baixar = browser.find_elements_by_xpath('/html/body/table/tbody/tr/td/b/a')
      
      

      if links_pag_para_baixar!=[]:
        arq_de_urls_para_baixar = open('urls_para_baixar.txt', 'a')
        arq_de_urls_para_baixar.write(preencheZeros(str(int(com)),4)+preencheZeros(str(ano),2)+preencheZeros(str(cod),6)+', '+str(instancia)+', '+str(num_pagina)+', ') ##### MUDANÇA
        for link_pag_para_baixar in links_pag_para_baixar:
          link_text = link_pag_para_baixar.get_attribute('href')

          if instancia==1:
            tipo_pagina = link_text[link_text.find('proc_')+len('proc_'):link_text.find('.jsp?')] ##### MUDANÇA
          else:
            tipo_pagina = link_text[link_text.find('proc_')+len('proc_'):link_text.find('2.jsp?')] ##### MUDANÇA

            
          if tipo_pagina == 'movimentacoes' or tipo_pagina == 'complemento':
            tipos_paginas.append(tipo_pagina)
            urls.append(link_text)
          else:
            arq_de_urls_para_baixar.write(link_pag_para_baixar.get_attribute('href') +', ')       

        #arq_de_urls_para_baixar.write('\n')       
        #arq_de_urls_para_baixar.close()


        for (tipo_pagina,url) in zip(tipos_paginas,urls):
          carregar_pagina(browser,url)
          verificar_exibição_da_pagina(browser, browser.page_source, url)
          code_da_pag = browser.page_source
          if instancia==1:
            nome_arquivo = tipo_pagina+' - ' + preencheZeros(str(int(com)),4)+preencheZeros(str(ano),2)+preencheZeros(str(cod),6)+".html"
          else:
            nome_arquivo = tipo_pagina + '2('+ num_pagina +')- ' + preencheZeros(str(int(com)),4)+preencheZeros(str(ano),2)+preencheZeros(str(cod),6)+".html" ##### MUDANÇA

          with open("paginas\\"+nome_arquivo, 'w') as page:
            page.write(str(browser.page_source.encode("utf-8", 'ignore'), 'utf-8', 'ignore'))


          butoes_anexo = browser.find_elements_by_xpath('/html/body/table/tbody/tr/td[1]/a')
          for butao in butoes_anexo:
             butao.click()                              
          if tipo_pagina == "movimentacoes":
            links_anexos = browser.find_elements_by_xpath('/html/body/table/tbody/tr/td/table/tbody/tr/td[4]/a')
          if tipo_pagina == "complemento":                
            links_anexos = browser.find_elements_by_xpath('/html/body/table/tbody/tr/td/table/tbody/tr')
          links = [] 
          num_anexo=0
          
          if links_anexos!=[]:
            #anexos_em_pdf = open('urls_de_anexos_em_pdf.txt','a')
            #print(anexos_em_pdf)
            #arq_de_urls_para_baixar.write(preencheZeros(str(int(com)),4)+preencheZeros(str(ano),2)+preencheZeros(str(cod),6)+', '+str(instancia)+', '+str(num_pagina)+', ')
            for link_web_element in links_anexos:  
              nome_arquivo_pdf_antigo = link_web_element.text

              if link_web_element.text[-4:]=='.pdf' or link_web_element.text[-5:]=='.html':
                url_anexo = link_web_element.get_attribute('href')
                arq_de_urls_para_baixar.write(str(url_anexo)+', ')

              else:
                funcao_para_extrair_url = str(link_web_element.get_attribute('onclick'))
                inicio_codigo_do_arq = funcao_para_extrair_url.find("'")
                fim_codigo_do_arq = funcao_para_extrair_url.find("'",inicio_codigo_do_arq)
                codigo_do_arq = funcao_para_extrair_url[inicio_codigo_do_arq:fim_codigo_do_arq]

                if codigo_do_arq!= '':  
                  url_anexo = 'www4.tjmg.jus.br/juridico/sf/relatorioAcordao?numeroVerificador='+str(codigo_do_arq)
                  arq_de_urls_para_baixar.write(str(url_anexo)+', ')

            
            # for link_anexo in links:
            #   carregar_pagina(browser,link_anexo)
            #   verificar_exibição_da_pagina(browser, browser.page_source,url)
            #   code_da_pag = browser.page_source
            #   nome_arquivo_anexo = "anexo("+ str(num_anexo) + ") - " + preencheZeros(str(int(com)),4)+preencheZeros(str(ano),2)+preencheZeros(str(cod),6)+".html"
            #   try:
            #     with open("paginas/"+nome_arquivo_anexo, 'w') as page:
            #       page.write(str(browser.page_source.encode("utf-8", 'ignore'),'utf-8', 'ignore'))
            #   except:
            #     arq_de_urls_para_baixar.write(str(link_anexo)+', ')
            #   num_anexo=num_anexo+1
        arq_de_urls_para_baixar.write('\n')
        arq_de_urls_para_baixar.close()

      return 1
   else:
      return 0


def link_maker(ano, cod_unico, cod_comarca, tipo_pagina, instancia = 1, num = 0):
  if instancia == 1:
    link = 'www4.tjmg.jus.br/juridico/sf/proc_'+tipo_pagina+'.jsp?listaProcessos='+preencheZeros(ano,2)+preencheZeros(cod_unico,6)+'&comrCodigo='+str(int(cod_comarca))+'&numero='+str(instancia)
  else:
    link = 'www4.tjmg.jus.br/juridico/sf/proc_'+tipo_pagina+'2.jsp?listaProcessos=1'+preencheZeros(cod_comarca,4)+ preencheZeros(ano,2) +preencheZeros(cod_unico,6)+'0'+preencheZeros(num,3) 
  return link


            
def minera(browser, range_ano, comarca_vet, comarca_inicio = 2, comarca_final= -1, cod_inicial = 0, cod_final = 999999, procurar_fim = 1, tolerancia_descobrir_fim=25, tolerancia_paginas_vazias = 100):
  pos_inicial_comarca = comarca_vet.index(comarca_inicio)
  if comarca_final!=-1:
    pos_final_comarca = comarca_vet.index(comarca_final)
  else:
    pos_final_comarca = comarca_vet[-1]

  for ano in range_ano:
    for com in comarca_vet[pos_inicial_comarca : pos_final_comarca+1]:
      paginas_vazias = 0
      if procurar_fim == 1:
        cod_final = descobrir_fim(browser,com, ano, tolerancia_descobrir_fim)
        print("Comarca: " + str(com) + " Codigo Final:"+str(cod_final))
      pagina_coletada=0
      cod=cod_inicial
      while cod<cod_final:
        try:
          pagina_coletada = coleta_2(browser,ano,com,cod,1)
        except:
          print('exceptionnnnnnnn')
          parada = open('parada.txt','w')
          parada.write(str(ano)+' '+str(com)+' '+str(cod))
          parada.close()
        if pagina_coletada == 1:
          num_pagina=0
          while coleta_2(browser,ano,com,cod,2,num_pagina)==1 or num_pagina==0:
            num_pagina=num_pagina+1
          
          paginas_vazias = 0

        else:
          paginas_vazias = paginas_vazias + 1

        if paginas_vazias > tolerancia_paginas_vazias and cod > cod_final:
          break

        cod=cod+1

def continuar(comarca_vet, browser):
  parada = open('parada.txt','r')
  onde_parou = parada.read()
  parada.close()
  onde_parou = onde_parou.split()

  ano = int(onde_parou[0])
  comarca = int(onde_parou[1])
  codigo = int(onde_parou[2])

  prox_comarca = comarca_vet[comarca_vet.index(comarca)+1]

  minera(browser, [ano], [comarca], comarca_inicio=comarca, cod_inicial = codigo)
  minera(browser, [ano], comarca_vet, comarca_inicio=prox_comarca)
  minera(browser, range(ano-1,0,-1), comarca_vet)

