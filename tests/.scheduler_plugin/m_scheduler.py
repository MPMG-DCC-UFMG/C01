from __future__ import absolute_import

import redis
import ujson
import threading
import time
import sys
import hashlib

from datetime import datetime, timedelta
from kafka import KafkaProducer

SETTINGS = {
    'REDIS_HOST': 'localhost',
    'REDIS_PORT': 6379,
    'REDIS_DB': 0,
    'REDIS_PASSWORD': None,
    'REDIS_SOCKET_TIMEOUT': 10,
    'KAFKA_HOSTS': ['localhost:9092'],
    'KAFKA_INCOMING_TOPIC': 'demo.incoming'
}


class SchedulerPlugin:
    def __init__(self, time_delta: float = 1):
        self.scheduled = set()
        self.now = datetime.now()
        self.time_delta = time_delta
        self.setup(SETTINGS)

    def setup(self, settings):
        self.redis_conn = redis.Redis(host=settings['REDIS_HOST'],
                                      port=settings['REDIS_PORT'],
                                      db=settings.get('REDIS_DB'),
                                      password=settings['REDIS_PASSWORD'],
                                      decode_responses=True,
                                      socket_timeout=settings.get(
                                          'REDIS_SOCKET_TIMEOUT'),
                                      socket_connect_timeout=settings.get('REDIS_SOCKET_TIMEOUT'))

        try:
            self.redis_conn.info()

        except ConnectionError:
            sys.exit(1)

        self.producer = KafkaProducer(bootstrap_servers=settings['KAFKA_HOSTS'],
                                      value_serializer=lambda m: ujson.dumps(m).encode("utf-8"))
        self.incoming_topic = settings['KAFKA_INCOMING_TOPIC']

        self.start_daemon()

    def handle(self, dict):
        self.schedule(dict)

        dict['parsed'] = True
        dict['valid'] = True

    def calculate_weekday_shift(self, weekday: int, target_weekday: int) -> int:
        if target_weekday >= weekday:
            return target_weekday - weekday
        return 7 - weekday + target_weekday

    def calculate_hour_shift(self, hour: int, target_hour: int) -> int:
        if target_hour >= hour:
            return target_hour - hour
        return 24 - hour + target_hour

    def get_next_crawl_by_time(self, now: datetime, start_at: str) -> datetime:
        next_crawl = datetime.strptime(start_at, '%Y-%m-%d %H:%M')
        if next_crawl < now:
            raise ValueError()
        return next_crawl

    def get_next_crawl_by_minutes(self, now: datetime, delta: float) -> datetime:
        return now + timedelta(minutes=delta)

    def get_next_crawl_by_hours(self, now: datetime, delta: float, at_minute: int = None, from_hour: int = None, to_hour: int = None) -> datetime:
        next_crawl = now + timedelta(hours=delta)
        if from_hour is not None and to_hour is not None:
            crawl_hour = next_crawl.hour

            if from_hour > to_hour:
                if crawl_hour < from_hour and crawl_hour > to_hour:
                    hours_shift = self.calculate_hour_shift(
                        crawl_hour, from_hour)
                    next_crawl += timedelta(hours=hours_shift)

            elif crawl_hour < from_hour or crawl_hour > to_hour:
                hours_shift = self.calculate_hour_shift(crawl_hour, from_hour)
                next_crawl += timedelta(hours=hours_shift)

        if at_minute is not None:
            return next_crawl.replace(minute=at_minute)

        return next_crawl

    def get_next_crawl_by_days(self, now: datetime, delta: float, at_hour: int = None, at_minute: int = None, from_weekday: int = None, to_weekday: int = None) -> datetime:
        next_crawl = now + timedelta(days=delta)

        if from_weekday is not None and to_weekday is not None:
            crawl_weekday = next_crawl.weekday()

            if from_weekday > to_weekday:
                if crawl_weekday < from_weekday and crawl_weekday > to_weekday:
                    days_shift = self.calculate_weekday_shift(
                        crawl_weekday, from_weekday)
                    next_crawl += timedelta(days=days_shift)

            elif crawl_weekday < from_weekday or crawl_weekday > to_weekday:
                days_shift = self.calculate_weekday_shift(
                    crawl_weekday, from_weekday)
                next_crawl += timedelta(days=days_shift)

        if at_hour is not None:
            next_crawl = next_crawl.replace(hour=at_hour)

        if at_minute is not None:
            next_crawl = next_crawl.replace(minute=at_minute)

        return next_crawl

    def get_next_crawl_by_weeks(self, now: datetime, delta: float, at_weekday: int = None, at_hour: int = None, at_minute: int = None) -> datetime:
        next_crawl = now + timedelta(weeks=delta)

        if at_weekday is not None:
            crawl_weekday = next_crawl.weekday()

            if crawl_weekday != at_weekday:
                days_shift = self.calculate_weekday_shift(
                    crawl_weekday, at_weekday)
                next_crawl += timedelta(days=days_shift)

        if at_hour is not None:
            next_crawl = next_crawl.replace(hour=at_hour)

        if at_minute is not None:
            next_crawl = next_crawl.replace(minute=at_minute)

        return next_crawl

    def validate_field(self, conf: dict, key: str, min_val: int, max_val: int) -> int:
        if key in conf:
            val = conf[key]

            if type(val) is not int:
                raise TypeError()

            elif val < min_val or val > max_val:
                raise ValueError()

            else:
                return val

        else:
            return None

    def parse_hour_conf(self, conf: dict) -> tuple:
        at_minute = self.validate_field(conf, 'at_minute', 0, 59)

        from_hour = self.validate_field(conf, 'from', 0, 23)
        to_hour = self.validate_field(conf, 'to', 0, 23)

        if from_hour is None or to_hour is None:
            from_hour = None
            to_hour = None

        return at_minute, from_hour, to_hour

    def parse_day_conf(self, conf: dict) -> tuple:
        at_hour = self.validate_field(conf, 'at_hour', 0, 23)
        at_minute = self.validate_field(conf, 'at_minute', 0, 59)

        from_weekday = self.validate_field(conf, 'from', 0, 6)
        to_weekday = self.validate_field(conf, 'to', 0, 6)

        if from_weekday is None or to_weekday is None:
            from_weekday = None
            to_weekday = None

        return at_hour, at_minute, from_weekday, to_weekday

    def parse_week_conf(self, conf: dict) -> tuple:
        at_weekday = self.validate_field(conf, 'at_weekday', 0, 6)
        at_hour = self.validate_field(conf, 'at_hour', 0, 23)
        at_minute = self.validate_field(conf, 'at_minute', 0, 59)

        return at_weekday, at_hour, at_minute

    def get_next_crawl_time(self, now: datetime, conf: dict) -> datetime:
        if conf.get('start_at'):
            next_crawl = self.get_next_crawl_by_time(now, conf['start_at'])
            del conf['start_at']
            return next_crawl

        elif conf.get('repeat'):
            conf = conf['repeat']

            delta = conf['every']
            if type(delta) is not float and type(delta) is not int:
                raise TypeError(
                    f'The step size between one crawl and another must be int or float.')

            if delta < 1:
                raise ValueError()

            interval = conf['interval']

            if interval == 'minutes':
                return self.get_next_crawl_by_minutes(now, delta)

            elif interval == 'hours':
                at_minute, from_hour, to_hour = self.parse_hour_conf(conf)
                return self.get_next_crawl_by_hours(now, delta, at_minute, from_hour, to_hour)

            elif interval == 'days':
                at_hour, at_minute, from_weekday, to_weekday = self.parse_day_conf(
                    conf)
                return self.get_next_crawl_by_days(now, delta, at_hour, at_minute, from_weekday, to_weekday)

            elif interval == 'weeks':
                at_weekday, at_hour, at_minute = self.parse_week_conf(conf)
                return self.get_next_crawl_by_weeks(now, delta, at_weekday, at_hour, at_minute)

            else:
                raise ValueError(
                    'Intervals between crawls must be: minutes, hours, days or weeks')

        else:
            raise ValueError(
                'It is necessary to define when a crawl should be made and/or its repetition configuration.')

    def schedule_crawl(self, timestamp: str, crawl: dict) -> bool:
        key = f'scheduler::{timestamp}'
        val = ujson.dumps(crawl)

        if self.redis_conn.sadd(key, val):
            self.scheduled.add(timestamp)
            return True
        return self.redis_conn.sismember(key, val)

    def get_scheduled_crawls(self, timestamp: str) -> set:
        key = f'scheduler::{timestamp}'

        crawls = self.redis_conn.smembers(key)
        self.redis_conn.delete(key)

        return crawls

    def send_crawl(self, crawl: dict):
        del crawl['scheduler']
        crawl['ts'] = self.now.timestamp()

        self.producer.send(self.incoming_topic, crawl)

    def schedule(self, req: dict) -> bool:
        crawl_req = req['scheduler']
        next_crawl_time = self.get_next_crawl_time(self.now, crawl_req)

        if next_crawl_time:
            timestamp = next_crawl_time.strftime("%Y-%m-%d %H:%M")
            return self.schedule_crawl(timestamp, req)

        return False

    def update_schedule(self, crawl: dict):
        if 'scheduler' not in crawl:
            return

        url = crawl['url']
        crawlid = hashlib.md5(url.encode()).hexdigest()

        key = f'scheduling_updates::{crawlid}'
        scheduling_update = self.redis_conn.get(key)

        if scheduling_update:
            schedule_conf = crawl['scheduler']

            scheduling_update = ujson.loads(scheduling_update)

            interval = scheduling_update['interval']
            every = scheduling_update['every']

            schedule_conf['repeat']['interval'] = interval
            schedule_conf['repeat']['every'] = every

            self.redis_conn.delete(key)

    def daemon(self) -> None:
        while True:
            timestamp = self.now.strftime("%Y-%m-%d %H:%M")
            if timestamp in self.scheduled:
                scheduled_crawls = self.get_scheduled_crawls(timestamp)

                for req in scheduled_crawls:
                    crawl = ujson.loads(req)

                    self.update_schedule(crawl)
                    self.schedule(crawl)
                    self.send_crawl(crawl)

                self.producer.flush()
                self.scheduled.remove(timestamp)

            time.sleep(1)
            self.now += timedelta(seconds=self.time_delta)

    def start_daemon(self):
        thread = threading.Thread(target=self.daemon, daemon=True)
        thread.start()
