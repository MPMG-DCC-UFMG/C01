import json
import unittest

import psycopg2

from crawled_request_filter import CrawledRequestFilter
from crawled_request_filter.utils import hashfy
from crawled_request_filter import settings

class TestCrawlRequestFilter(unittest.TestCase):
    def setUp(self):
        '''Configure connection with PostgreSQL
        '''

        self.conn = psycopg2.connect(dbname=settings.CRAWL_HISTORIC_DB_NAME,
                                user=settings.POSTGRESQL_USER,
                                password=settings.POSTGRESQL_PASSWORD,
                                host=settings.POSTGRESQL_HOST,
                                port=settings.POSTGRESQL_PORT)

        self.conn.set_session(autocommit=True)
        self.cursor = self.conn.cursor()

    def _delete_crawl_historic_in_database(self, crawlid: str):
        '''Deletes a crawl historic in the database
        '''

        table_name = settings.CRAWL_HISTORIC_TABLE_NAME
        column_name = settings.CRAWL_HISTORIC_COLUMN_NAME

        sql_query = f'DELETE FROM {table_name} WHERE CRAWLID = \'{crawlid}\''
        self.cursor.execute(sql_query)

    def _insert_crawl_historic_in_database(self, crawlid: str, crawl_historic: dict):
        '''Insert a crawl historic in the database
        '''

        table_name = settings.CRAWL_HISTORIC_TABLE_NAME
        column_name = settings.CRAWL_HISTORIC_COLUMN_NAME

        value = json.dumps(crawl_historic)

        sql_query = f'INSERT INTO {table_name} (CRAWLID, {column_name}) VALUES (\'{crawlid}\', \'{value}\');'
        self.cursor.execute(sql_query)

    def test_crawl_never_made(self):
        '''Checks whether the ability to verify that a crawl has been made works correctly.
        '''

        crawl_req = {
            'url': 'https://www.some_url.com/content/1'
        } 

        crawlid = hashfy(crawl_req['url'])
        self._delete_crawl_historic_in_database(crawlid)

        crf = CrawledRequestFilter()
        self.assertTrue(crf.crawl_never_made(crawlid)) 

        self._insert_crawl_historic_in_database(crawlid, {})
        self.assertTrue(crf.crawl_never_made(crawlid) == False)

        self._delete_crawl_historic_in_database(crawlid)

    def test_filter(self):
        '''Checks whether the ability to determine whether a crawl should be filtered is working correctly.
        '''
        
        crawl_req = {
            'url': 'https://www.some_another_url.com/content/1'
        }

        crawlid = hashfy(crawl_req['url'])
        self._delete_crawl_historic_in_database(crawlid)

        crf = CrawledRequestFilter()
        self.assertTrue(crf.filter(crawl_req) == False) 

        self._insert_crawl_historic_in_database(crawlid, {})
        self.assertTrue(crf.filter(crawl_req))

        self._delete_crawl_historic_in_database(crawlid)