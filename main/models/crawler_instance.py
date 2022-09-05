import datetime

from django.db import models
from main.models import TimeStamped, CrawlRequest

class CrawlerInstance(TimeStamped):
    crawler = models.ForeignKey(CrawlRequest, on_delete=models.CASCADE,
                                related_name='instances')
    instance_id = models.BigIntegerField(primary_key=True)

    number_files_found = models.PositiveIntegerField(default=0, null=True, blank=True)
    number_files_success_download = models.PositiveIntegerField(default=0, null=True, blank=True)
    number_files_error_download = models.PositiveIntegerField(default=0, null=True, blank=True)

    number_pages_found = models.PositiveIntegerField(default=0, null=True, blank=True)
    number_pages_success_download = models.PositiveIntegerField(default=0, null=True, blank=True)
    number_pages_error_download = models.PositiveIntegerField(default=0, null=True, blank=True)
    number_pages_duplicated_download = models.PositiveIntegerField(default=0, null=True, blank=True)

    page_crawling_finished = models.BooleanField(default=False, null=True, blank=True)

    running = models.BooleanField()
    num_data_files = models.IntegerField(default=0)
    data_size_kbytes = models.BigIntegerField(default=0)

    @property
    def duration_seconds(self):
        if self.creation_date == None or self.last_modified == None:
            return 0

        start_timestamp = datetime.datetime.timestamp(self.creation_date)
        end_timestamp = datetime.datetime.timestamp(self.last_modified)

        return end_timestamp - start_timestamp

    @property
    def duration_readable(self):
        final_str = ''
        str_duration = str(datetime.timedelta(seconds=self.duration_seconds))
        if 'day' in str_duration:
            parts = str_duration.split(',')
            final_str += parts[0].replace('day', 'dia')
            parts = parts[1].split(':')
            hours = int(parts[0])
            if hours > 0:
                final_str += ' ' + str(hours) + 'h'
        else:
            parts = str_duration.split(':')
            hours = int(parts[0])
            minutes = int(parts[1])
            seconds = int(float(parts[2]))
            if hours > 0:
                final_str += str(hours) + 'h'
                if minutes > 0:
                    final_str += ' ' + str(minutes) + 'min'
            elif minutes > 0:
                final_str += str(minutes) + 'min'
                if seconds > 0:
                    final_str += ' ' + str(seconds) + 's'
            else:
                final_str += str(seconds) + 's'

        return final_str

    @property
    def data_size_readable(self):
        size = self.data_size_kbytes
        for unit in ['kb', 'mb', 'gb', 'tb']:
            if size < 1000.0:
                break
            size /= 1000.0
        return f"{size:.{2}f}{unit}"


    def download_files_finished(self):
        return self.number_files_success_download + self.number_files_error_download == self.number_files_found