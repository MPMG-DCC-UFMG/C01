import json
import asyncio
import sys

from playwright.async_api import async_playwright
from step_crawler import functions_file
from step_crawler import code_generator as code_g
sys.path.append("../../../")

async def main():
    async with async_playwright() as apw:
        browser = await apw.chromium.launch(headless=False)
        page = await browser.new_page()
        tests = [('https://eproc.trf2.jus.br/eproc/externo_controlador.php?acao=advogado_cadastrar', 'recipe.json'),
                ("https://google.com", "google.json")]
        for url, filename in tests:
            await page.goto(url)
            await page.wait_for_load_state("networkidle")
            with open(filename) as recipe_file:
                recipe = json.load(recipe_file)
            steps = code_g.generate_code(recipe, functions_file)
            pages = await steps.execute_steps(page=page)

        await browser.close()
        return

asyncio.get_event_loop().run_until_complete(main())