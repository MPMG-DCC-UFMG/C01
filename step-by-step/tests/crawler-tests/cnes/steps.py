from step_crawler.functions_file import *


async def execute_steps(**missing_arguments):
    estado = "ACRE"
    await selecione(opcao=estado, xpath="/html/body/div[2]/main/div/div[2]/"
                                        "div/form[1]/div[2]/div[1]/div/select",
                    **missing_arguments)
    espere(segs=2)
    for cidade in await opcoes(xpath="/html/body/div[2]/main/div/div[2]/div/"
                                     "form[1]/div[2]/div[2]/div/select",
                               exceto=["Selecione"], **missing_arguments):
        await selecione(opcao=cidade, xpath="/html/body/div[2]/main/div/"
                                            "div[2]/div/form[1]/div[2]/div[2]/"
                                            "div/select", **missing_arguments)
        await clique(xpath="/html/body/div[2]/main/div/div[2]/div/"
                           "form[2]/div/button", **missing_arguments)
