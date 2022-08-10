from rest_framework import serializers

from .models import Task

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        read_only_fields = ['id', 'creation_date', 'last_modified']

        fields = ['id', 'creation_date', 'last_modified', 'crawl_request', 'runtime', 
                'crawler_queue_behavior', 'repetion_mode', 'personalized_repetition_mode']
