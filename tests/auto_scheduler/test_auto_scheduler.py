import unittest
import ujson
import redis

from datetime import datetime, timedelta

from auto_scheduler import AutoScheduler
from auto_scheduler import settings


class TestAutoScheduler(unittest.TestCase):
    def test_update_crawl_frequency(self):
        '''Verifica se é capaz de gerar estimativas dado um histórico passado corretamente.
        '''

        now = datetime.now()

        crawl_historic = list()

        # valor arbitrário
        time_interval = 50
        for _ in range(settings.NUMBER_VISITS_TO_GENERATE_ESTIMATE):
            crawl_historic.append({
                'timestamp': now.timestamp(),
                'crawl_hash': 'content that doesn\'t change'
            })

            # valores arbitrários, poderia ser qualquer outro intervalo de tempo e valor
            now += timedelta(minutes=time_interval)

        estimated_time = AutoScheduler.update_crawl_frequency(
            'some_url_hash', crawl_historic)
        time_interval_in_secs = time_interval * 60

        # como o hash das coletas não mudam, o tempo estimado de quando elas mudam deve ser maior que o currentemente a visita
        self.assertTrue(estimated_time > time_interval_in_secs)

        crawl_historic = list()

        # valor arbitrário
        time_interval = 3
        for idx in range(settings.NUMBER_VISITS_TO_GENERATE_ESTIMATE):
            crawl_historic.append({
                'timestamp': now.timestamp(),
                'crawl_hash': f'content that always changes: {idx}'
            })

            # valores arbitrários, poderia ser qualquer outro intervalo de tempo e valor
            now += timedelta(hours=time_interval)

        estimated_time = AutoScheduler.update_crawl_frequency(
            'some_url_hash', crawl_historic)
        time_interval_in_secs = time_interval * 3600

        # como todas visitas há mudanças, então o correto é que se estime que a frequência de visitas
        # deve ser igual ou menor que o correntemente usado
        self.assertTrue(estimated_time <= time_interval_in_secs)

    def test_send_update(self):
        '''Verifica se é possível enviar a atualização de agendamento
        '''

        redis_conn = redis.Redis(host=settings.REDIS_HOST,
                                 port=settings.REDIS_PORT,
                                 db=settings.REDIS_DB,
                                 password=settings.REDIS_PASSWORD,
                                 decode_responses=True,
                                 socket_timeout=settings.REDIS_SOCKET_TIMEOUT,
                                 socket_connect_timeout=settings.REDIS_SOCKET_TIMEOUT)

        crawlid = 'some_unique_crawlid'
        schedule_update = {'interval': 'some_interval', 'every': 1}

        key = f'scheduling_updates::{crawlid}'
        redis_conn.delete(key)

        AutoScheduler.send_schedule_update(crawlid, schedule_update)

        val = ujson.dumps(schedule_update)

        # verifica se a atualização de agendamento foi inserida no Redis
        self.assertTrue(val == redis_conn.get(key))
