# -*- coding: utf-8 -*-
"""
Rúbia Reis Guerra
rubia-rg@github
Parse form parameters from HTML
"""
from collections import defaultdict


class HTMLForm:
    """Parse HTML forms"""
    def __init__(self, form):
        """Constructor for HTMLForm

        Args:
            form (`lxml.etree._Element`): target form.
        """
        self.form = form

    def list_field_types(self) -> list:
        """Returns types of fields in the form"""
        return list(self.fields().keys())

    def get_number_fields(self) -> int:
        """Returns the number of fields in the form"""
        return len(self.form.xpath("//input/@type"))

    def required_fields(self) -> list:
        """Returns required fields as [`lxml.etree._Element`]"""
        return self.form.xpath("//input[@required]")

    def input_types(self) -> list:
        """Returns input types as [`lxml.etree._ElementUnicodeResult`]"""
        return self.form.xpath("//input/@type")

    def select_fields(self) -> list:
        """Returns select fields as [`lxml.etree._Element`]"""
        return self.form.xpath("//select")

    def option_fields(self) -> list:
        """Returns select fields' options  as [`lxml.etree._Element`]"""
        return self.form.xpath("//select/option")

    def select_with_option_fields(self) -> defaultdict:
        """Returns select fields and options as defaultdict"""
        options = self.option_fields()
        select_fields = defaultdict(list)
        for option in options:
            select_fields[self.get_parent_field(option)].append(option)
        return select_fields

    def void_options(self) -> list:
        """Returns select fields' void options as list"""
        return self.form.xpath("//select/option[normalize-space(.)='']")

    def fields(self) -> dict:
        """Returns form fields as dictionary

        Returns:
            {'type1': [field1, field2], 'type2': field3}
            Example: {'text': [name, phone], 'radio': year}
        """
        inputs = {}
        for input_type in set(self.input_types()):
            inputs[input_type] = self.form.xpath("//input[@type='" + input_type + "']")
        return inputs

    @staticmethod
    def list_field_attributes(field) -> dict:
        """Returns form attributes as dictionary

        Args:
            field: 'lxml.etree._Element'

        Returns:
            Dictionary of field attributes
        """
        return dict(field.attrib)

    @staticmethod
    def get_parent_field(field):
        """Returns parent field.
        Example: find an 'option' field parent select.

        Args:
            field: form field 'lxml.etree._Element'

        Returns:
            Parent 'lxml.etree._Element'
        """
        return field.getparent()
