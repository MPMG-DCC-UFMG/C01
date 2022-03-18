import io
import asyncio
import datetime
import time
import operator
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
    await pagina.waitForSelector("html")


async def fill_iframe_content(page):
    # based on: https://gist.github.com/jgontrum/5a9060e40c7fc04c2c3bae3f1a9b28ad

    iframes = await page.querySelectorAll('iframe')
    for iframe in iframes:
        frame = await iframe.contentFrame()

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
            (iframe, content) => {
                iframe.innerHTML = content;
            }
        ''', iframe, content)


@step("Clicar")
async def clique(pagina, elemento):
    if type(elemento) == str:
        await pagina.waitForXPath(elemento)
        elements = await pagina.xpath(elemento)
        if len(elements) == 1:
            await pagina.evaluate('element => { element.click(); }', elements[0])
        else:
            raise Exception('XPath points to non existent element, or multiple elements!')
    else:
        await pagina.evaluate('element => { element.click(); }', elemento)
    await espere_pagina(pagina)


@step("Selecionar")
async def selecione(pagina, xpath, opcao):
    await pagina.waitForXPath(xpath)
    await pagina.type(cssify(xpath), opcao)
    await espere_pagina(pagina)


@step("Salvar página")
async def salva_pagina(pagina):
    await fill_iframe_content(pagina)
    content = await pagina.content()
    body = str.encode(content)
    return body


@step("Extrair texto de")
async def extrai_texto(pagina, xpath):
    await pagina.waitForXPath(xpath)
    elements = await pagina.xpath(xpath)
    if len(elements) == 1:
        text = await pagina.evaluate("el => el.textContent", elements[0])
    else:
        raise Exception('XPath points to non existent element, or multiple elements!')
    return text

@step("Extrair propriedade de")
async def extrai_propriedade(pagina, xpath, propriedade):
    await pagina.waitForXPath(xpath)
    elements = await pagina.xpath(xpath)
    if len(elements) == 1:
        text = await pagina.evaluate("el => el.getAttribute(\"" + propriedade + "\")", elements[0])
    else:
        raise Exception('XPath points to non existent element, or multiple elements!')
    
    return text


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


@step("Localizar elementos")
async def localiza_elementos(pagina, xpath, numero_xpaths=None, modo='simples'):
    xpath_list = []

    if modo == 'complexo':
        elements = await pagina.xpath(xpath)
        for el in elements:
            text = await pagina.evaluate("""el => { 
                var getXpathOfNode = (domNode, bits) => {
                    bits = bits ? bits : [];
                    var c = 0;
                    var b = domNode.nodeName;
                    var p = domNode.parentNode;

                    if (p) {
                        var els = p.getElementsByTagName(b);
                        if (els.length >  1) {
                        while (els[c] !== domNode) c++;
                        b += "[" + (c+1) + "]";
                        }
                        bits.push(b);
                        return getXpathOfNode(p, bits);
                    }
                    return bits.reverse().join("/");
                }; 
                return getXpathOfNode(el);
            }""", el)

            xpath_list.append(text.lower())
        
    elif modo == 'simples':
        base_xpath = xpath.split("[*]")[0]

        for i in range(len(await pagina.xpath(base_xpath))):
            candidate_xpath = xpath.replace("*", str(i + 1))
            if await elemento_existe_na_pagina(pagina, candidate_xpath):
                xpath_list.append(candidate_xpath)

    numero_xpaths = len(xpath_list) if not numero_xpaths else numero_xpaths

    return xpath_list[:numero_xpaths]


@step("Voltar", executable_contexts=['page', 'tab'])
async def retorna_pagina(pagina):
    await pagina.goBack()


@step("Digitar em")
async def digite(pagina, xpath, texto):
    await pagina.querySelectorEval(cssify(xpath), 'el => el.value = ""')
    await pagina.click(cssify(xpath))
    time.sleep(1)
    await pagina.type(cssify(xpath), texto)


@step("Objeto")
async def objeto(pagina, objeto):
    return objeto


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
    """This step returns True if there's any visible element given a xpath, otherwise, returns False

        :param pagina : a pyppeteer page
        :param xpath : elements xpaths
        :returns bool: True or False
    """
    try:
        await pagina.waitForXPath(xpath, visible=True, timeout=300)
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
    await pagina.waitForXPath(link_xpath)
    elements = await pagina.xpath(link_xpath)

    if len(elements) != 1:
        raise Exception('XPath points to non existent element, or multiple elements!')

    new_page_promisse = asyncio.get_event_loop().create_future()
    pagina.browser.once("targetcreated", lambda target: new_page_promisse.set_result(target))
    await pagina.evaluate('el => { el.setAttribute("target", "_blank"); el.click();}', elements[0])
    try:
        new_page = await (await asyncio.wait_for(new_page_promisse, 60)).page()
        await espere_pagina(new_page)
        await new_page.bringToFront()

        return new_page
    except asyncio.TimeoutError:
        raise Exception('Process timed out when trying to open xpath "' + link_xpath +'" in a new page!')
