import json
import logging
import os
import time
import scrapy

from scrapy.crawler import CrawlerProcess

JTR_IDENTIFIER = 402
TRF2_URL = "http://portal.trf2.jus.br/portal/consulta/cons_procs.asp"

FIRST_YEAR = 1989
LAST_YEAR = 2019

ORIGINS = [0, 9999]
MAX_SEQ = 9999999

FOLDER_PATH = "coleta"

# Functions to generate the process codes

def verif_code(num_proc):
    """
    Calculates the verificaton code for a given process number

    :param num_proc: the process number for which to generate the code
    :returns: the verif number for the supplied code
    """
    num_proc = int(num_proc)
    val = 98 - ((num_proc * 100) % 97)

    return val


def build_from_data(year, origin, sequence):
    """
    Generates a process code from its parameters

    :param year: year of the related process
    :param origin: identifier for the originating unit for this process
    :param sequence: sequential identifier for the process
    :returns: the corresponding process with its verifying digits
    """

    p_fmt = "{:07d}{:04d}{:03d}{:04d}"
    ver_code = verif_code(p_fmt.format(sequence, year, JTR_IDENTIFIER, origin))

    res_fmt = "{:07d}{:02d}{:04d}{:03d}{:04d}"
    return res_fmt.format(sequence, ver_code, year, JTR_IDENTIFIER, origin)


def generate_codes(first_year, last_year, origins, max_seq):
    """
    Generates all the codes to be downloaded

    :returns: a generator instance which iterates over all possible codes
    """
    for year in range(first_year, last_year + 1):
        for origin in origins:
            for n in range(0, max_seq + 1):
                yield build_from_data(year, origin, n)

class Trf2_2Crawler(scrapy.Spider):
    name = "trf2_2"
    
    def __init__(self):
        logging.getLogger('scrapy').setLevel(logging.WARNING)

        if not os.path.exists(FOLDER_PATH):
            os.makedirs(FOLDER_PATH)


    def start_requests(self):
        req_body = "Botao=Pesquisar&UsarCaptcha=S&gabarito=4&resposta=4&Localidade=0&baixado=0&CodLoc=&NumProc={}++&TipDocPess=0&captchacode=4"

        count = 0
        for code in generate_codes(FIRST_YEAR, LAST_YEAR, ORIGINS, MAX_SEQ):
            count += 1
            req = scrapy.Request(TRF2_URL, method='POST',
                body=req_body.format(code),
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                callback=self.parse_entry)
            req.meta['count'] = count
            yield req

    def parse_entry(self, response):
        count = response.meta['count']

        page_cont = response.text

        urls = response.css('iframe::attr(src)').extract()
        framecount = 0
        for url in urls:
            framecount += 1
            full_url = response.urljoin(url)
            file_name = str(count) + "-" + str(framecount) + ".html"
            page_cont = page_cont.replace(url, file_name)
            req = scrapy.Request(full_url, callback=self.parse_iframe)
            req.meta['file_name'] = file_name
            yield req

        if len(urls) > 0:
            with open(os.path.join(FOLDER_PATH, str(count) + ".html"), 'w') as html_file:
                html_file.write(page_cont)


    def parse_iframe(self, response):
        proc_code = response.css("#Procs option::text").get()
        with open(os.path.join(FOLDER_PATH, response.meta['file_name']), 'w') as html_file:
            html_file.write(response.text)

        yield {'code': proc_code}


def main():
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/5.0 (X11; Linux x86_64; rv:74.0) Gecko/20100101 Firefox/74.0'
    })

    process.crawl(Trf2_2Crawler)
    process.start()

if __name__ == "__main__":
    main()
