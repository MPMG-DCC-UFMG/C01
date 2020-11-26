import json
import unittest

import psycopg2
from psycopg2.extensions import cursor

from crawled_request_filter import CrawledRequestFilter
from crawled_request_filter.utils import hashfy
from crawled_request_filter import settings


class TestCrawlRequestFilter(unittest.TestCase):
    def setUp(self):
        '''Configure connection with PostgreSQL
        '''

        # The database created in other module, in:
        # https://github.com/MPMG-DCC-UFMG/C04/blob/master/src/auto_scheduler/auto_scheduler/database_handler.py 
        # but to run the tests independently, they are also created here, if necessary.
        self._create_db_if_not_exists()

        self.conn = psycopg2.connect(
            # Name of the database that saved the crawl metadata,
            # see https://github.com/MPMG-DCC-UFMG/C04/issues/238 for more details
            dbname='auto_scheduler',
            user=settings.POSTGRESQL_USER,
            password=settings.POSTGRESQL_PASSWORD,
            host=settings.POSTGRESQL_HOST,
            port=settings.POSTGRESQL_PORT)

        self.conn.set_session(autocommit=True)
        self.cursor = self.conn.cursor()
        
        # For the same reason as creating the database above,
        # the table is created here, if necessary.
        self._create_table_if_not_exists()
    
    def _db_exists(self, cur: cursor) -> bool:
        '''Checks if a database already exists.

        Args:
            cur: Cursor for SQL queries.
            db_name: Database name.

        Returns:
            True, if the database exists, False otherwise.

        '''

        sql_query = 'SELECT datname FROM pg_catalog.pg_database WHERE datname = \'auto_scheduler\';'
        cur.execute(sql_query)

        return cur.fetchone() is not None

    def _create_db_if_not_exists(self):
        '''Creates the database, if it does not exist, since PostgreSQL does not have "CREATE DATABASE IF NOT EXISTS"
        '''

        conn = psycopg2.connect(user=settings.POSTGRESQL_USER, password=settings.POSTGRESQL_PASSWORD,
                                host=settings.POSTGRESQL_HOST, port=settings.POSTGRESQL_PORT)
        conn.set_session(autocommit=True)

        cur = conn.cursor()

        if not self._db_exists(cur):
            sql_query = 'CREATE DATABASE auto_scheduler;'
            cur.execute(sql_query)

        cur.close()
        conn.close()

    def _create_table_if_not_exists(self):
        '''Creates the table to save the crawl history, if it does not exist.
        '''

        sql_query = 'CREATE TABLE IF NOT EXISTS CRAWL_HISTORIC' \
                    '(CRAWLID CHAR(32) PRIMARY KEY NOT NULL, ' \
                    'CRAWL_HISTORIC JSONB);'

        self.cursor.execute(sql_query)
    
    def _delete_crawl_historic_in_database(self, crawlid: str):
        '''Deletes a crawl historic in the database
        '''
        # See https://github.com/MPMG-DCC-UFMG/C04/issues/238 for more details about the schema
        sql_query = 'DELETE FROM CRAWL_HISTORIC WHERE CRAWLID = %s'
        data = (crawlid, )

        self.cursor.execute(sql_query, data)

    def _insert_crawl_historic_in_database(self, crawlid: str, crawl_historic: dict):
        '''Insert a crawl historic in the database
        '''
        value = json.dumps(crawl_historic)

        # See https://github.com/MPMG-DCC-UFMG/C04/issues/238 for more details about the schema
        sql_query = 'INSERT INTO CRAWL_HISTORIC (CRAWLID, CRAWL_HISTORIC) VALUES (%s, %s);'
        data = (crawlid, value)

        self.cursor.execute(sql_query, data)

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