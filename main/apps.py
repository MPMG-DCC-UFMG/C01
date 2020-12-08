from crawlers.crawler_manager import log_writer_process
from django.apps import AppConfig
from django.db.utils import OperationalError
from multiprocessing import Process
from step_crawler import functions_file
from step_crawler import parameter_extractor

import atexit
import json
import signal

# Enable interrupt signal
signal.signal(signal.SIGINT, signal.SIG_DFL)


class MainConfig(AppConfig):
    name = 'main'
    server_running = False

    def runOnce(self):
        steps_signature = parameter_extractor.get_module_functions_info(
            functions_file)
        with open('main/staticfiles/json/steps_signature.json', 'w+') as file:
            json.dump(steps_signature, file)

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

        # starts kafka log consumer
        log_writer = Process(target=log_writer_process)
        log_writer.start()
        atexit.register(log_writer.join)

        # cleaning download queue and current download
        from .models import DownloadDetail
        DownloadDetail.objects.all().delete()

    def ready(self):
        try:
            self.runOnce()
        except OperationalError as err:
            print(
                f"Error at MainConfig.ready(). Message:\n{err}\n"
                f"Are you making migrations or migrating?\n"
                f" If so, ignore this error. Otherwise you should fix it."
            )
