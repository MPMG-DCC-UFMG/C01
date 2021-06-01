from django.apps import AppConfig
from django.db.utils import OperationalError
from step_crawler import parameter_extractor
from step_crawler import functions_file

import json
import os
import signal
import sys

# Enable interrupt signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

class MainConfig(AppConfig):
    name = 'main'
    server_running = False

    def runOnce(self):
        # Create json folder if necessary
        if not os.path.exists('main/staticfiles/json/'):
            os.makedirs('main/staticfiles/json/')

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
        if not ('makemigrations' in sys.argv or 'migrate' in sys.argv):
            from .models import CrawlerInstance
            instances = CrawlerInstance.objects.filter(running=True)

            for instance in instances:
                instance.running = False
                instance.save()

    def ready(self):
        try:
            self.runOnce()
        except OperationalError as err:
            print(
                f"Error at MainConfig.ready(). Message:\n{err}\n"
                f"Are you making migrations or migrating?\n"
                f" If so, ignore this error. Otherwise you should fix it."
            )
