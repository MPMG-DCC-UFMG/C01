from rest_framework import serializers

from .models import CrawlRequest, CrawlerInstance, CrawlerQueue, CrawlerQueueItem, Task


class CrawlerInstanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CrawlerInstance
        fields = '__all__'


class CrawlRequestSerializer(serializers.ModelSerializer):
    instances = CrawlerInstanceSerializer(many=True, read_only=True)
    running = serializers.ReadOnlyField()
    waiting_on_queue = serializers.ReadOnlyField()

    class Meta:
        model = CrawlRequest
        read_only_fields = ["id", "creation_date", "last_modified", "running", "waiting_on_queue"]
        fields = '__all__'


class TimestampField(serializers.Field):
    def to_representation(self, value):
        return round(value.timestamp() * 1000)


class CrawlerQueueItemSerializer(serializers.ModelSerializer):
    # crawl_request = CrawlRequestSerializer(many=False, read_only=True)
    crawler_id = serializers.ReadOnlyField(source='crawl_request.pk')
    crawler_name = serializers.ReadOnlyField(source='crawl_request.source_name')
    queue_type = serializers.ReadOnlyField(source='crawl_request.expected_runtime_category')
    creation_date = TimestampField()
    last_modified = TimestampField()

    class Meta:
        model = CrawlerQueueItem
        read_only_fields = ["id", "creation_date", "last_modified", "queue", "running"]
        fields = ["id", "creation_date", "last_modified", "crawler_id",
            "crawler_name", "queue_type", "position", "forced_execution", "running"]


class CrawlerQueueSerializer(serializers.ModelSerializer):
    items = CrawlerQueueItemSerializer(many=True, read_only=True)

    class Meta:
        model = CrawlerQueue

        fields = '__all__'


class TaskSerializer(serializers.ModelSerializer):
    crawler_name = serializers.ReadOnlyField(source='crawl_request.source_name')
    next_run = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Task
        read_only_fields = ['id', 'creation_date', 'last_modified']

        fields = ['id', 'creation_date', 'last_modified', 'crawl_request', 
                  'crawler_name', 'crawler_queue_behavior', 'last_run', 
                  'scheduler_config', 'next_run']
