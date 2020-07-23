import step_crawler
from step_crawler.functions_file import *

async def execute_steps(**missing_arguments):
    estado = "ACRE"
    await selecione(**missing_arguments, opcao = estado, xpath = "/html/body/div[2]/main/div/div[2]/div/form[1]/div[2]/div[1]/div/select")
    espere(segs = 2)
    for cidade in await opcoes(**missing_arguments, xpath = "/html/body/div[2]/main/div/div[2]/div/form[1]/div[2]/div[2]/div/select", exceto = ["Selecione"]):
        await selecione(**missing_arguments, opcao = cidade, xpath = "/html/body/div[2]/main/div/div[2]/div/form[1]/div[2]/div[2]/div/select")
        await clique(**missing_arguments, xpath = "/html/body/div[2]/main/div/div[2]/div/form[2]/div/button")
