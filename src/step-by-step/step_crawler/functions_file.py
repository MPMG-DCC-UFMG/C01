import io
import asyncio
import time
import uuid
from cssify import cssify
from PIL import Image
from captcha_solver.image_solver import ImageSolver
from pyext import RuntimeModule


def wait(segs):
    time.sleep(segs)


def generates_file_name():
    return "./{}.html".format(uuid.uuid4().hex)


async def wait_page(page):
    jsWait = "document.readyState === 'complete' || \
              document.readyState === 'iteractive'"
    while not (await page.evaluate(jsWait)):
        await page.waitFor(1)


async def click(page, xpath):
    await page.waitForXPath(xpath)
    await page.click(cssify(xpath))
    await wait_page(page)


async def select_this_in(page, option, xpath):
    await page.waitForXPath(xpath)
    await page.type(cssify(xpath), option)
    await wait_page(page)


async def save_page(page):
    content = await page.content()
    body = str.encode(content)
    return body


async def options_in(page, xpath, except_=None):
    if except_ is None:
        except_ = []
    options = []
    await page.waitForXPath(xpath)
    for option in (await page.xpath(xpath + "/option")):
        value = await option.getProperty("text")
        options.append(value.toString().split(":")[-1])
    return [value for value in options if value not in except_]


async def is_clickable(page, xpath):
    try:
        await clique(page, xpath)
        return True
    except:
        return False


async def get_pagination_links(page, buttons_xpath, links_xpath, next_button_index=-1):
    clickable = True
    urls = []
    while clickable:
        urls += [await(await link.getProperty('href')).jsonValue() for link in await page.xpath(links_xpath)]

        buttons = await page.xpath(buttons_xpath)
        if len(buttons) != 0:
            next_button = buttons[next_button_index]
            before_click = await page.content()
            await next_button.click()
            after_click = await page.content()
            if before_click == after_click:
                clickable = False
        else:
            clickable = False


async def send_keys(page, xpath, text):
    await page.type(cssify(xpath), text)


async def is_writed_in(page, text, xpath):
    elements = await page.xpath(xpath)
    if len(elements):
        element = elements[0]
    else:
        return 0

    element_text_content = await element.getProperty('textContent')
    element_text = await(element_text_content).jsonValue()
    if text in element_text:
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
