from django.apps import AppConfig
from django.db.utils import OperationalError
from step_crawler import parameter_extractor
from step_crawler import functions_file
import json


class MainConfig(AppConfig):
    name = 'main'
    server_running = False

    def runOnce(self):
        steps_signature = parameter_extractor.get_module_functions_info(functions_file)
        with open('main/staticfiles/json/steps_signature.json', 'w+') as file:
            json.dump(steps_signature, file)

        if self.server_running:
            return
        self.server_running = True
        # have to import here, after everything is ready
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
