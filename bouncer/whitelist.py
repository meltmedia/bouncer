import datetime
import math

from . import config
from . import ec2

INIT_SETS = ['blacklist', 'whitelist', 'detected']


def init():
    """ Transform any lists to sets to speed up comparisons """
    for s in INIT_SETS:
        config.access[s] = set([str(a) for a in config.access[s]])


def isAllowed(address):
    """ Check the lists and update if needed """
    if address in config.access['blacklist']:
        return False

    if address in config.access['whitelist']:
        return True

    if address in config.access['detected']:
        return True

    return updateAndCheck(address)


def updateAndCheck(address):
    if not isThrottled(address):
        update(live=True)

    if address in config.access['detected']:
        return True

    return False


def isThrottled(address):
    """ Check to see if we need to throttle this request """
    # Add them to the updates if they're not there and return
    if address not in config.access['updates']:
        config.access['updates'][address] = datetime.datetime.now()
        return False

    if isTooSoon(config.access['updates'][address]):
        return True

    config.access['updates'][address] = datetime.datetime.now()
    return False


def update(live=False):
    """ Only run the update periodically unless it is a live request """
    if not live and isTooSoon():
        return

    config.access['detected'] = set(ec2.getAll())
    config.access['last'] = datetime.datetime.now()


def isTooSoon(when=None):
    """ Check to see if the last update is within the quiet period """
    if not when:
        then = config.access['last']
    else:
        then = when

    if not then:
        return False

    now = datetime.datetime.now()

    since = math.floor((now - then).total_seconds())
    quiet = config.access['quietPeriod'] * 60

    if since < quiet:
        return True

    return False
