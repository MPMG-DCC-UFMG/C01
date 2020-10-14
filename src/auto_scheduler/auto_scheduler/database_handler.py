import ujson
import psycopg2

from psycopg2 import OperationalError
from psycopg2.extensions import cursor

from auto_scheduler import settings


class DatabaseHandler:
    '''
    Serves as an interface for saving crawl metadata in PostgreSQL.
    '''

    def __init__(self):
        self.conn = None
        self.cur = None

        self.setup()

    def setup(self):
        '''Performs the basic settings of the class operation.
        '''

        self.create_db_if_not_exists()

        self.conn = psycopg2.connect(dbname=settings.CRAWL_HISTORIC_DB_NAME, user=settings.POSTGRESQL_USER,
                                     password=settings.POSTGRESQL_PASSWORD, host=settings.POSTGRESQL_HOST, port=settings.POSTGRESQL_PORT)
        self.conn.set_session(autocommit=True)

        self.cur = self.conn.cursor()
        self.create_table_if_not_exists()

    def db_exists(self, cur: cursor, db_name: str) -> bool:
        '''Checks if a database already exists.

        Args:
            cur: Cursor for SQL queries.
            db_name: Database name.

        Returns:
            True, if the database exists, False otherwise.

        '''

        sql_query = f'SELECT datname FROM pg_catalog.pg_database WHERE datname = \'{db_name}\';'
        cur.execute(sql_query)

        return cur.fetchone() is not None

    def create_db_if_not_exists(self):
        '''Creates the database, if it does not exist, since PostgreSQL does not have "CREATE DATABASE IF NOT EXISTS"
        '''

        db_name = settings.CRAWL_HISTORIC_DB_NAME

        conn = psycopg2.connect(user=settings.POSTGRESQL_USER, password=settings.POSTGRESQL_PASSWORD,
                                host=settings.POSTGRESQL_HOST, port=settings.POSTGRESQL_PORT)
        conn.set_session(autocommit=True)

        cur = conn.cursor()

        if not self.db_exists(cur, db_name):
            sql_query = f'CREATE DATABASE {db_name};'
            cur.execute(sql_query)

        cur.close()
        conn.close()

    def create_table_if_not_exists(self):
        '''Creates the table to save the crawl history, if it does not exist.
        '''

        table_name = settings.CRAWL_HISTORIC_TABLE_NAME

        sql_query = f'CREATE TABLE IF NOT EXISTS {table_name}' \
                    '(CRAWLID CHAR(32) PRIMARY KEY NOT NULL, ' \
                    'CRAWL_HISTORIC JSONB);'

        self.cur.execute(sql_query)

    def insert_crawl_historic(self, crawlid: str, crawl_historic: dict):
        '''Insert a new crawl history in the database.

        Args:
            crawlid: Unique crawl identifier.
            crawl_historic: Crawl history in json.
        '''

        table_name = settings.CRAWL_HISTORIC_TABLE_NAME
        value = ujson.dumps(crawl_historic)

        sql_query = f'INSERT INTO {table_name} (CRAWLID, CRAWL_HISTORIC) VALUES (\'{crawlid}\', \'{value}\');'
        self.cur.execute(sql_query)

    def update_crawl_historic(self, crawlid: str, crawl_historic: dict):
        '''Updates the crawl history.

        Args:
            crawlid: Unique crawl identifier.
            crawl_historic: Crawl history in json to be updated.
        '''

        table_name = settings.CRAWL_HISTORIC_TABLE_NAME
        value = ujson.dumps(crawl_historic)

        sql_query = f'UPDATE {table_name} SET CRAWL_HISTORIC = \'{value}\' WHERE CRAWLID = \'{crawlid}\';'
        self.cur.execute(sql_query)

    def get_crawl_historic(self, crawlid: str):
        '''Retrieves the crawl history.

        Args:
           crawlid: Unique identifier of the crawl to be retrieved. 

        '''

        table_name = settings.CRAWL_HISTORIC_TABLE_NAME

        sql_query = f'SELECT CRAWL_HISTORIC FROM {table_name} WHERE CRAWLID = \'{crawlid}\';'
        self.cur.execute(sql_query)

        query_results = self.cur.fetchall()
        if not len(query_results):
            return None

        # queries come by default as tuple lists
        return query_results[0][0]

    def close(self):
        '''Closes connections to PostgreSQL.
        '''

        self.cur.close()
        self.conn.close()
