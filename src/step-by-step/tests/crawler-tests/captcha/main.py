from pyppeteer import launch
import asyncio
from PIL import Image
from captcha_solver.image_solver import ImageSolver
from cssify import cssify
from pyext import RuntimeModule
from step_crawler import atomizer as atom
from step_crawler.functions_file import *
from step_crawler import functions_file
from step_crawler import code_generator as code_g
import io
import json
import sys
sys.path.append("../../../")


async def main():
    browser = await launch({"headless": False,
                            'args': ['--start-maximized', '--no-sandbox'],
                            'dumpio':True})
    page = await browser.newPage()
    await page.goto('https://www.google.com')

    steps = code_g.generate_code(recipe, functions_file)
    pages = await steps.execute_steps(page=page)

    await page.waitForNavigation()
    await browser.close()
    return

with open('recipe.json') as file:
    recipe = json.load(file)

asyncio.get_event_loop().run_until_complete(main())



    # text = await functions_file.break_captcha(page, '/html/body/div/div[4]/span/center/div[1]/img',
    #                            '/html/body/div/div[2]/form/div[2]/div[1]/div[1]/div/div[2]/input')
    # print(text)

    # # screenshot do elemento e gera uma imagem
    # xpath = '/html/body/div/div[4]/span/center/div[1]/img'
    # element = (await page.xpath(xpath))[0]
    # image_data = await element.screenshot(path="image.jpg")

    # # mostra a imagem que representa o print do elemento
    # image = Image.open(io.BytesIO(image_data))
    # image.show()

    # # reconhece os caracteres
    # solver = ImageSolver(preprocessing=lambda x: x)
    # text = solver.solve(image=image)

    # # digita texto de captcha no campo de input
    # xpath_input = '/html/body/div/div[2]/form/div[2]/div[1]/div[1]/div/div[2]/input'
    # await page.type(cssify(xpath_input), text)

    # await page.goto('http://cnes.datasus.gov.br/pages/estabelecimentos/consulta.jsp')
