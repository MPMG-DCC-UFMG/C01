import sys 
sys.path.append("code")
from functions_file import *

async def execute_steps(**missing_argument):
    for estado in await opcoes(**{'xpath': '/html/body/div[2]/main/div/div[2]/div/form[1]/div[2]/div[1]/div/select'}, **missing_argument):
        await selecione(**{'opcao': 'estado', 'xpath': '/html/body/div[2]/main/div/div[2]/div/form[1]/div[2]/div[1]/div/select'}, **missing_argument)
        espere(**{'segs': 2})
        for cidade in await opcoes(**{'xpath': '/html/body/div[2]/main/div/div[2]/div/form[1]/div[2]/div[2]/div/select'}, **missing_argument):
            await selecione(**{'opcao': 'cidade', 'xpath': '/html/body/div[2]/main/div/div[2]/div/form[1]/div[2]/div[2]/div/select'}, **missing_argument)
            espere(**{'segs': 2})
            await clique(**{'xpath': '/html/body/div[2]/main/div/div[2]/div/form[2]/div/button'}, **missing_argument)
            espere(**{'segs': 2})
            while await for_clicavel(**{'xpath': '/html/body/div[2]/main/div/div[2]/div/div[3]/div/div/div/ul/li[5]/a'}, **missing_argument):
                espere(**{'segs': 2})
