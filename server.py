import argparse
import logging
import werkzeug.serving

import bouncer.ext.args as extargs
import bouncer.ext.easylog as easylog

import bouncer.config as config
import bouncer.schedule as schedule
import bouncer.whitelist as whitelist
import bouncer.views as views

log = logging.getLogger('bouncer.server')


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
        '-d', '--debug',
        default=False, action='store_true',
        help='Enable debug mode')
    parser.add_argument(
        '-R', '--reloader',
        default=False, action='store_true',
        help='Enable the reloader')

    return parser.parse_args(data)


def run(host='127.0.0.1', port=4010, debug=False, reloader=False, **kwargs):
    whitelist.init()

    app = views.init(debug=debug)

    scheduleEnabled = not kwargs['disable_schedule']

    if reloader and scheduleEnabled:
        print "* Disabling schedule due to reloader being enabled."
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

    log.debug('Starting bouncer')

    config.load(filenames=args.config)
    config.data['arguments'] = args.__dict__

    run(**args.__dict__)
