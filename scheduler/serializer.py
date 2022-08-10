from rest_framework import serializers

from .models import Task

class TaskSerializer(serializers.ModelSerializer):
    crawler_name = serializers.ReadOnlyField(source='crawl_request.source_name')

    class Meta:
        model = Task
        read_only_fields = ['id', 'creation_date', 'last_modified']

        fields = ['id', 'creation_date', 'last_modified', 'crawl_request', 'runtime','crawler_name', 
                'crawler_queue_behavior', 'repeat_mode', 'personalized_repetition_mode']
