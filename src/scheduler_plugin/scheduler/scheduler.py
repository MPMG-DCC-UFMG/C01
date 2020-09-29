from __future__ import absolute_import
from .base_handler import BaseHandler

import redis
import ujson
import threading
import time

from datetime import datetime, timedelta
from kafka import KafkaProducer


class SchedulerPlugin(BaseHandler):
    schema = "scheduler_schema.json"
    scheduled = set()

    def setup(self, settings):
        '''Configuration of the basic elements of the class.
        '''

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

        self.run_daemon()

    def handle(self, dict):
        '''Processes a valid API request

        Args:
            dict: a valid dictionary object

        Returns:
            None

        '''

        self.schedule(dict)

        dict['parsed'] = True
        dict['valid'] = True

    def calculate_weekday_shift(self, weekday: int, target_weekday: int) -> int:
        '''Calculates the number of days between one day and the other of the week.

        Args:
            weekday: day of origin. Where Monday = 0 ... Sunday = 6
            target_weekday: target day. Where Monday = 0 ... Sunday = 6

         Returns:
            The number of days between `weekday` and `target_weekday`

        '''

        if target_weekday >= weekday:
            return target_weekday - weekday
        return 7 - weekday + target_weekday

    def calculate_hour_shift(self, hour: int, target_hour: int) -> int:
        '''Calculates the number of hours between one hour and the next.

        Args:
            hour: time of origin.
            target_hour: time of origin.

        Returns:
            Returns the number of hours between `hour` and` target_hour`

        '''

        if target_hour >= hour:
            return target_hour - hour
        return 24 - hour + target_hour

    def get_next_crawl_by_time(self, now: datetime, start_at: str) -> datetime:
        '''Returns the time of the next crawl based on a defined value.

        Args:
            now: Current time.
            start_at: Crawl time in "Y-m-d H:M" format.

        Returns:
            Returns the time of the next crawl defined by `start_at`, or None, if something went wrong.

        '''

        try:
            next_crawl = datetime.strptime(start_at, '%Y-%m-%d %H:%M')
            if next_crawl < now:
                return None
            return next_crawl

        except:
            return None

    def get_next_crawl_by_minutes(self, now: datetime, delta: int) -> datetime:
        '''Returns the time of the next crawl based on the `delta` step in minutes.

        Args:
            now: Current time.
            delta: Step in minutes for the next crawl.

        Returns:
            Returns the next crawl time.

        '''

        return now + timedelta(minutes=delta)

    def get_next_crawl_by_hours(self, now: datetime, delta: int, at_minute: int = -1, from_hour: int = -1, to_hour: int = -1) -> datetime:
        '''Returns the time of the next collection based on the `delta` step in hours.

        Args:
            now: Current time.
            delta: Step size in hours for the next crawl.
            at_minute: If greater than or equal to zero, the minute the crawl should be processed.
            from_hour: If greater than or equal to zero and `to_hour` also, the shortest time the crawl must be processed.
            to_hour: If greater than or equal to zero and `from_hour` as well, the longest time the crawl must be processed.

        Returns:
            Returns the next collection time.

        '''

        next_crawl = now + timedelta(hours=delta)

        if from_hour >= 0 and to_hour >= 0:
            crawl_hour = next_crawl.hour

            if from_hour > to_hour:
                if crawl_hour < from_hour and crawl_hour > to_hour:
                    hours_shift = self.calculate_hour_shift(
                        crawl_hour, from_hour)
                    next_crawl += timedelta(hours=hours_shift)

            elif crawl_hour < from_hour or crawl_hour > to_hour:
                hours_shift = self.calculate_hour_shift(crawl_hour, from_hour)
                next_crawl += timedelta(hours=hours_shift)

        if at_minute >= 0:
            return next_crawl.replace(minute=at_minute)

        return next_crawl

    def get_next_crawl_by_days(self, now: datetime, delta: int, at_hour: int = -1, at_minute: int = -1, from_weekday: int = -1, to_weekday: int = -1) -> datetime:
        '''Returns the next collection time based on the `delta` step in days.

        Args:
            now: Current time.
            delta: Step in days for the next crawl.
            at_hour: If greater than or equal to 0, the time the crawl should be processed.
            at_minute: If greater than or equal to 0, the minute the crawl must be processed.
            from_weekday: If greater than or equal to 0 and `to_weekday` also, the minimum day of the week that the crawl must be processed. Where Monday = 0.. Sunday = 6
            to_weekday: If greater than or equal to 0 and `from_weekday` also, the maximum day of the week that the crawl should be processed. Where Monday = 0.. Sunday = 6

        Returns:
            Returns the next crawl time.

        '''

        next_crawl = now + timedelta(days=delta)

        if from_weekday >= 0 and to_weekday >= 0:
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

        if at_hour >= 0:
            next_crawl = next_crawl.replace(hour=at_hour)

        if at_minute >= 0:
            next_crawl = next_crawl.replace(minute=at_minute)

        return next_crawl

    def get_next_crawl_by_weeks(self, now: datetime, delta: int, at_weekday: int = -1, at_hour: int = -1, at_minute: int = -1) -> datetime:
        '''Returns the next crawl time based on the `delta` step in weeks.

        Args:
            now: Current time.
            delta: Step size in weeks for the next crawl.
            at_weekday: If greater than or equal to 0, day of the week that the scheduled crawl should be processed. Where Monday = 0 ... Sunday = 6
            at_hour: If greater than or equal to 0, time that the scheduled crawl must be processed.
            at_minute: If greater than or equal to 0, minute that the scheduled crawl should be processed.

        Returns:
            Returns the time of the next collection.

        '''

        next_crawl = now + timedelta(weeks=delta)

        if at_weekday >= 0:
            crawl_weekday = next_crawl.weekday()

            if crawl_weekday != at_weekday:
                days_shift = self.calculate_weekday_shift(
                    crawl_weekday, at_weekday)
                next_crawl += timedelta(days=days_shift)

        if at_hour >= 0:
            next_crawl = next_crawl.replace(hour=at_hour)

        if at_minute >= 0:
            next_crawl = next_crawl.replace(minute=at_minute)

        return next_crawl

    def validate_field(self, conf: dict, key: str, min_val: int, max_val: int) -> int:
        '''Validates that the value of `key` in` conf` respects the restrictions of `min_val` and` max_val`

        Args:
            conf: Dictionary with crawl settings.
            key: Key to a value in `conf` that will be validated.
            min_val: Minimum value that the value of the key in `conf` is valid.
            max_val: Maximum value that the value of the key in `conf` is valid.

        Returns:
            The value of `key` in` conf` or -1 if the restrictions have not been satisfied.

        '''

        if key in conf:
            val = conf[key]

            if type(val) is not int:
                return -1

            elif val < min_val or val > max_val:
                return -1

            else:
                return val

        else:
            return -1

    def parse_hour_conf(self, conf: dict) -> tuple:
        '''Validates and/or standardizes the crawls settings fields per hour.

        Args:
            conf: Crawl settings per hour.

        Returns:
            Returns the values of hourly crawl settings.

        '''

        at_minute = self.validate_field(conf, 'at_minute', 0, 59)

        from_hour = self.validate_field(conf, 'from', 0, 23)
        to_hour = self.validate_field(conf, 'to', 0, 23)

        if from_hour == -1 or to_hour == -1:
            from_hour = -1
            to_hour = -1

        return at_minute, from_hour, to_hour

    def parse_day_conf(self, conf: dict) -> tuple:
        '''Validates and/or standardizes the crawl schedule settings fields per day.

        Args:
            conf: Configuration of crawl per day.

        Returns:
            Returns standardized values for crawl schedule settings per day.

        '''

        at_hour = self.validate_field(conf, 'at_hour', 0, 23)
        at_minute = self.validate_field(conf, 'at_minute', 0, 59)

        from_weekday = self.validate_field(conf, 'from', 0, 6)
        to_weekday = self.validate_field(conf, 'to', 0, 6)

        if from_weekday == -1 or to_weekday == -1:
            from_weekday = -1
            to_weekday = -1

        return at_hour, at_minute, from_weekday, to_weekday

    def parse_week_conf(self, conf: dict) -> tuple:
        '''Validates and/or standardizes the crawl schedule settings fields per week.

        Args:
            conf: Configuration of crawl per week.

        Returns:
            Returns standardized values for weekly crawl schedule settings.

        '''

        at_weekday = self.validate_field(conf, 'at_weekday', 0, 6)
        at_hour = self.validate_field(conf, 'at_hour', 0, 23)
        at_minute = self.validate_field(conf, 'at_minute', 0, 59)

        return at_weekday, at_hour, at_minute

    def get_next_crawl_time(self, now: datetime, conf: dict) -> datetime:
        '''Returns the next crawl time based on minutes, hours, days and weeks. In addition to some other restrictions.

        Args:
            now: Current time.
            conf: Configuration of crawl schedule..

        Returns:
            Returns the time of the next crawl or None, if it has been configured incorrectly.

        '''

        try:
            if conf.get('start_at'):
                next_crawl = self.get_next_crawl_by_time(now, conf['start_at'])
                del conf['start_at']
                return next_crawl

            elif conf.get('repeat'):
                conf = conf['repeat']

                delta = conf['every']
                if type(delta) is not int:
                    return None

                if delta < 1:
                    return None

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
                    return None

            else:
                return None

        except Exception as e:
            self.logger.error(str(e))
            return None

    def schedule_crawl(self, timestamp: str, crawl: dict) -> bool:
        '''Schedule a visit.

        Args:
            timestamp: Timestamp of when crawl will occur.
            crawl: Crawl configuration.

        Returns:
            Returns True if the schedule was successful, False, otherwise.

        '''

        key = f'scheduler::{timestamp}'
        val = ujson.dumps(crawl)

        if self.redis_conn.sadd(key, val):
            self.scheduled.add(timestamp)
            return True
        return self.redis_conn.sismember(key, val)

    def get_scheduled_crawls(self, timestamp: str) -> set:
        '''Retrieves crawls scheduled for a specific time.

        Args:
            timestamp: Timestamp of scheduled crawls.

        Returns:
            Returns the set of crawls scheduled for a specific time.

        '''

        key = f'scheduler::{timestamp}'

        crawls = self.redis_conn.smembers(key)
        self.redis_conn.delete(key)

        return crawls

    def send_crawl(self, crawl: dict) -> None:
        '''Sends a crawl to be processed by the Scrapy Cluster.

        Args:
            crawl: Dictionary containing information about the visit to be performed..

        Returns:
            None.

        '''

        del crawl['scheduler']
        del crawl['ts']

        self.producer.send(self.incoming_topic, crawl)
        self.logger.info('Crawl sent to Kafka by Scheduler')

    def schedule(self, req: dict) -> bool:
        '''Schedule a visit.

        Args:
            req: Request for crawl schedule.

        Returns:
            Returns True if the scheduling was successful, False, otherwise.

        '''

        # removes metadata from the SC, as well as null default values assigned by it.
        req = dict((key, req[key]) for key in req if req[key])

        if 'scheduler' not in req:
            return False

        crawl_req = req['scheduler']
        now = datetime.now()
        next_crawl_time = self.get_next_crawl_time(now, crawl_req)

        if next_crawl_time:
            timestamp = next_crawl_time.strftime("%Y-%m-%d %H:%M")
            if self.schedule_crawl(timestamp, req):
                self.logger.info(
                    f'Crawl scheduled for {timestamp} sucessfully')
                return

        self.logger.info("Failed to schedule crawl")

    def daemon(self) -> None:
        '''Thread that checks if it is time for a scheduled crawl is in time to be processed by the Scrapy Cluster and to be rescheduled.
        '''

        while True:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

            if timestamp in self.scheduled:
                scheduled_crawls = self.get_scheduled_crawls(timestamp)

                for req in scheduled_crawls:
                    crawl = ujson.loads(req)

                    self.schedule(crawl)
                    self.send_crawl(crawl)

                self.producer.flush()
                self.scheduled.remove(timestamp)

            time.sleep(60 - datetime.now().second)

    def run_daemon(self):
        '''Starts the thread responsible for checking when crawls will be processed.
        '''

        thread = threading.Thread(target=self.daemon, daemon=True)
        thread.start()
