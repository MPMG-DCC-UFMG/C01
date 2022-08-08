from rest_framework import serializers

from .models import SchedulerJob

class SchedulerJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchedulerJob
        read_only_fields = ['id', 'creation_date', 'last_modified']

        fields = ['id', 'creation_date', 'last_modified', 'crawl_request', 'runtime', 
                'crawler_queue_behavior', 'repetion_mode', 'personalized_repetition_mode']
