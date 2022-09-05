
from django.db import models
from django.db.models.base import ModelBase

CRAWLER_QUEUE_DB_ID = 1

class CrawlerQueue(models.Model):
    max_fast_runtime_crawlers_running = models.PositiveIntegerField(default=1, blank=True)
    max_medium_runtime_crawlers_running = models.PositiveIntegerField(default=1, blank=True)
    max_slow_runtime_crawlers_running = models.PositiveIntegerField(default=1, blank=True)

    @classmethod
    def object(cls: ModelBase):
        if cls._default_manager.all().count() == 0:
            crawler_queue = CrawlerQueue.objects.create(id=CRAWLER_QUEUE_DB_ID)
            crawler_queue.save()

        return CrawlerQueue.objects.get(id=CRAWLER_QUEUE_DB_ID)

    @classmethod
    def to_dict(cls: ModelBase) -> dict:
        crawler_queue = CrawlerQueue.object()

        queue_items = list()
        for queue_item in crawler_queue.items.all():
            queue_items.append({
                'id': queue_item.id,
                'creation_date': round(queue_item.creation_date.timestamp() * 1000),
                'last_modified': round(queue_item.last_modified.timestamp() * 1000),
                'crawler_id': queue_item.crawl_request.id,
                'crawler_name': queue_item.crawl_request.source_name,
                'queue_type': queue_item.queue_type,
                'position': queue_item.position,
                'forced_execution': queue_item.forced_execution,
                'running': queue_item.running
            })

        data = {
            'max_fast_runtime_crawlers_running': crawler_queue.max_fast_runtime_crawlers_running,
            'max_medium_runtime_crawlers_running': crawler_queue.max_medium_runtime_crawlers_running,
            'max_slow_runtime_crawlers_running': crawler_queue.max_slow_runtime_crawlers_running,
            'items': queue_items
        }

        return data

    def num_crawlers_running(self, queue_type: str) -> int:
        return self.items.filter(queue_type=queue_type, running=True).count()

    def num_crawlers(self) -> int:
        return self.items.all().count()

    def __get_next(self, queue_type: str, max_crawlers_running: int, source_queue: str = None):
        next_crawlers = list()

        # um coletor irá executar na fila que não seria a sua. Como no caso onde
        # a fila de coletores lentos em execução está vazia e ele pode alocar para executar
        # coletores médios e curtos
        if source_queue:
            num_crawlers_running = self.num_crawlers_running(source_queue)

        else:
            num_crawlers_running = self.num_crawlers_running(queue_type)

        if num_crawlers_running >= max_crawlers_running:
            return next_crawlers

        candidates = self.items.filter(queue_type=queue_type, running=False).order_by('position').values()
        limit = max(0, max_crawlers_running - num_crawlers_running)

        return [(e['id'], e['crawl_request_id']) for e in candidates[:limit]]

    def get_next(self, queue_type: str):
        next_crawlers = list()
        has_items_from_another_queue = False

        if queue_type == 'fast':
            next_crawlers = self.__get_next('fast', self.max_fast_runtime_crawlers_running)

        elif queue_type == 'medium':
            next_crawlers = self.__get_next('medium', self.max_medium_runtime_crawlers_running)

            # We fill the vacant spot in the queue of slow crawlers with the fastest ones
            if len(next_crawlers) < self.max_medium_runtime_crawlers_running:
                fast_next_crawlers = self.__get_next(
                    'fast', self.max_medium_runtime_crawlers_running - len(next_crawlers), 'medium')
                next_crawlers.extend(fast_next_crawlers)
                has_items_from_another_queue = True

        elif queue_type == 'slow':
            next_crawlers = self.__get_next('slow', self.max_slow_runtime_crawlers_running)

            # We fill the vacant spot in the queue of slow crawlers with the fastest ones
            if len(next_crawlers) < self.max_slow_runtime_crawlers_running:
                medium_next_crawlers = self.__get_next(
                    'medium', self.max_slow_runtime_crawlers_running - len(next_crawlers), 'slow')
                next_crawlers.extend(medium_next_crawlers)
                has_items_from_another_queue = True

            # We fill the vacant spot in the queue of slow crawlers with the fastest ones
            if len(next_crawlers) < self.max_slow_runtime_crawlers_running:
                fast_next_crawlers = self.__get_next(
                    'fast', self.max_slow_runtime_crawlers_running - len(next_crawlers), 'slow')
                next_crawlers.extend(fast_next_crawlers)
                has_items_from_another_queue = True

        else:
            raise ValueError('Queue type must be fast, medium or slow.')

        return has_items_from_another_queue, next_crawlers


    def save(self, *args, **kwargs):
        self.pk = self.id = 1
        return super().save(*args, **kwargs)