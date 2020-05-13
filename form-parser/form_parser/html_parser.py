# -*- coding: utf-8 -*-
"""
Rúbia Reis Guerra
rubia-rg@github
Parse form parameters from HTML
"""
from collections import defaultdict


class HTMLForm:
    def __init__(self, form):
        self.form = form

    def list_field_types(self) -> list:
        return list(self.fields().keys())

    def get_number_fields(self) -> int:
        return len(self.form.xpath("//input/@type"))

    def required_fields(self) -> list:
        return self.form.xpath("//input[@required]")

    def input_types(self) -> list:
        return self.form.xpath("//input/@type")

    def select_fields(self) -> list:
        return self.form.xpath("//select")

    def option_fields(self) -> list:
        return self.form.xpath("//select/option")

    def select_with_option_fields(self) -> defaultdict:
        options = self.option_fields()
        select_fields = defaultdict(list)
        for option in options:
            select_fields[self.get_parent_field(option)].append(option)
        return select_fields

    def void_options(self) -> list:
        return self.form.xpath("//select/option[normalize-space(.)='']")

    def fields(self) -> dict:
        inputs = {}
        for input_type in set(self.input_types()):
            inputs[input_type] = self.form.xpath("//input[@type='" + input_type + "']")
        return inputs

    @staticmethod
    def list_field_attributes(field) -> dict:
        """
        :param field: 'lxml.etree._Element'
        :return: dict
        """
        return dict(field.attrib)

    @staticmethod
    def get_parent_field(field):
        """
        :param field: 'lxml.etree._Element'
        :return: 'lxml.etree._Element'
        """
        return field.getparent()
