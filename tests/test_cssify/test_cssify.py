#!/usr/bin/env python

from test_data import SUPPORTED, UNSUPPORTED
import os
import sys
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parentdir)
import cssify
from cssify.cssify import XpathException
import unittest

class CssifyTest(unittest.TestCase):
    def test_supported(self):
        for path, cssified in SUPPORTED:
            self.assertEqual(cssify.cssify(path), cssified)

    def test_unsupported(self):
        for path in UNSUPPORTED:
            self.assertRaises(XpathException, cssify.cssify, (path))
