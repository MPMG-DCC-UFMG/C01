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
    options = {
                "headless": False,
                'args': ["--start-maximized", '--no-sandbox'],
                'dumpio':True,
              }
    browser = await launch(options)

    page = await browser.newPage()
    await page.goto('https://eproc.trf2.jus.br/eproc/externo_controlador.php?acao=advogado_cadastrar')

    steps = code_g.generate_code(recipe, functions_file)
    pages = await steps.execute_steps(page=page)
    # await page.waitForNavigation()
    await browser.close()
    return

with open('recipe.json') as file:
    recipe = json.load(file)

asyncio.get_event_loop().run_until_complete(main())