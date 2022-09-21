from __future__ import annotations 

from django.db import models

from main.models import (TimeStamped, CrawlerQueue, CrawlRequest)


class CrawlerQueueItem(TimeStamped):
    NO_WAIT_POSITION = -99999999

    queue = models.ForeignKey(CrawlerQueue, on_delete=models.CASCADE, default=1, related_name='items')
    queue_type = models.CharField(max_length=8, default="medium")
    crawl_request = models.ForeignKey(CrawlRequest, on_delete=models.CASCADE, unique=True, related_name='queue_items')
    forced_execution = models.BooleanField(default=False)
    running = models.BooleanField(default=False, blank=True)
    position = models.IntegerField(null=False, default=0)