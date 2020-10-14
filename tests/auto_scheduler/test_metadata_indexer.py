import unittest
from datetime import datetime

import psycopg2

from auto_scheduler import MetadataIndexer
from auto_scheduler import hashfy
from auto_scheduler import settings

class TestMetadataIndexer(unittest.TestCase):
    def test_persist(self):

        crawl = {
            'url': 'https://www.some_url.com/content/11',
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
            'timestamp': datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f'),
        }

        crawlid = hashfy(crawl['url'])
        MetadataIndexer.persist(crawl)

        conn = psycopg2.connect(dbname=settings.CRAWL_HISTORIC_DB_NAME, user=settings.POSTGRESQL_USER, password=settings.POSTGRESQL_PASSWORD, host=settings.POSTGRESQL_HOST, port=settings.POSTGRESQL_PORT)
        conn.set_session(autocommit=True)

        cur = conn.cursor()
        sql_query = f'SELECT CRAWL_HISTORIC FROM {settings.CRAWL_HISTORIC_TABLE_NAME} WHERE CRAWLID = \'{crawlid}\';'
        cur.execute(sql_query)

        results = cur.fetchall()

        cur.close()
        conn.close()
        
        self.assertTrue(results is not None)
