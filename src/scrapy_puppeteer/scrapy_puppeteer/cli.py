import asyncio
from twisted.internet import asyncioreactor

asyncioreactor.install(asyncio.get_event_loop())
import sys
from scrapy.cmdline import execute


def __main__():
    execute(argv=sys.argv)
