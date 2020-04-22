# -*- coding: utf-8 -*-
"""
Rúbia Reis Guerra
rubia-rg@github
Extract form fields from URL and returns dict {'field_name': 'value', ...}
"""
import urllib.parse


class URLParser:
    def __init__(self, url):
        self.url = url

    def query(self):
        return urllib.parse.urlsplit(self.url).query

    def parameters(self, query=None, keep_blank_values=True):
        if query is None:
            query = self.get_query()
        return urllib.parse.parse_qs(query, keep_blank_values=keep_blank_values)
