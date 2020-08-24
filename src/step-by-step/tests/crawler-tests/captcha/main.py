from pyppeteer import launch
import asyncio
from PIL import Image
from captcha_solver.image_solver import ImageSolver
from cssify import cssify

import io

import json

async def main():
    browser = await launch({"headless": True,
                            'args': ['--start-fullscreen', '--no-sandbox', '--start-maximized'],
                            'dumpio':True})
    page = await browser.newPage()
    await page.goto('https://www.google.com')

    text = await break_captcha(page, '/html/body/div/div[4]/span/center/div[1]/img',
                               '/html/body/div/div[2]/form/div[2]/div[1]/div[1]/div/div[2]/input')
    print(text)

    screenshot do elemento e gera uma imagem
    xpath = '/html/body/div/div[4]/span/center/div[1]/img'
    element = (await page.xpath(xpath))[0]
    image_data = await element.screenshot(path="image.jpg")

    # mostra a imagem que representa o print do elemento
    image = Image.open(io.BytesIO(image_data))
    image.show()

    # reconhece os caracteres
    solver = ImageSolver(preprocessing=lambda x: x)
    text = solver.solve(image=image)

    # digita texto de captcha no campo de input
    xpath_input = '/html/body/div/div[2]/form/div[2]/div[1]/div[1]/div/div[2]/input'
    await page.type(cssify(xpath_input), text)

    await page.waitForNavigation()
    await browser.close()
    return



async def break_captcha(page, xpath_input, xpath_output):
    element = (await page.xpath(xpath_input))[0]
    image_data = await element.screenshot(path="image.jpg")
    image = Image.open(io.BytesIO(image_data))
    solver = ImageSolver(preprocessing=lambda x: x)
    text = solver.solve(image=image)
    # preenche o campo de texto com o resultado
    await page.type(cssify(xpath_output), text)
    return text

asyncio.get_event_loop().run_until_complete(main())


