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
    """Extract and parse HTML for forms"""
    def __init__(self, url):
        """Constructor for HTMLExtractor

        Args:
            url (str): target url.
        """
        self.url = url
        self.html_response = self.get_response(url)

    @staticmethod
    def get_response(url: str) -> requests.models.Response:
        """HTTP request GET method

        Args:
            url (str): target url.

        Returns:
            Request response.
        """
        return requests.get(url, headers=config.request_headers())

    def html_text(self) -> str:
        """Extracts HTML from request's response as string

        Returns:
            HTML as text.
        """
        return self.html_response.text

    def html_content(self) -> bytes:
        """Extracts HTML from request's response as bytes

        Args:
            HTML as bytes.
        """
        return self.html_response.content

    def get_etree(self) -> etree._Element:
        """Constrcturs lxml.etree from HTML

        Returns:
            lxml.etree from HTML
        """
        try:
            return etree.HTML(self.html_text())
        except ValueError:
            return etree.HTML(self.html_content())

    def get_forms(self) -> list:
        """Extracts forms from HTML

        Returns:
            List of forms -> [`lxml.etree._Element`]
        """
        html_tree = self.get_etree()
        return html_tree.xpath("//form")
