from scrapy.cmdline import execute
import sys
import asyncio
from twisted.internet import asyncioreactor

asyncioreactor.install(asyncio.get_event_loop())


def __main__():
    execute(argv=sys.argv)
