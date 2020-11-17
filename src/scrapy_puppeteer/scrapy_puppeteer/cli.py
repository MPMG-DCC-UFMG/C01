import asyncio
from twisted.internet import asyncioreactor

try:
    loop = asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

try:
    asyncioreactor.install(loop)
except Exception:
    pass
import sys
from scrapy.cmdline import execute


def __main__():
    execute(argv=sys.argv)
