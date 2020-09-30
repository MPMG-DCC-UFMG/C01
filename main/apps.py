from django.apps import AppConfig
from django.db.utils import OperationalError

from crawlers.crawler_manager import start_consumers_and_producers


class MainConfig(AppConfig):
    name = 'main'
    server_running = False

    def runOnce(self):
        if self.server_running:
            return
        self.server_running = True

        # Setting all cralwers that were running when server was shut down
        # as not running
        # have to import here, after everything is ready
        from .models import CrawlerInstance
        instances = CrawlerInstance.objects.filter(running=True)

        for instance in instances:
            instance.running = False
            instance.save()

        # starts file descriptor and file downloader processes
        start_consumers_and_producers()

    def ready(self):
        try:
            self.runOnce()
        except OperationalError as err:
            print(
                f"Error at MainConfig.ready(). Message:\n{err}\n"
                f"Are you making migrations or migrating?\n" 
                f" If so, ignore this error. Otherwise you should fix it."
            )
