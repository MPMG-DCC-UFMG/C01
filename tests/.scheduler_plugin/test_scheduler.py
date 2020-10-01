import unittest
import random
import ujson
import time
import threading

from tests.m_scheduler import SchedulerPlugin
from datetime import datetime, timedelta

from kafka import KafkaConsumer

SETTINGS = {
    'REDIS_HOST': 'localhost',
    'REDIS_PORT': 6379,
    'REDIS_DB': 0,
    'REDIS_PASSWORD': None,
    'REDIS_SOCKET_TIMEOUT': 10,
    'KAFKA_HOSTS': ['localhost:9092'],
    'KAFKA_INCOMING_TOPIC': 'demo.incoming'
}


class TestScheduler(unittest.TestCase):
    def setUp(self):
        self.crawls_timestamp_received = None
        self.keep_running = True
        self.kafka_consumer = KafkaConsumer(
            SETTINGS['KAFKA_INCOMING_TOPIC'], bootstrap_servers=SETTINGS['KAFKA_HOSTS'])

    def test_weekday_shift(self):
        '''Verifica se o cálculo de intervalos entre dias está correto.
        '''

        scheduler = SchedulerPlugin()

        for from_weekday in range(7):
            for to_weekday in range(7):
                curr_weekday = from_weekday

                num_days = 0
                while curr_weekday != to_weekday:
                    curr_weekday += 1
                    if curr_weekday == 7:
                        curr_weekday = 0
                    num_days += 1

                self.assertTrue(num_days == scheduler.calculate_weekday_shift(
                    from_weekday, to_weekday))

    def test_hour_shift(self):
        '''Verifica se o cálculo de intervalo entre horas está correto.
        '''

        scheduler = SchedulerPlugin()

        for from_hour in range(24):
            for to_hour in range(24):
                curr_hour = from_hour

                num_hours = 0
                while curr_hour != to_hour:
                    curr_hour += 1
                    if curr_hour == 24:
                        curr_hour = 0
                    num_hours += 1

                self.assertTrue(
                    num_hours == scheduler.calculate_hour_shift(from_hour, to_hour))

    def test_get_next_crawl_by_time(self):
        '''Verifica se é possível agendar um horário específico para que uma coleta seja realizada ou comece.
        '''

        scheduler = SchedulerPlugin()

        # Tenta criar timestamp para uma coleta no passado
        with self.assertRaises(ValueError):
            now = datetime.now()
            conf = {'start_at': '2020-07-12 23:59'}
            next_crawl = scheduler.get_next_crawl_time(now, conf)
            self.assertTrue(next_crawl is None)

        # Tenta criar timestamp de uma coleta no futuro
        now_delta = now + timedelta(hours=2)
        crawl_at = now_delta.strftime("%Y-%m-%d %H:%M")
        conf = {'start_at': crawl_at}

        next_crawl = scheduler.get_next_crawl_time(now, conf)
        self.assertTrue(next_crawl is not None)

        # Tenta criar timestamp de coleta num horário inválido
        with self.assertRaises(ValueError):
            conf = {'start_at': '2020-07-12 23:90'}
            next_crawl = scheduler.get_next_crawl_time(now, conf)
            self.assertTrue(next_crawl is None)

        # Tenta criar um timestamp de coleta num formato inválido
        with self.assertRaises(ValueError):
            conf = {'start_at': '2020-07-12, 23:90'}
            next_crawl = scheduler.get_next_crawl_time(now, conf)
            self.assertTrue(next_crawl is None)

    def test_get_next_crawl_by_minutes(self):
        '''Verifica agendamentos por minutos.
        '''

        scheduler = SchedulerPlugin()

        now = datetime.now()
        curr_minute = now.minute

        for delta_minute in range(1, 61):
            crawl_minute = (curr_minute + delta_minute) % 60
            conf = {'repeat': {'every': delta_minute, 'interval': 'minutes'}}
            next_crawl = scheduler.get_next_crawl_time(now, conf)
            self.assertTrue(crawl_minute == next_crawl.minute)

    def test_get_next_crawl_by_hours(self):
        '''Verifica todos parâmetros para recoletas definidas em intervalos de horas.
        '''

        scheduler = SchedulerPlugin()
        max_hours = 25

        now = datetime.now()
        curr_hour = now.hour

        for from_hour in range(24):
            for to_hour in range(24):
                for at_minute in range(60):
                    for delta_hour in range(1, max_hours):
                        conf = {
                            'repeat': {
                                'every': delta_hour,
                                'interval': 'hours',
                                'at_minute': at_minute,
                                'from': from_hour,
                                'to': to_hour
                            }
                        }

                        crawl_hour = (curr_hour + delta_hour) % 24

                        if from_hour > to_hour:
                            if crawl_hour > to_hour and crawl_hour < from_hour:
                                crawl_hour = from_hour

                        elif crawl_hour < from_hour or crawl_hour > to_hour:
                            crawl_hour = from_hour

                        next_crawl = scheduler.get_next_crawl_time(now, conf)

                        self.assertTrue(next_crawl.hour == crawl_hour)
                        self.assertTrue(next_crawl.minute == at_minute)

        # testa período de recoleta inválido
        with self.assertRaises(ValueError):
            conf = {'repeat': {'every': 0, 'interval': 'minutes'}}
            new_crawl = scheduler.get_next_crawl_time(now, conf)

        # testa período inválido de recoleta
        with self.assertRaises(ValueError):
            conf = {'repeat': {'every': -1, 'interval': 'minutes'}}
            new_crawl = scheduler.get_next_crawl_time(now, conf)
            self.assertTrue(new_crawl is None)

    def test_get_next_crawl_by_days(self):
        '''Verifica todos parâmetros para agendamentos por dias.
        '''

        scheduler = SchedulerPlugin()
        max_days = 8

        now = datetime.now()
        curr_weekday = now.weekday()

        for from_weekday in range(7):
            for to_weekday in range(7):
                for at_hour in range(24):
                    for at_minute in range(60):
                        for delta_days in range(1, max_days):
                            conf = {
                                'repeat': {
                                    'every': delta_days,
                                    'interval': 'days',
                                    'at_hour': at_hour,
                                    'at_minute': at_minute,
                                    'from': from_weekday,
                                    'to': to_weekday
                                }
                            }

                            crawl_weekday = (curr_weekday + delta_days) % 7

                            if from_weekday > to_weekday:
                                if crawl_weekday > to_weekday and crawl_weekday < from_weekday:
                                    crawl_weekday = from_weekday

                            elif crawl_weekday < from_weekday or crawl_weekday > to_weekday:
                                crawl_weekday = from_weekday

                            next_crawl = scheduler.get_next_crawl_time(
                                now, conf)

                            self.assertTrue(
                                next_crawl.weekday() == crawl_weekday)
                            self.assertTrue(next_crawl.hour == at_hour)
                            self.assertTrue(next_crawl.minute == at_minute)

        # testa período de recoleta inválido
        with self.assertRaises(ValueError):
            conf = {'repeat': {'every': 0, 'interval': 'days'}}
            next_crawl = scheduler.get_next_crawl_time(now, conf)

        # testa período inválido de recoleta
        with self.assertRaises(ValueError):
            conf = {'repeat': {'every': -1, 'interval': 'days'}}
            new_crawl = scheduler.get_next_crawl_time(now, conf)

    def test_get_next_crawl_by_weeks(self):
        '''Verifica todos parâmetros para agendamentos por semanas.
        '''

        scheduler = SchedulerPlugin()
        max_weeks = 52

        now = datetime.now()
        for at_weekday in range(7):
            for at_hour in range(24):
                for at_minute in range(60):
                    for delta_weeks in range(1, max_weeks):
                        conf = {
                            'repeat': {
                                'every': delta_weeks,
                                'interval': 'weeks',
                                'at_weekday': at_weekday,
                                'at_hour': at_hour,
                                'at_minute': at_minute
                            }
                        }

                        new_crawl = scheduler.get_next_crawl_time(now, conf)

                        self.assertTrue(new_crawl.weekday() == at_weekday)
                        self.assertTrue(new_crawl.hour == at_hour)
                        self.assertTrue(new_crawl.minute == at_minute)

        # testa período de recoleta inválido
        with self.assertRaises(ValueError):
            conf = {'repeat': {'every': 0, 'interval': 'weeks'}}
            new_crawl = scheduler.get_next_crawl_time(now, conf)

        # testa período inválido de recoleta
        with self.assertRaises(ValueError):
            conf = {'repeat': {'every': -1, 'interval': 'weeks', }}
            new_crawl = scheduler.get_next_crawl_time(now, conf)

    def _income_listener(self):
        '''Método com consumidor kafka que recebe mensagens do tópico de entrada do Scrapy Cluster.
        '''

        self.crawls_timestamp_received = list()
        for message in self.kafka_consumer:
            timestamp = ujson.loads(message.value)['ts']
            self.crawls_timestamp_received.append(timestamp)

            if not self.keep_running:
                break

    def test_schedule(self):
        '''Verifica se é possível definir recoletas e se elas ocorrem corretamente.
        '''

        scheduler = SchedulerPlugin(time_delta=60)
        req = {
            'url': 'https://www.google.com',
            'appid': 'testapp',
            'crawlid': 'xyz',
            'spiderid': 'test_spider',
            'scheduler': {
                'repeat': {
                    'every': 1,
                    'interval': 'minutes'
                },
            }
        }

        thread = threading.Thread(target=self._income_listener, daemon=True)
        thread.start()

        scheduler.handle(req)
        time.sleep(61)
        self.keep_running = False

        # Como recoletas ocorrem no intervalo de um minuto e o tempo esta passando virtualmente 60 segundos por segundo real,
        # é esperado que haja, pelo menos, 60 requisições de coletas enviadas ao tópico de entrada do SC
        self.assertTrue(len(self.crawls_timestamp_received) >= 60)
