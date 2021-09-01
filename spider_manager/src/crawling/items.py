# -*- coding: utf-8 -*-

# Define here the models for your scraped items

from scrapy import Item, Field


class RawResponseItem(Item):
    # default
    appid = Field()
    crawlid = Field()
    
    url = Field()
    response_url = Field()
    status_code = Field()
    body = Field()
    success = Field()
    exception = Field()
    encoding = Field()
    referer = Field()
    content_type = Field()
    crawler_id = Field()
    instance_id = Field()
    crawled_at_date = Field()
    files_found = Field()
    images_found = Field()
