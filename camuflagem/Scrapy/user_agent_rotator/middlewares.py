import random
from itertools import cycle

from scrapy import signals
from scrapy.exceptions import NotConfigured

class RotateUserAgentMiddleware(object):
    def __init__(self, user_agents, min_item_count, max_item_count, choose_randomly):
        self.items_scraped = 0
        self.user_agents = user_agents

        self.min_item_count = min_item_count
        self.max_item_count = max_item_count

        self.item_count = random.randint(self.min_item_count, self.max_item_count)
        self.user_agent = str(random.choice(self.user_agents))

        self.choose_randomly = choose_randomly

        if not self.choose_randomly:
            self.user_agents = cycle(self.user_agents)

    @classmethod
    def from_crawler(cls, crawler):
        if not crawler.settings.getbool('ROTATE_USER_AGENT_ENABLED', False):
            raise NotConfigured()

        user_agents = crawler.settings.get('USER_AGENTS', None)

        min_item_count = crawler.settings.getint('MIN_USER_AGENT_USAGE', None)
        max_item_count = crawler.settings.getint('MAX_USER_AGENT_USAGE', None)

        choose_randomly = crawler.settings.getbool('CHOOSE_USER_AGENT_RANDOMLY', False)

        if user_agents is None or min_item_count is None or max_item_count is None:
            raise NotConfigured()

        obj = cls(user_agents, min_item_count, max_item_count, choose_randomly)

        return obj

    def process_request(self, request, spider):
        self.items_scraped += 1

        if self.items_scraped >= self.item_count:
            self.items_scraped = 0
            self.item_count = random.randint(self.min_item_count, self.max_item_count)

            if self.choose_randomly:
                self.user_agent = str(random.choice(self.user_agents))
            else:
                self.user_agent = next(self.user_agents)

        request.headers['user-agent'] = self.user_agent
