from django.contrib import admin
from .models import CrawlRequest, CrawlerInstance

# Register your models here.
admin.site.register(CrawlRequest)
admin.site.register(CrawlerInstance)