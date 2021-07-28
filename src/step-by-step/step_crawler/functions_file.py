import io
import asyncio
import time
import uuid
from cssify import cssify
from PIL import Image
from captcha_solver.image_solver import ImageSolver
from pyext import RuntimeModule

"""
    Attention: the string arguments on step functions are their names displayed
    in interface. If you want to customize the display showed at the step-by-
    step block, please make sure to pass a string as a parameter.

"""

def step(display):
    def function(f):
        f.is_step = True
        f.display = display
        return f

    return function

@step("Imprimir")
def imprime(texto):
    print(texto)
    return


@step("Repetir")
def repete(vezes):
    return [i for i in range(vezes)]


@step("Esperar")
def espere(segundos):
    time.sleep(segundos)


def gera_nome_arquivo():
    return "./{}.html".format(uuid.uuid4().hex)


async def espere_pagina(pagina):
    await pagina.waitForSelector("html")


@step("Clicar")
async def clique(pagina, elemento):
    if type(elemento) == str:
        await pagina.waitForXPath(elemento)
        await pagina.click(cssify(elemento))
    else:
        elemento.click()
    await espere_pagina(pagina)


@step("Selecionar")
async def selecione(pagina, xpath, opcao):
    await pagina.waitForXPath(xpath)
    await pagina.type(cssify(xpath), opcao)
    await espere_pagina(pagina)


@step("Salvar Página")
async def salva_pagina(pagina):
    content = await pagina.content()
    body = str.encode(content)
    return body


@step("Opções")
async def opcoes(pagina, xpath, exceto=None):
    if exceto is None:
        exceto = []
    options = []
    await pagina.waitForXPath(xpath)
    for option in (await pagina.xpath(xpath + "/option")):
        value = await option.getProperty("text")
        options.append(value.toString().split(":")[-1])
    return [value for value in options if value not in exceto]


@step("É clicável")
async def for_clicavel(pagina, xpath):
    try:
        await clique(pagina, xpath)
        return True
    except:
        return False


@step("Obter elementos filhos")
async def elementos_filhos(pagina, xpath):
    base_xpath = xpath
    xpath_list = []
    elements = await pagina.xpath(xpath)
    for i in range(len(elements)):
        xpath_list.append(base_xpath + f"[{i+1}]")
    return xpath_list


async def pegue_os_links_da_paginacao(pagina, xpath_dos_botoes, xpath_dos_links, indice_do_botao_proximo=-1):
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


@step("Digitar em")
async def digite(pagina, xpath, texto):
    await pagina.type(cssify(xpath), texto)


@step("Está escrito")
async def nesse_elemento_esta_escrito(pagina, xpath, texto):
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


@step("Quebrar captcha de imagem")
async def quebrar_captcha_imagem(pagina, xpath_do_elemento_captcha, xpath_do_campo_a_preencher, funcao_preprocessamento=None):
    """This step downloads the captcha image then solves it and fills its respective form field

        :param pagina : a pyppeteer page
        :param xpath_do_elemento_captcha : XPATH of the captcha image element
        :param xpath_do_campo_a_preencher : XPATH of the form field for captcha text.
        :param funcao_preprocessamento (optional): The preprocessing function, to be applied
                                         before character recognition. Defaults to None.
        :returns text: the string representing the captcha characters
    """

    element = (await pagina.xpath(xpath_do_elemento_captcha))[0]
    image_data = await element.screenshot(type='jpeg')
    image = Image.open(io.BytesIO(image_data))
    if funcao_preprocessamento:
        module = RuntimeModule.from_string("preprocessing", funcao_preprocessamento)
        solver = ImageSolver(preprocessing=module.funcao_preprocessamento)
    else:
        solver = ImageSolver()
    text = solver.solve(image=image)
    type_function = f"(text) => {{ (document.querySelector('{cssify(xpath_do_campo_a_preencher)}')).value = text; }}"
    await pagina.evaluate(type_function, text)
    return text


@step("Checar se elemento existe na página")
async def elemento_existe_na_pagina(pagina, xpath):
    """This step returns True if there's any element given a xpath, otherwise, returns False

        :param pagina : a pyppeteer page
        :returns bool: True or False
    """
    return bool(await pagina.xpath(xpath))
