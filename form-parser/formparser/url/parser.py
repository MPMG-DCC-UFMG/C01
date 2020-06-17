# -*- coding: utf-8 -*-
"""
Rúbia Reis Guerra
rubia-rg@github
Extract form fields from URL and returns dict {'field_name': 'value', ...}
"""
import urllib.parse


class Parser:
    """Parse URL for form parameters"""
    def __init__(self, url: str):
        """Constructor for URLParser

        Args:
            url (str): target url.
        """
        self.url = url

    def query(self) -> str:
        """Extract query from url

        Returns:
            String containing the query.
            Example: 'example.com/index.html?param1=value1&param2=value2'
            Returns: 'param1=value1&param2=value2'
        """
        return urllib.parse.urlsplit(self.url).query

    def parameters(self, query=None, keep_blank_values=True) -> dict:
        """Extract parameters from query

        Args:
            query (:obj:`str`, optional): Query. If query is not provided,
                attempts to extract from self.url
            keep_blank_values (:obj:`bool`, optional): argument for
            urllib.parse.parse_qs().
                 Example: 'example.com/index.html?param1=&param2=value2'
                 If True: {'param1': '', 'param2': 'value2'}.
                 If False: {'param2': 'value2'}.
        Returns:
            Dictionary containing the parameters and values.
            Example: 'example.com/index.html?param1=value1&param2=value2'
            Returns: {'param1': 'value1', 'param2': 'value2'}
        """
        if query is None:
            query = self.query()
        return urllib.parse.parse_qs(query, keep_blank_values=keep_blank_values)
