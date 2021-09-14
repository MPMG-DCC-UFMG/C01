import atexit
import os
import json
import signal
from multiprocessing import Process

from django.apps import AppConfig
from django.db.utils import OperationalError

from crawler_manager.crawler_manager import log_writer_process
from step_crawler import functions_file
from step_crawler import parameter_extractor
from crawler_manager.crawler_manager import run_spider_manager_listener

import json
import os
import signal
import sys

# Enable interrupt signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

class MainConfig(AppConfig):
    name = 'main'

    def runOnce(self):
        # Create json folder if necessary
        if not os.path.exists('main/staticfiles/json/'):
            os.makedirs('main/staticfiles/json/')

        steps_signature = parameter_extractor.get_module_functions_info(functions_file)
        with open('main/staticfiles/json/steps_signature.json', 'w+') as file:
            json.dump(steps_signature, file)

        # Setting all cralwers that were running when server was shut down
        # as not running
        # have to import here, after everything is ready
        if not ('makemigrations' in sys.argv or 'migrate' in sys.argv):
            from .models import CrawlerInstance
            instances = CrawlerInstance.objects.filter(running=True)

            for instance in instances:
                instance.running = False
                instance.save()

        # starts kafka log consumer
        log_writer = Process(target=log_writer_process)
        log_writer.start()
        atexit.register(log_writer.join)

        run_spider_manager_listener()
        
    def ready(self):
        try:
            self.runOnce()
        except OperationalError as err:
            print(
                f"Error at MainConfig.ready(). Message:\n{err}\n"
                f"Are you making migrations or migrating?\n"
                f" If so, ignore this error. Otherwise you should fix it."
            )
