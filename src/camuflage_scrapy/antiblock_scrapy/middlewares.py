import random
from itertools import cycle
from typing import List

from scrapy import signals
from scrapy.crawler import Crawler
from scrapy.exceptions import NotConfigured
from scrapy.http import Request
from scrapy.spiders import Spider

from toripchanger import TorIpChanger

class TorProxyMiddleware(object):
    '''This middleware enables Tor to serve as connection proxies'''

    def __init__(self, crawler: Crawler, max_count: int, allow_reuse_ip_after: int):
        '''Creates a new instance of TorProxyMiddleware
        
        Keywords arguments:
            max_count -- Maximum IP usage
            allow_reuse_ip_after -- When an IP can be reused
        '''

        self.crawler = crawler
        self.max_count = max_count

        self.tor_ip_changer = TorIpChanger(reuse_threshold=allow_reuse_ip_after)
        self.tor_ip_changer.get_new_ip()

        self.items_scraped = 0

    @classmethod
    def from_crawler(cls, crawler: Crawler):
        if not crawler.settings.getbool('TOR_IPROTATOR_ENABLED', False):
            raise NotConfigured()

        max_count = crawler.settings.getint('TOR_IPROTATOR_CHANGE_AFTER', 1000)
        allow_reuse_ip_after = crawler.settings.getint('TOR_IPROTATOR_ALLOW_REUSE_IP_AFTER', 10)

        mw = cls(crawler=crawler, max_count=max_count, allow_reuse_ip_after=allow_reuse_ip_after)

        return mw

    def process_request(self, request: Request, spider: Spider) -> None:
        if self.items_scraped >= self.max_count:
            spider.log('Changing Tor IP...')
            self.items_scraped = 0
            
            self.crawler.engine.pause()
            new_ip = self.tor_ip_changer.get_new_ip()
            self.crawler.engine.unpause()
            
            if not new_ip:
                raise Exception('FatalError: Failed to find a new IP')
            
            spider.log(f'New Tor IP: {new_ip}')

        # http://127.0.0.1:8118 is the default address for Privoxy
        request.meta['proxy'] = 'http://127.0.0.1:8118'
        self.items_scraped += 1

class RotateUserAgentMiddleware(object):
    '''This middleware enables user-agent rotation'''

    def __init__(self, user_agents: List, min_usage: int, max_usage: int):
        '''Creates a new instance of RotateUserAgentMiddleware 
        
        Keyword arguments:
            user_agents -- List of user-agents
            min_usage -- Minimum user-agent usage
            max_usage -- Maximum user-agent usage
        '''

        self.items_scraped = 0

        self.min_usage = min_usage
        self.max_usage = max_usage

        self.limit_usage = random.randint(self.min_usage, self.max_usage)

        self.user_agents = cycle(user_agents)
        self.user_agent = next(self.user_agents)

    @classmethod
    def from_crawler(cls, crawler: Crawler):
        if not crawler.settings.getbool('ROTATE_USER_AGENT_ENABLED', False):
            raise NotConfigured()

        user_agents = crawler.settings.get('USER_AGENTS', None)

        min_usage = crawler.settings.getint('MIN_USER_AGENT_USAGE', 1)
        max_usage = crawler.settings.getint('MAX_USER_AGENT_USAGE', 100)

        if user_agents is None or min_usage < 1 or max_usage < 1:
            raise NotConfigured()

        return cls(user_agents, min_usage, max_usage)

    def process_request(self, request: Request, spider: Spider):
        if self.items_scraped >= self.limit_usage:
            self.items_scraped = 0
            self.limit_usage = random.randint(self.min_usage, self.max_usage)

            self.user_agent = next(self.user_agents)

        request.headers['user-agent'] = self.user_agent
        self.items_scraped += 1