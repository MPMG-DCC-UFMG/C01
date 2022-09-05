from django.db import models

from main.models import TimeStamped, CrawlerInstance

class Log(TimeStamped):
    instance = models.ForeignKey(CrawlerInstance, on_delete=models.CASCADE,
                                 related_name="log")
    log_message = models.TextField(blank=True, null=True)
    logger_name = models.CharField(max_length=50, blank=True, null=True)
    log_level = models.CharField(max_length=10, blank=True, null=True)
    raw_log = models.TextField(blank=True, null=True)