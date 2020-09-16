# -*- coding: utf-8 -*-
"""
Rúbia Reis Guerra
rubia-rg@github
Parse form parameters from HTML
"""
from collections import defaultdict
from formparser.html.extractor import HTMLExtractor
from formparser.html.dynamic_fields import DynamicFields


class HTMLParser:
    """Parse HTML forms"""

    def __init__(self, url=None, form=None):
        """Constructor for HTMLForm

        Args:
            form (`lxml.etree._Element`): target form.
        """
        if form is not None:
            self.form = form
        elif url is not None:
            self.url = url
            self.form = self.fetch_form(url)
        # TODO: throw exception when form == None and url == None

    @staticmethod
    def fetch_form(url, form_index=-1):
        """Gets form from url

        Args:
            url `str`: target url
            form_index `int`: position of the form in the webpage,
            set to -1 since most pages the first form corresponds to
            a search box

        Returns:
            form `lxml.etree._Element`
        """
        html = HTMLExtractor(url)
        return html.get_forms()[form_index]

    def number_of_fields(self) -> int:
        """Returns the number of fields in the form"""
        return len(self.form.xpath("//input | //select"))

    def fields(self) -> dict:
        """Returns form fields as dictionary

        Returns:
            {'type1': [field1, field2], 'type2': field3}
            Example: {'text': [name, phone], 'radio': year}
        """
        inputs = {}
        field_types = self.unique_field_types()
        for input_type in field_types:
            if input_type == 'select':
                inputs[input_type] = self.form.xpath("//select")
            else:
                inputs[input_type] = self.form.xpath("//input[@type='" +
                                                     input_type + "']")
        return inputs

    def unique_field_types(self) -> set:
        """Returns a set of types of fields in the form"""
        return set(self.list_input_types())

    def list_input_types(self) -> list:
        """Returns input types as [`lxml.etree._ElementUnicodeResult`]"""
        input_types_list = []
        for field_type in self.form.xpath("//input/@type | //select"):
            if not isinstance(field_type, str):
                input_types_list.append('select')
            else:
                input_types_list.append(field_type)
        return input_types_list

    def list_fields(self) -> list:
        """Returns form fields as list

        Returns:
            [field1, field2, ...]
            Example: [name, phone, year, ...]
        """
        return self.form.xpath("//input | //select")

    def list_field_labels(self) -> list:
        """Returns list of form fields' labels

        Returns:
            List of field labels
        """
        return [label.text for label in self.form.xpath("//label")]

    def required_fields(self) -> list:
        """Returns required fields as [`lxml.etree._Element`]"""
        return self.form.xpath("//input[@required]")

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

    def submit_button(self) -> list:
        """Returns submit button"""
        return self.form.xpath("//input[@type='submit']")

    def dynamic_fields(self, form_url=None, dynamic_types=None) -> dict:
        """Returns dict of dynamic form fields. The keys show the
        field that generated change, while the values are the fields that
        changed after an action.

        Args:
            form_url: url of webpage where the form is (if not provided when
                          constructing the object HTMLParser)
            dynamic_types: list of field types to be checked.
                           Default field types are 'select'
                           and 'radio'
        Returns:
            {'field1_xpath': [field2_xpath, field3_xpath]}
        """
        if dynamic_types is None:
            dynamic_types = ['select', 'radio', 'checkbox']
        if self.url is not None:
            df = DynamicFields(self.url, self.form)
        else:
            df = DynamicFields(form_url, self.form)
        checked_fields = defaultdict(list)
        for dynamic_type in dynamic_types:
            try:
                checked_fields[dynamic_type] = self.fields()[dynamic_type]
            except KeyError:
                continue
        df.get_dynamic_fields(checked_fields)
        return df.dynamic_fields

    @staticmethod
    def field_attributes(field) -> dict:
        """Returns field attributes as dictionary

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
