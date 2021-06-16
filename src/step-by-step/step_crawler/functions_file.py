import io
import asyncio
import time
import uuid
from cssify import cssify
from PIL import Image
#from captcha_solver.image_solver import ImageSolver
from pyext import RuntimeModule


def espere(segundos):
    time.sleep(segundos)

def intervalo(parada):
    return [i for i in range(parada)]

def imprimir(texto):#used for tests
    return texto

def gera_nome_do_arquivo():
    return "./{}.html".format(uuid.uuid4().hex)


async def espere_a_pagina(pagina):
    jsWait = "document.readyState === 'complete' || \
              document.readyState === 'iteractive'"
    while not (await pagina.evaluate(jsWait)):
        await pagina.waitFor(1)


async def clique(pagina, xpath):
    await pagina.waitForXPath(xpath)
    await pagina.click(cssify(xpath))
    await espere_a_pagina(pagina)


async def selecione_isso_em(pagina, opcao, xpath):
    await pagina.waitForXPath(xpath)
    await pagina.type(cssify(xpath), opcao)
    await espere_a_pagina(pagina)


async def salva_pagina(pagina):
    content = await pagina.content()
    body = str.encode(content)
    return body


async def opcoes_em(pagina, xpath, exceto=None):
    if exceto is None:
        exceto = []
    options = []
    await pagina.waitForXPath(xpath)
    for option in (await pagina.xpath(xpath + "/option")):
        value = await option.getProperty("text")
        options.append(value.toString().split(":")[-1])
    return [value for value in options if value not in exceto]


async def e_clicavel(pagina, xpath):
    try:
        await clique(pagina, xpath)
        return True
    except:
        return False



async def pegue_os_links_da_paginacao(pagina, xpath_dos_botoes, xpath_dos_links, indice_do_botao_de_proximo=-1):
    clickable = True
    urls = []
    while clickable:
        urls += [await (await link.getProperty('href')).jsonValue() for link in await pagina.xpath(xpath_dos_links)]


        buttons = await pagina.xpath(xpath_dos_botoes)
        if len(buttons) != 0:
            next_button = buttons[indice_do_botao_de_proximo]
            before_click = await pagina.content()
            await next_button.click()
            after_click = await pagina.content()
            if before_click == after_click:
                clickable = False
        else:
            clickable = False


async def digite(pagina, xpath, texto):
    await pagina.type(cssify(xpath), texto)



async def esta_escrito_em(pagina, texto, xpath):
    elements = await pagina.xpath(xpath)
    if len(elements):
        element = elements[0]
    else:
        return 0

    element_text_content = await element.getProperty('textContent')
    element_text = await (element_text_content).jsonValue()
    if texto in element_text:
        return True
    else:
        return False


# async def quebre_o_capcha(pagina, xpath_do_input, xpath_do_output, preprocessamento=None):
#     """This step downloads the captcha image then solves it and fills its respective form field

#         :param pagina : a pyppeteer page
#         :param xpath_do_input : XPATH of the captcha image element
#         :param xpath_do_output : XPATH of the form field for captcha text.
#         :param preprocessamento (optional): The preprocessing function, to be applied
#                                          before character recognition. Defaults to None.
#         :returns text: the string representing the captcha characters
#     """

#     element = (await pagina.xpath(xpath_do_input))[0]
#     image_data = await element.screenshot(type='jpeg')
#     image = Image.open(io.BytesIO(image_data))
#     if preprocessamento:
#         module = RuntimeModule.from_string("preprocessing", preprocessamento)
#         solver = ImageSolver(preprocessing=module.preprocessing)
#     else:
#         solver = ImageSolver()
#     text = solver.solve(image=image)
#     type_function = f"(text) => {{ (document.querySelector('{cssify(xpath_do_output)}')).value = text; }}"
#     await pagina.evaluate(type_function, text)
#     return text


async def elemento_existe_na_pagina(pagina, xpath):
    """This step returns True if there's any element given a xpath, otherwise, returns False

        :param pagina : a pyppeteer page
        :returns bool: True or False
    """
    return bool(await pagina.xpath(xpath))
