import asyncio
import sys
from twisted.internet import asyncioreactor
from scrapy.cmdline import execute


def __main__():
    execute(argv=sys.argv)
