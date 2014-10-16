import flask
import logging

from . import config
from . import whitelist

# TODO: Implement a better way to discover providers.
from .providers.s3 import S3Provider  # noqa


log = logging.getLogger(__name__)
access_log = logging.getLogger('bouncer.access')


def init(debug=False):
    log.debug('initializing flask application')

    app = flask.Flask(__name__)
    app.debug = debug
    app.secret = config.flask['secret']

    register(app)

    return app


# TODO: Strike a balance between secure and paranoid
def get_address():
    # Are we hitting the server directly? Probably not proxied.
    if flask.request.host.endswith(':%s' % config.arguments['port']):
        return flask.request.remote_addr

    if flask.request.headers.getlist("X-Forwarded-For"):
        return flask.request.headers.getlist("X-Forwarded-For")[-1]

    flask.abort(403)


def allowed():
    address = get_address()
    if not whitelist.isAllowed(address):
        access_log.warn(
            'DENY %s %s %s' %
            (address, flask.request.host, flask.request.path))
        flask.abort(403)

    access_log.info(
        'ALLOW %s %s %s' %
        (address, flask.request.host, flask.request.path))


def missing(e):
    return config.messages['missing'], 404


def unauthorized(e):
    return config.messages['forbidden'], 403


def register(app):
    log.debug('registering flask routes')

    app.before_request(allowed)
    app.register_error_handler(404, missing)
    app.register_error_handler(403, unauthorized)

    for backend_name in config.backends:
        try:
            registerBackend(app, backend_name, config.backends[backend_name])
        except Exception as e:
            log.error("Unable to register backend '%s': %s"
                      % (backend_name, e))


def registerBackend(app, name, backend):
    log.info('registering backend %s at %s' % (name, backend['path']))

    # Perform normalizations
    path = backend['path']
    if not path.endswith('/'):
        path = "%s/" % path

    catch_path = "%s/<path:path>" % path
    catch_name = "%s/path" % name

    path = path.replace('//', '/')
    catch_path = catch_path.replace('//', '/')

    provider = globals()['%sProvider' % backend['type']]

    app.add_url_rule(path, name, provider(backend))
    app.add_url_rule(catch_path, catch_name, provider(backend))
