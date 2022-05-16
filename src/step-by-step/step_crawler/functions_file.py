import io
import asyncio
import datetime
import time
import operator
import playwright
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


def step(display, executable_contexts=['page', 'tab', 'iframe']):
    def function(f):
        f.is_step = True
        f.display = display
        f.executable_contexts = executable_contexts
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
    await pagina.wait_for_selector("html")


async def fill_iframe_content(page):
    # based on: https://gist.github.com/jgontrum/5a9060e40c7fc04c2c3bae3f1a9b28ad

    iframes = await page.query_selector_all('iframe')
    for iframe in iframes:
        frame = await iframe.content_frame()

        # Checks if the element is really an iframe
        if not frame:
            continue

        # Extract the content inside the iframe
        content = await frame.evaluate('''
            () => {
                const el = document.querySelector("*");
                return el.innerHTML;
            }
        ''')

        # Inserts iframe content as base page content
        await page.evaluate('''
            ([iframe, content]) => {
                iframe.innerHTML = content;
            }
        ''', [iframe, content])


@step("Clicar")
async def clique(pagina, elemento):
    if type(elemento) == str:
        el_locator = pagina.locator(f'xpath={elemento}')

        try:
            await el_locator.wait_for()
        except playwright._impl._api_types.TimeoutError:
            raise Exception('No element was found with the supplied XPath!')
        except playwright._impl._api_types.Error:
            raise Exception('XPath points to multiple elements!')

        element = await el_locator.first.element_handle()

        await pagina.evaluate('element => { element.click(); }', element)
    else:
        await pagina.evaluate('element => { element.click(); }', elemento)
    await espere_pagina(pagina)


@step("Selecionar")
async def selecione(pagina, xpath, opcao):
    el_locator = pagina.locator(f'xpath={xpath}')
    await el_locator.wait_for()
    await el_locator.type(opcao)
    await espere_pagina(pagina)


@step("Salvar página")
async def salva_pagina(pagina):
    await fill_iframe_content(pagina)
    content = await pagina.content()
    body = str.encode(content)
    return body


@step("Extrair texto de")
async def extrai_texto(pagina, xpath):
    el_locator = pagina.locator(f'xpath={xpath}')
    await el_locator.wait_for()
    text = await el_locator.text_content()
    return text


@step("Opções")
async def opcoes(pagina, xpath, exceto=None):
    if exceto is None:
        exceto = []
    options = []


    el_locator = pagina.locator(f'xpath={xpath}')
    await el_locator.wait_for()

    for option in (await pagina.locator(f'xpath={xpath + "/option"}').element_handles()):
        value = await option.get_attribute("text")
        options.append(value.toString().split(":")[-1])
    return [value for value in options if value not in exceto]


@step("É clicável")
async def for_clicavel(pagina, xpath):
    try:
        await clique(pagina, xpath)
        return True
    except:
        return False


@step("Localizar elementos")
async def localiza_elementos(pagina, xpath, numero_xpaths=None):
    base_xpath = xpath.split("[*]")[0]

    xpath_list = []
    for i in range(await pagina.locator(f'xpath={base_xpath}').count()):
        candidate_xpath = xpath.replace("*", str(i + 1))
        if await elemento_existe_na_pagina(pagina, candidate_xpath):
            xpath_list.append(candidate_xpath)

    numero_xpaths = len(xpath_list) if not numero_xpaths else numero_xpaths
    return xpath_list[:numero_xpaths]


@step("Voltar", executable_contexts=['page', 'tab'])
async def retorna_pagina(pagina):
    await pagina.go_back()


@step("Digitar em")
async def digite(pagina, xpath, texto):
    el_locator = pagina.locator(f'xpath={xpath}')
    await el_locator.evaluate('el => el.value = ""')
    await el_locator.type(texto)


@step("Objeto")
async def objeto(pagina, objeto):
    return objeto


@step("Está escrito")
async def nesse_elemento_esta_escrito(pagina, xpath, texto):
    el_locator = pagina.locator(f'xpath={xpath}')

    if el_locator.count() > 0:
        element = el_locator.element_handle()
    else:
        return 0

    # element_text_content = await element.text_content()
    # element_text = await (element_text_content).jsonValue()
    element_text = await element.text_content()
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
    el_locator = pagina.locator(f'xpath={xpath_do_elemento_captcha}')
    await el_locator.wait_for()
    element = (await el_locator.element_handles())[0]

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
    """This step returns True if there's any visible element given a xpath, otherwise, returns False

        :param pagina : a pyppeteer page
        :param xpath : elements xpaths
        :returns bool: True or False
    """
    try:
        el_locator = pagina.locator(f'xpath={xpath}')
        await el_locator.wait_for('visible', timeout=300)
    except Exception as e:
        return False
    return True

@step("Comparação")
async def comparacao(pagina, arg1, comp, arg2):
    """This step returns the result of comp(arg1, arg2)

        :param arg1 : a python object
        :param comp : a stringfied version of a comparison operator
        :param arg1 : a python object
        :returns bool: True or False
    """
    op_dict = {"==" : operator.eq, "<=" : operator.le, ">=" : operator.ge,
               "<" : operator.lt, ">" : operator.gt, "!=" : operator.ne,}

    return op_dict[comp](arg1, arg2)

async def open_in_new_tab(pagina, link_xpath):
    el_locator = pagina.locator(f'xpath={link_xpath}')

    try:
        await el_locator.wait_for()
    except playwright._impl._api_types.TimeoutError:
        raise Exception('No element was found with the supplied XPath!')
    except playwright._impl._api_types.Error:
        raise Exception('XPath points to multiple elements!')

    element = await el_locator.first.element_handle()

    try:
        async with pagina.context.expect_page() as tab:
            await pagina.evaluate(
                'el => { el.setAttribute("target", "_blank"); el.click();}',
                element
            )

        new_page = await tab.value
        await espere_pagina(new_page)
        await new_page.bring_to_front()

        return new_page
    except playwright._impl._api_types.TimeoutError:
        # TODO we will have to change this section to warn the user without
        # crashing the collector when we merge master with this branch
        raise Exception('Process timed out when trying to open xpath "'\
            + link_xpath +'" in a new page!')
