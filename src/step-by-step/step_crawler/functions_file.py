import io
import asyncio
import time
import uuid
from cssify import cssify
from PIL import Image
from captcha_solver.image_solver import ImageSolver
from pyext import RuntimeModule


def imprime(texto):
    print(texto)
    return

def repete(vezes):
    return [i for i in range(vezes)]


def espere(segs):
    time.sleep(segs)


def gera_nome_arquivo():
    return "./{}.html".format(uuid.uuid4().hex)


async def wait_page(page):
    await page.waitForSelector("html")


async def clique(page, param):
    if type(param) == str:
        await page.waitForXPath(param)
        await page.click(cssify(param))
    else:
        param.click()
    await wait_page(page)

async def selecione(page, xpath, opcao):
    await page.waitForXPath(xpath)
    await page.type(cssify(xpath), opcao)
    await wait_page(page)


async def salva_pagina(page):
    content = await page.content()
    body = str.encode(content)
    return body


async def opcoes(page, xpath, exceto=None):
    if exceto is None:
        exceto = []
    options = []
    await page.waitForXPath(xpath)
    for option in (await page.xpath(xpath + "/option")):
        value = await option.getProperty("text")
        options.append(value.toString().split(":")[-1])
    return [value for value in options if value not in exceto]


async def for_clicavel(page, xpath):
    try:
        await clique(page, xpath)
        return True
    except:
        return False


async def elementos_filhos(page, xpath):
    base_xpath = xpath
    xpath_list = []
    elements = await page.xpath(xpath)
    for i in range(len(elements)):
        xpath_list.append(base_xpath + f"[{i+1}]")
    return xpath_list


async def pegue_os_links_da_paginacao(page, xpath_dos_botoes, xpath_dos_links, indice_do_botao_proximo=-1):
    clickable = True
    urls = []
    while clickable:
        urls += [await (await link.getProperty('href')).jsonValue() for link in await page.xpath(xpath_dos_links)]


        buttons = await page.xpath(xpath_dos_botoes)
        if len(buttons) != 0:
            next_button = buttons[indice_do_botao_proximo]
            before_click = await page.content()
            await next_button.click()
            after_click = await page.content()
            if before_click == after_click:
                clickable = False
        else:
            clickable = False


async def digite(page, xpath, texto):
    await page.type(cssify(xpath), texto)



async def nesse_elemento_esta_escrito(page, xpath, texto):
    elements = await page.xpath(xpath)
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


async def break_image_captcha(page, xpath_input, xpath_output, preprocessing=None):
    """This step downloads the captcha image then solves it and fills its respective form field

        :param page : a pyppeteer page
        :param xpath_input : XPATH of the captcha image element
        :param xpath_output : XPATH of the form field for captcha text.
        :param preprocessing (optional): The preprocessing function, to be applied
                                         before character recognition. Defaults to None.
        :returns text: the string representing the captcha characters
    """

    element = (await page.xpath(xpath_input))[0]
    image_data = await element.screenshot(type='jpeg')
    image = Image.open(io.BytesIO(image_data))
    if preprocessing:
        module = RuntimeModule.from_string("preprocessing", preprocessing)
        solver = ImageSolver(preprocessing=module.preprocessing)
    else:
        solver = ImageSolver()
    text = solver.solve(image=image)
    type_function = f"(text) => {{ (document.querySelector('{cssify(xpath_output)}')).value = text; }}"
    await page.evaluate(type_function, text)
    return text


async def element_in_page(page, xpath):
    """This step returns True if there's any element given a xpath, otherwise, returns False

        :param page : a pyppeteer page
        :returns bool: True or False
    """
    return bool(await page.xpath(xpath))
