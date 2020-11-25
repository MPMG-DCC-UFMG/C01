import math
import sys
from datetime import datetime

import numpy as np
import psycopg2
import ujson

from crawl_prioritizer import settings
from crawl_prioritizer.utils import get_url_domain, hashfy

class CrawlPrioritizer:
    def __init__(self):
        self.priority_equation = settings.PRIORITY_EQUATION
        self.domain_priority = settings.DOMAIN_PRIORITY
        
        # Connection to PostgreSQL, configured in self.setup()
        self.conn = None 
        
        # Cursor that executes SQL queries in PostgreSQL, configured in self.setup()
        self.cursor = None

        self.setup()

    def setup(self):
        '''Makes the necessary settings for the class.
        '''

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

    def get_crawl_statistics(self, crawlid: str) -> tuple:
        ''' Retrieves statistics from a crawl. Specifically the timestamp of the last crawl made and the estimated frequency of change, if available.

        Args:
            crawlid: Unique crawl identifier (MD5 hash of your URL)
        
        Returns:
            Tuple with the timestamp of the last crawl made and the frequency of changes estimated.

        '''
        
        curr_timestamp = datetime.now().timestamp()

        time_since_last_crawl = None
        change_frequency = None

        # See https://github.com/MPMG-DCC-UFMG/C04/issues/238 for more details about the schema
        sql_query = 'SELECT CRAWL_HISTORIC FROM CRAWL_HISTORIC WHERE CRAWLID = %s;'
        data = (crawlid,)

        self.cursor.execute(sql_query, data)

        query_results = self.cursor.fetchall()
        if not len(query_results):
            return time_since_last_crawl, change_frequency

        # Data format based on: https://github.com/MPMG-DCC-UFMG/C04/issues/238
        crawl_historic = query_results[0][0]

        last_visit_timestamp = crawl_historic['last_visit_timestamp']
        change_frequency = crawl_historic['estimated_frequency_changes']

        # The number of visits made at the source was not sufficient to generate an estimate of the frequency of changes,
        # then the frequency of changes considered in change_frequency will be the period of visits that is being made at the source.
        if not change_frequency:
            visits = crawl_historic['visits']['0']
            crawl_timestamps = [visit['timestamp'] for visit in visits]

            # The current timestamp is considered because a visit to the crawl source is now being requested.
            crawl_timestamps.append(curr_timestamp)

            # Calculates the frequency of visits made at the source.
            visits_frequency = np.mean(np.diff(crawl_timestamps))
            change_frequency = visits_frequency
        
        time_since_last_crawl = curr_timestamp - last_visit_timestamp

        return time_since_last_crawl, change_frequency
    
    def get_expanded_priority_equation(self, domain_prio: float, time_since_last_crawl: float, change_frequency: float) -> str:
        ''' Put the values of variables domain_prio, time_since_last_crawl and change_frequency in the priority equation.

        Args:
           domain_prio: The priority of the crawl domain to be performed.
           time_since_last_crawl: Time in seconds since last visit.
           change_frequency: Estimated frequency of changes.
        
        Returns:
            Returns the crawl priority calculation equation with the parameter values entered in it.

        '''
        
        expr = self.priority_equation
    
        expr = expr.replace('domain_prio', f'{domain_prio}')
        expr = expr.replace('time_since_last_crawl', f'{time_since_last_crawl}')
        expr = expr.replace('change_frequency', f'{change_frequency}')

        return expr

    def calculate_priority(self, crawl_req: dict) -> float:
        ''' Calculates the priority of a crawl request.

        Args:
            crawl_req: Crawl request in Scrapy Cluster format.

        Returns:
            Returns the crawl priority.

        '''
        
        crawlid = hashfy(crawl_req['url'])
        crawl_domain = get_url_domain(crawl_req['url'])

        domain_prio = self.domain_priority.get(crawl_domain, 1)
        time_since_last_crawl, change_frequency = self.get_crawl_statistics(crawlid)

        if time_since_last_crawl is None:
            return settings.PRIORITY_NEVER_MADE_CRAWL 

        expr = self.get_expanded_priority_equation(domain_prio, time_since_last_crawl, change_frequency)        
        
        variables_in_exec_scope = dict()
        exec(expr, globals(), variables_in_exec_scope)

        crawl_priority = variables_in_exec_scope.get('crawl_priority')
        
        if crawl_priority > settings.MAX_PRIORITY:
            crawl_priority = settings.MAX_PRIORITY
        
        elif crawl_priority < settings.MIN_PRIORITY:
            crawl_priority = settings.MIN_PRIORITY
        
        return crawl_priority