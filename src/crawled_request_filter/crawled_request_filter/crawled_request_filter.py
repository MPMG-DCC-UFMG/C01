import psycopg2

from crawled_request_filter import settings
from crawled_request_filter.utils import hashfy

class CrawledRequestFilter:
    def __init__(self):
        self.conn = psycopg2.connect(dbname=settings.CRAWL_HISTORIC_DB_NAME,
                            user=settings.POSTGRESQL_USER,
                            password=settings.POSTGRESQL_PASSWORD,
                            host=settings.POSTGRESQL_HOST,
                            port=settings.POSTGRESQL_PORT)

        self.conn.set_session(autocommit=True)
        self.cursor = self.conn.cursor()

    def crawl_never_made(self, crawlid: str) -> bool:
        '''Checks if a crawl has never been made.

        Args:
            crawlid: Unique crawl identifier.
        
        Returns:
            Returns True if the crawl was never done, False, otherwise.

        '''
        
        sql_query = f'SELECT {settings.CRAWL_HISTORIC_COLUMN_NAME} FROM {settings.CRAWL_HISTORIC_TABLE_NAME} WHERE CRAWLID = \'{crawlid}\';'
        self.cursor.execute(sql_query)

        return self.cursor.fetchone() is None

    def filter(self, crawl_req: dict) -> bool:
        '''Checks whether a crawl should be filtered, that is, not occur.

        Args:
            crawl_req: Crawl request in the Scrapy Cluster standard.

        Returns:
            Returns True if the crawl is to be filtered, False, in another case.
            
        '''
        
        url = crawl_req['url']
        crawlid = hashfy(url)

        return not self.crawl_never_made(crawlid)
