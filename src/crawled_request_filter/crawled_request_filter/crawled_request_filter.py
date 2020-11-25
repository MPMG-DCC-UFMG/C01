import psycopg2

from crawled_request_filter import settings
from crawled_request_filter.utils import hashfy

class CrawledRequestFilter:
    def __init__(self):
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

    def crawl_never_made(self, crawlid: str) -> bool:
        '''Checks if a crawl has never been made.

        Args:
            crawlid: Unique crawl identifier.
        
        Returns:
            Returns True if the crawl was never done, False, otherwise.

        '''
        
        # See https://github.com/MPMG-DCC-UFMG/C04/issues/238 for more details about the schema
        sql_query = 'SELECT CRAWL_HISTORIC FROM CRAWL_HISTORIC WHERE CRAWLID = %s;'
        data = (crawlid,)

        self.cursor.execute(sql_query, data)

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
