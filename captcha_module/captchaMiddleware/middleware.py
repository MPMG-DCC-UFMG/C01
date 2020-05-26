import logging
import time

import requests
from scrapy import signals
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.common.keys import Keys
from lxml import html

from sel.image_solver import ImageSolver
from sel.audio_solver import AudioSolver

class CaptchaMiddleware(object):

    def process_response(self, request, response, spider):
        if not request.meta.get("captcha_type", False):
            return response
            
        if isinstance(request, SeleniumRequest):
            if request.meta["captcha_type"] == "image":
                solver = ImageSolver(request.url, webdriver=request.meta["driver"])
                source = request.meta["captcha_source"]
            else:
                captcha_url = response.xpath(request.meta["captcha_source"] + request.meta["capthca_source_att"]).get()
                source = requests.compat.urljoin(request.url, captcha_url)
                solver = AudioSolver(request.url, webdriver=request.meta["driver"], download_dir="./")

            time.sleep(2)
            text = solver.solve(source=source)
            captcha_form = request.meta["driver"].find_element_by_xpath(request.meta["captcha_form"])
            captcha_form.send_keys(text)
            captcha_form.send_keys(Keys.RETURN)
            request.meta["captcha_awnser"] = text

        else:
            if request.meta["captcha_type"] == "image":
                solver = ImageSolver(request.url)
            else:
                solver = AudioSolver(request.url)

            captcha_url = response.xpath(request.meta["captcha_source"] + request.meta["capthca_source_att"]).get()
            source = requests.compat.urljoin(request.url, captcha_url)
            text = solver.solve(source=source)
            request.meta["captcha_awnser"] = text

        return response