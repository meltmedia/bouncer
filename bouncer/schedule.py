from apscheduler.schedulers.background import BackgroundScheduler

import logging

log = logging.getLogger(__name__)
scheduler = BackgroundScheduler()


def init(funcs, frequency=5):
    scheduler.start()
    for func in funcs:
        seconds = frequency * 60

        scheduler.add_job(
            func, trigger='interval', seconds=seconds, name=func.__name__,
            max_instances=1, coalesce=True, misfire_grace_time=60)


def stop():
    scheduler.shutdown()
