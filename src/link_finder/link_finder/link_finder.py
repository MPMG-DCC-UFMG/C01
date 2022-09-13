from playwright.sync_api import sync_playwright
from playwright.sync_api._generated import Response as PlaywrightResponse

from scrapy.linkextractors import LinkExtractor
from scrapy.http import TextResponse as ScrapyResponse
from typing import List, Set

class LinkFinder:
    def __init__(self) -> None:
        self.urls_found = set()
        self.allowed_domains = list() 
        self.page_must_have_text = list()
        self.max_depth = 0

        self.browser = None
        self.page = None

    def __extract_urls(self, response: ScrapyResponse) -> Set[str]:
        link_extractor = LinkExtractor(
            allow_domains=self.allowed_domains,
        )
        return set(link.url for link in link_extractor.extract_links(response))

    def __playwright_response_to_scrapy_response(self, playwright_response: PlaywrightResponse) -> ScrapyResponse:
        return ScrapyResponse(url=playwright_response.url, 
                            status=playwright_response.status, 
                            encoding='utf-8', #TODO: pegar o encoding dinamicamente
                            headers=playwright_response.headers, 
                            body=playwright_response.body())

    def valid_page(self, page_body: str) -> bool:
        return True
        # TODO: Implementar lógica de validação de página
        for text in self.page_must_have_text:
            if text in page_body:
                return True 
        return False  

    def __get_urls(self, seed_url: str, curr_depth: int):
        if curr_depth > self.max_depth:
            return

        playwright_response = self.page.goto(seed_url)
        page_body = self.page.content()

        if not self.valid_page(page_body):
            return

        # self.urls_found.add(seed_url)
        scrapy_response = self.__playwright_response_to_scrapy_response(playwright_response)

        for url in self.__extract_urls(scrapy_response):
            try:
                self.urls_found.add(url)
                # self.__get_urls(url, curr_depth + 1)
            
            except:
                continue

    def get_urls(self, seed_url: str, max_depth: int = 1, allowed_domains: List[str] = [], 
                        page_must_have_text: List[str] = [''], browser_headless_mode: bool = True) -> Set[str]:
        with sync_playwright() as playwright:
            self.browser = playwright.chromium.launch(headless=browser_headless_mode)
            # self.page = self.browser.new_page()
            self.context = self.browser.new_context(user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36')
            self.page = self.context.new_page()

            allowed_domains = seed_url
            allowed_domains = allowed_domains.replace('https://', '')
            allowed_domains = allowed_domains.replace('http://', '')
            allowed_domains = allowed_domains.replace('www.', '')
            allowed_domains = allowed_domains.split('/')[0]

            self.urls_found = set()
            self.allowed_domains = [allowed_domains]
            self.page_must_have_text = page_must_have_text
            self.max_depth = max_depth

            self.__get_urls(seed_url, 1)
            
            self.context.close()
            self.browser.close()
            self.page.close()

        return self.urls_found
    
if __name__ == '__main__':
    lf = LinkFinder()
    links_found = lf.get_urls('https://www.uberlandia.mg.gov.br/', allowed_domains=['uberlandia.mg.gov.br'])
    print(links_found)