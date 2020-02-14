import os
from datetime import datetime
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


driver = webdriver.Firefox()
driver.get("https://www.registrodeprecos.mg.gov.br/aasi/do/filtrarRPs")
assert "SIRP" in driver.title
elem = driver.find_element_by_class_name("botao")
elem.click()
elem = driver.find_element_by_class_name("paginacaoTexto")
numeroRegistros=elem.text
numeroRegistros, lixo = numeroRegistros.split(' reg', 1)
lixo, numeroRegistros = numeroRegistros.split('al: ',1)
numeroRegistros = numeroRegistros.replace(',','')
numeroRegistros = int(numeroRegistros)

print(elem.text)
print('numero: ', numeroRegistros)
pbar = tqdm(total=numeroRegistros)


registrosSalvos = 1
registrosIteracao = 4547

dataConsulta = datetime.today().strftime('%Y_%m_%d')

if not os.path.exists(dataConsulta):
    os.makedirs(dataConsulta)

# while(registrosSalvos<=numeroRegistros):
    
driver.get("https://www.registrodeprecos.mg.gov.br/aasi/do/selecionarRP?metodo=selecionarPub&id="+str(registrosIteracao))

if 'operação não pôde ser completada devido aos erros' not in driver.page_source:
    pasta = os.path.join(dataConsulta, str(registrosIteracao))
    if not os.path.exists(pasta):
        os.makedirs(pasta)
    
    # REGISTRO DE PREÇO 
    with open(os.path.join(pasta,'registro_de_preco_'+str(registrosIteracao)+'.html'), 'w') as f:
        f.write(driver.page_source)

    # ITENS DO PLANEJAMENTO
    urlBaseItens = "https://www.registrodeprecos.mg.gov.br/aasi/do/buscarPlanCons?metodo="
    driver.get("https://www.registrodeprecos.mg.gov.br/aasi/do/buscarPlanCons?metodo=buscarPlanAdesao&idRP="+str(registrosIteracao))
    if 'operação não pôde ser completada devido aos erros' not in driver.page_source:
        with open(os.path.join(pasta,'itens_planejamento_'+str(registrosIteracao)+'_1.html'), 'w') as f:
            f.write(driver.page_source)
        temProxima = True
        while(temProxima):
            try:
                proximaPagina = driver.find_element_by_link_text('Próximo')
                proximaPagina = proximaPagina.get_attribute('href')
                driver.get(proximaPagina)
                with open(os.path.join(pasta,'itens_planejamento_'+str(registrosIteracao)+"_"+str()+'.html'), 'w') as f:
                    f.write(driver.page_source)
            except:
                temProxima = False
                pass

    # ITENS PRECOS REGISTROS
    driver.get("https://www.registrodeprecos.mg.gov.br/aasi/do/consultaInfoAtaRP?metodo=exibirAnexoAta&anexo=I&idRP="+str(registrosIteracao))
    if 'operação não pôde ser completada devido aos erros' not in driver.page_source:
        with open(os.path.join(pasta,'itens_precos_registros_'+str(registrosIteracao)+'.html'), 'w') as f:
            f.write(driver.page_source)
            
    # ORGAOS PARTICIPANTES
    driver.get("https://www.registrodeprecos.mg.gov.br/aasi/do/consultaInfoAtaRP?metodo=exibirAnexoAta&anexo=II&idRP="+str(registrosIteracao))
    if 'operação não pôde ser completada devido aos erros' not in driver.page_source:
        with open(os.path.join(pasta,'orgaos_participantes_'+str(registrosIteracao)+'.html'), 'w') as f:
            f.write(driver.page_source)
            
    # FORNECEDORES PARTICIPANTES
    driver.get("https://www.registrodeprecos.mg.gov.br/aasi/do/buscarFornecedores?metodo=buscarFornecedores&operacao=FORN_PARTICIPANTES&idRP="+str(registrosIteracao))
    if 'operação não pôde ser completada devido aos erros' not in driver.page_source:
        with open(os.path.join(pasta,'fornecedores_participantes_'+str(registrosIteracao)+'.html'), 'w') as f:
            f.write(driver.page_source)
            
    # DOCUMENTOS
    driver.get("https://www.registrodeprecos.mg.gov.br/aasi/do/consultarArquivos?metodo=buscarArquivosRP&idRP="+str(registrosIteracao))
    if 'operação não pôde ser completada devido aos erros' not in driver.page_source:
        with open(os.path.join(pasta,'documentos_'+str(registrosIteracao)+'.html'), 'w') as f:
            f.write(driver.page_source)
            
    registrosSalvos+=1
    pbar.update(1)
registrosIteracao+=1

pbar.close()
driver.close()
driver.quit()