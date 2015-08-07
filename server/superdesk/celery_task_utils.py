# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import logging
from flask import current_app as app
from superdesk.utc import utcnow, get_date
from eve.utils import date_to_str
from datetime import timedelta

logger = logging.getLogger(__name__)


def __get_running_key(name, id):
    return 'task-running-{}:{}'.format(name, id)


def is_task_running(name, id, update_schedule):
    """
    Returns False if the instance was never run before or is not currently running.
    True otherwise.
    If the instance is not already running, we set it as running using locking.
    """
    def set_if_not_running(pipe):
        last_updated = pipe.get(key)
        if last_updated:
            last_updated = get_date(str(last_updated))
            delta = last_updated + update_schedule
            if delta < now:
                logger.warn('Overwriting running key for {}:{}'.format(name, id))
                pipe.set(key, date_to_str(now))
                return True
            else:
                logger.warn('Task {}:{} is already running. last_updated={}'.format(name, id, last_updated))
                return False
        else:
            pipe.set(key, date_to_str(now))
            return True

    key = __get_running_key(name, id)
    now = utcnow()

    if 'minutes' in update_schedule:
        update_schedule = timedelta(minutes=update_schedule.get('minutes', 5))
    elif 'seconds' in update_schedule:
        update_schedule = timedelta(seconds=update_schedule.get('seconds', 10))

    is_set = __redis_transaction(set_if_not_running, key)
    return not is_set


def mark_task_as_not_running(name, id):
    def remove_key(pipe):
        is_removed = pipe.delete(key)
        return True if is_removed > 0 else False

    key = __get_running_key(name, id)
    removed = __redis_transaction(remove_key, key)
    if not removed:
        logger.error('Failed to set {}:{} as not running'.
                     format(name, id))
    return removed


def __redis_transaction(func, key):
    """
    Modified version of the transaction class from the Redis library.
    We want to exit if someone else is modifying the value.
    Convenience method for executing the callable `func` as a transaction
    while watching all keys specified in `watches`. The 'func' callable
    should expect a single argument which is a Pipeline object.
    """
    with app.redis.pipeline(True, None) as pipe:
        try:
            if key:
                pipe.watch(key)
            func_value = func(pipe)
            pipe.execute()
            return func_value
        except Exception as ex:
            print(ex)
            return False
