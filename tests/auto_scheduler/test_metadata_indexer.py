import hashlib
import json
import os
import unittest
from datetime import datetime

from auto_scheduler import MetadataIndexer
from auto_scheduler import hashfy
from auto_scheduler import settings

class TestMetadataIndexer(unittest.TestCase):
    def test_persist(self):
        crawl = {
            'url': 'https://www.some_url.com/content/1',
            'body': '''<!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Document</title>
                </head>
                <body>
                    <p>Some content</p>
                </body>
                </html>''',
            'timestamp': str(datetime.now()),
        }

        crawlid = hashfy(crawl['url'])
        historic_filename = settings.HISTORIC_FOLDER + crawlid
        
        if os.path.exists(historic_filename):
            os.remove(historic_filename)

        MetadataIndexer.persist(crawl)

        self.assertTrue(os.path.exists(historic_filename))
