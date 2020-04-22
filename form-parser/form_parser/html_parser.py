# -*- coding: utf-8 -*-
"""
Rúbia Reis Guerra
rubia-rg@github
Extract form parameters from HTML
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


class HTMLForm:
    def __init__(self, form):
        self.form = form

    def list_field_types(self):
        return self.fields().keys()

    def get_number_fields(self):
        return len(self.form.xpath("//input/@type"))

    def required_fields(self):
        return self.form.xpath("//input[@required]")

    def input_types(self):
        return self.form.xpath("//input/@type")

    def select_fields(self):
        return self.form.xpath("//select")

    def fields(self):
        inputs = {}
        for input_type in set(self.input_types()):
            inputs[input_type] = self.form.xpath("//input[@type='" + input_type + "']")
        return inputs

    @staticmethod
    def list_field_attributes(field):
        return dict(field.attrib)

    @staticmethod
    def get_parent_field(field):
        return field.getparent()
