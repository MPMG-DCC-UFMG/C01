import step_crawler
from step_crawler.functions_file import *


async def execute_steps(**missing_arguments):
    pages = {}
    page = missing_arguments['page']
    for modalidade in ["All", "Carta Convite", "Chamamento Público", "Concorrência", "Concurso", "Consulta Pública", "Dispensa de Licitação", "Edital de Credenciamento", "Inexigibilidade de Licitação", "Leilão", "Pregão Eletrônico", "Pregão Presencial", "Procedimento de Manifestação de Interesse", "Procedimento de Pré-qualificação", "Regime Diferenciado de Contratação", "Registro de Preços", "Seleção Pública Simplificada", "Tomada de Preço"]:
        await selecione(**missing_arguments, opcao=modalidade, xpath="//*[@id='edit-field-modalidade-de-licitacao-value']")
        espere(segs=2)
        await clique(**missing_arguments, xpath="//*[@id='edit-submit-programas-e-projetos']")
        espere(segs=2)
        await clique(**missing_arguments, xpath="/html/body/div[1]/div/div[5]/div/div/div/div/div/div/div/div/div[2]/div/ul/li/a")
        espere(segs=2)
    return pages
