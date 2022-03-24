from rest_framework import serializers

from .models import CrawlRequest, CrawlerInstance, CrawlerQueue, CrawlerQueueItem


class CrawlerInstanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CrawlerInstance
        fields = '__all__'


class CrawlRequestSerializer(serializers.ModelSerializer):
    instances = CrawlerInstanceSerializer(many=True, read_only=True)
    running = serializers.ReadOnlyField()

    class Meta:
        model = CrawlRequest
        read_only_fields = ["id", "creation_date", "last_modified", "running"]
        fields = '__all__'

class CrawlerQueueItemSerializer(serializers.ModelSerializer):
    # crawl_request = CrawlRequestSerializer(many=False, read_only=True)

    class Meta:
        model = CrawlerQueueItem
        read_only_fields = ["id", "creation_date", "last_modified", "queue", "running"]
        fields = ["id", "creation_date", "last_modified", "crawl_request", "position", "running"]

class CrawlerQueueSerializer(serializers.ModelSerializer):
    pass 