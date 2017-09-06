import argparse
import json
import logging
import os
import werkzeug.serving

from .ext import args as extargs
from .ext import easylog
from .ext import crypto

from . import config
from . import schedule
from . import whitelist
from . import views

LOG = logging.getLogger('bouncer.server')

ENV_SECRET = 'BOUNCER_SECRET'
ENV_CONFIG = 'BOUNCER_CONFIG'
ENV_ENC_KEY = 'BOUNCER_ENC_KEY'


def get_args(data=None):
    default_parent = extargs.defaults(
        default_config=config.DEFAULT_FILES)

    parser = argparse.ArgumentParser(parents=[default_parent])

    parser.add_argument(
        '-p', '--port', default=4010,
        help='Set the port number to run on.')
    parser.add_argument(
        '-H', '--host', default='127.0.0.1',
        help='Set the host address to listen on.')

    parser.add_argument(
        '--disable-schedule', default=False, action='store_true',
        help='Disable the schedule to update instances')

    parser.add_argument(
        '-w', '--whitelist', action='append', default=[],
        help='IP addresses to whitelist'
    )

    parser.add_argument(
        '-d', '--debug',
        default=False, action='store_true',
        help='Enable debug mode')
    parser.add_argument(
        '-R', '--reloader',
        default=False, action='store_true',
        help='Enable the reloader')

    return parser.parse_known_args(data)[0]


def remote_config():
    if not os.environ.get(ENV_CONFIG):
        return {}

    if not os.environ.get(ENV_SECRET):
        LOG.warning('No secret to decrypt configuration')
        return {}

    url = os.environ.get(ENV_CONFIG)
    secret = os.environ.get(ENV_SECRET)
    enc_key = os.environ.get(ENV_ENC_KEY, 'data')

    LOG.info('Loading remote configuration from %s', url)
    data = crypto.read(url)

    try:
        data = json.loads(data)[enc_key]
    except (ValueError, KeyError):
        LOG.warning('Unable to load remote data as json, trying to use as is.')

    try:
        return json.loads(crypto.decrypt(secret, data))
    except Exception as err:
        LOG.error('Unable to decrypt data: %s', err)
        return {}


def run(host='127.0.0.1', port=4010, debug=False, reloader=False, **kwargs):
    whitelist.init()

    app = views.init(debug=debug)

    scheduleEnabled = not kwargs['disable_schedule']

    if reloader and scheduleEnabled:
        LOG.info("* Disabling schedule due to reloader being enabled.")
        scheduleEnabled = False

    if scheduleEnabled:
        schedule.init([whitelist.update])

    werkzeug.serving.run_simple(
        host, int(port), app, threaded=True,
        use_reloader=reloader, use_debugger=debug)

    if scheduleEnabled:
        schedule.stop()


if __name__ == '__main__':
    args = get_args()
    easylog.default(level=args.level, filename=args.logconfig)

    LOG.debug('Starting bouncer')

    config.load(filenames=args.config)
    config.data['arguments'] = args.__dict__

    config.data.update(remote_config())

    for address in args.whitelist:
        config.data['access']['whitelist'].append(address)

    run(**args.__dict__)
