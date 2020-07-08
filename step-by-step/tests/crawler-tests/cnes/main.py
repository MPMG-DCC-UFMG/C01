import json

from step_crawler import code_generator as code_g
from step_crawler import atomizer as atom
from step_crawler.functions_file import *
from step_crawler import functions_file

from pyppeteer import launch


async def main():
    browser = await launch(headless=False)
    page = await browser.newPage()
    await page.goto('http://cnes.datasus.gov.br/pages/estabelecimentos/'
                    'consulta.jsp')

    steps = __import__('steps')
    await steps.execute_steps(page = page)

    await browser.close()
    return


with open('recipe.json') as file:
    recipe = json.load(file)

with open('steps.py', 'w+') as file:
    # code = code_g.generate_code(recipe, functions_file)
    code = code_g.generate_code(atom.extend(recipe)[0], functions_file)
    print(code)
    file.write(code)

asyncio.get_event_loop().run_until_complete(main())







