import io
import asyncio
import time
import uuid
from cssify import cssify
from PIL import Image
from captcha_solver.image_solver import ImageSolver
from pyext import RuntimeModule


def step(function):
    function.is_step = True
    return function

@step
def imprime(texto):
    print(texto)
    return


@step
def repete(vezes):
    return [i for i in range(vezes)]


@step
def espere(segs):
    time.sleep(segs)


def gera_nome_arquivo():
    return "./{}.html".format(uuid.uuid4().hex)


async def wait_page(page):
    await page.waitForSelector("html")


@step
async def clique(page, param):
    if type(param) == str:
        await page.waitForXPath(param)
        elements = await page.xpath(param)
        if len(elements) == 1:
            await elements[0].click()
        else:
            raise Exception('XPath points to non existent element, or multiple elements!')
    else:
        param.click()
    await wait_page(page)

@step
async def selecione(page, xpath, opcao):
    await page.waitForXPath(xpath)
    await page.type(cssify(xpath), opcao)
    await wait_page(page)


@step
async def salva_pagina(page):
    content = await page.content()
    body = str.encode(content)
    return body

@step
async def extrai_texto(page, xpath):
    await page.waitForXPath(xpath)
    text = await page.Jeval(cssify(xpath), "el => el.textContent")
    return text

@step
async def opcoes(page, xpath, exceto=None):
    if exceto is None:
        exceto = []
    options = []
    await page.waitForXPath(xpath)
    for option in (await page.xpath(xpath + "/option")):
        value = await option.getProperty("text")
        options.append(value.toString().split(":")[-1])
    return [value for value in options if value not in exceto]


@step
async def for_clicavel(page, xpath):
    try:
        await clique(page, xpath)
        return True
    except:
        return False


@step
async def localiza_elementos(page, xpath, num=None):
    base_xpath = xpath.split("[*]")[0]

    xpath_list = []
    for i in range(len(await page.xpath(base_xpath))):
        candidate_xpath = xpath.replace("*", str(i+1))
        if await element_in_page(page, candidate_xpath):
            xpath_list.append(candidate_xpath)

    num = len(xpath_list) if not num else num
    return xpath_list[:num]


@step
async def retorna_pagina(page):
    await page.goBack()


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


@step
async def digite(page, xpath, texto):
    await page.type(cssify(xpath), texto)

@step
async def object(page, param):
    return param

@step
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


@step
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


@step
async def element_in_page(page, xpath):
    """This step returns True if there's any element given a xpath, otherwise, returns False

        :param page : a pyppeteer page
        :returns bool: True or False
    """
    return bool(await page.xpath(xpath))

async def open_in_new_tab(page, link_xpath):
    await page.waitForXPath(link_xpath)
    elements = await page.xpath(link_xpath)
    new_page_promisse = asyncio.get_event_loop().create_future()
    if len(elements) == 1:
        page.browser.once("targetcreated", lambda target: new_page_promisse.set_result(target))
        await page.evaluate('el => el.setAttribute("target", "_blank")', elements[0])
        await elements[0].click()
        await page.bringToFront()
    else:
        raise Exception('XPath points to non existent element, or multiple elements!')

    new_page = await (await new_page_promisse).page()
    await wait_page(new_page)
    await new_page.bringToFront()

    return new_page
