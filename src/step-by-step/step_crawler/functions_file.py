import io
import asyncio
import time
import uuid
from cssify import cssify
from PIL import Image
from captcha_solver.image_solver import ImageSolver


def range_(stop):
    return [i for i in range(stop)]


def print_(word):
    return word


def espere(segs):
    time.sleep(segs)


def gera_nome_arquivo():
    return "./{}.html".format(uuid.uuid4().hex)


async def wait_page(page):
    jsWait = "document.readyState === 'complete' || \
              document.readyState === 'iteractive'"
    while not (await page.evaluate(jsWait)):
        await page.waitFor(1)


async def clique(page, xpath):
    await page.waitForXPath(xpath)
    await page.click(cssify(xpath))
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


async def break_captcha(page, xpath_input, xpath_output):
    element = (await page.xpath(xpath_input))[0]
    image_data = await element.screenshot(path="image.jpg")
    image = Image.open(io.BytesIO(image_data))
    solver = ImageSolver(preprocessing=lambda x: x)
    text = solver.solve(image=image)
    # preenche o campo de texto com o resultado
    await page.type(cssify(xpath_output), text)
    return text