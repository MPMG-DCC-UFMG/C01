import ujson
import redis
import sys
import logging

import numpy as np

from auto_scheduler.estimator import Estimator
from auto_scheduler import settings

SECONDS_IN_WEEK = 604800
SECONDS_IN_DAY = 86400
SECONDS_IN_HOUR = 3600
SECONDS_IN_MINUTE = 60


class AutoScheduler:
    '''Responsible for processing visit history for estimators and sending revisit updates to the scheduler
    '''

    redis_conn = redis.Redis(host=settings.REDIS_HOST,
                            port=settings.REDIS_PORT,
                            db=settings.REDIS_DB,
                            password=settings.REDIS_PASSWORD,
                            decode_responses=True,
                            socket_timeout=settings.REDIS_SOCKET_TIMEOUT,
                            socket_connect_timeout=settings.REDIS_SOCKET_TIMEOUT)

    try:
        redis_conn.info()

    except ConnectionError:
        print('Failed to connect to Redis.')
        sys.exit(1)

    @staticmethod
    def send_schedule_update(crawlid: str, schedule: dict):
        '''Sends revisit updates to the scheduler.

        Args:
            crawlid: Unique crawl identifier (URL md5 hash)
            schedule: Updated visit scheduling setup
        '''

        key = f'scheduling_updates::{crawlid}'
        val = ujson.dumps(schedule)

        AutoScheduler.redis_conn.set(key, val)

    @staticmethod
    def frequency_changes_to_schedule_conf(frequency_changes: float) -> dict:
        '''Converts the estimated change frequency to the scheduler configuration pattern.

        Args:
            frequency_changes: Estimated frequency of changes in seconds

        Returns:
            Dictionary with visits setup for scheduler

        '''

        if frequency_changes > SECONDS_IN_WEEK:
            return {'interval': 'weeks', 'every': frequency_changes / SECONDS_IN_WEEK}

        elif frequency_changes > SECONDS_IN_DAY:
            return {'interval': 'days', 'every': frequency_changes / SECONDS_IN_DAY}

        elif frequency_changes > SECONDS_IN_HOUR:
            return {'interval': 'hours', 'every': frequency_changes / SECONDS_IN_HOUR}

        else:
            return {'interval': 'minutes', 'every': frequency_changes / SECONDS_IN_MINUTE}

    @staticmethod
    def update_crawl_frequency(crawlid: str, crawl_historic: list) -> float:
        ''' Updates the frequency of crawl visits

        Args:
            crawlid: Unique crawl identifier (URL md5 hash)
            crawl_historic: crawlid's crawl history

        Returns:
            The estimated frequency of changes
        '''

        timestamps = list()
        crawl_hashes = set()

        for crawl in crawl_historic:
            timestamps.append(crawl['timestamp'])
            crawl_hashes.add(crawl['crawl_hash'])

        crawl_interval = np.mean(np.diff(timestamps))
        num_changes = len(crawl_hashes)
        num_visits = len(crawl_historic)

        if settings.ESTIMATOR == 'changes':
            estimated_frequency_changes = Estimator.estimate_by_changes(
                num_changes, num_visits, crawl_interval)

        elif settings.ESTIMATOR == 'nochanges':
            estimated_frequency_changes = Estimator.estimate_by_nochanges(
                num_changes, num_visits, crawl_interval)

        else:
            raise ValueError(
                f'"{settings["estimator"]}" is an invalid estimator. Valid ones are "changes" and "nochanges".')

        schedule_conf = AutoScheduler.frequency_changes_to_schedule_conf(
            estimated_frequency_changes)
        AutoScheduler.send_schedule_update(crawlid, schedule_conf)

        return estimated_frequency_changes
