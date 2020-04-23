# -*- coding: utf-8 -*-
"""
Rúbia Reis Guerra
rubia-rg@github
Extract HTML forms for parsing
"""
import requests

from lxml import etree
from form_parser import config


class HTMLExtractor:
    def __init__(self, url):
        self.url = url
        self.html_response = self.get_response(url)

    @staticmethod
    def get_response(url):
        return requests.get(url, headers=config.request_headers())

    def html_text(self):
        return self.html_response.text

    def html_content(self):
        return self.html_response.content

    def get_etree(self):
        try:
            return etree.HTML(self.html_text())
        except ValueError:
            return etree.HTML(self.html_content())

    def get_forms(self):
        html_tree = self.get_etree()
        return html_tree.xpath("//form")
