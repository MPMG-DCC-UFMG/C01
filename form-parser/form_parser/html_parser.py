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

    def option_fields(self):
        return self.form.xpath("//select/option")

    def select_with_option_fields(self):
        options = self.option_fields()
        select_fields = defaultdict(list)
        for option in options:
            select_fields[self.get_parent_field(option)].append(option)
        return select_fields

    def void_options(self):
        return self.form.xpath("//select/option[normalize-space(.)='']")

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
