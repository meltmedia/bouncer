import flask
import logging
import importlib

from . import config
from . import whitelist

LOG = logging.getLogger(__name__)
ACCESS_LOG = logging.getLogger('bouncer.access')
METHODS = ['GET', 'POST', 'PUT', 'DELETE']


def init(debug=False):
    LOG.debug('initializing flask application')

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
        ACCESS_LOG.warn(
            'DENY %s %s %s' %
            (address, flask.request.host, flask.request.path))
        flask.abort(403)

    ACCESS_LOG.info(
        'ALLOW %s %s %s' %
        (address, flask.request.host, flask.request.path))


def missing(e):
    return config.messages['missing'], 404


def unauthorized(e):
    return config.messages['forbidden'], 403


def register(app):
    LOG.debug('registering flask routes')

    app.before_request(allowed)
    app.register_error_handler(404, missing)
    app.register_error_handler(403, unauthorized)

    for backend_name in config.backends:
        try:
            registerBackend(app, backend_name, config.backends[backend_name])
        except Exception as e:
            LOG.error("Unable to register backend '%s': %s"
                      % (backend_name, e))


def registerBackend(app, name, backend):
    LOG.info('registering backend %s at %s with %s' % (
        name, backend['path'], backend['provider']))

    # Perform normalizations
    path = backend['path']
    if not path.endswith('/'):
        path = "%s/" % path

    catch_path = "%s/<path:path>" % path
    catch_name = "%s/path" % name

    path = path.replace('//', '/')
    catch_path = catch_path.replace('//', '/')

    # Take the provider and remove the class name
    module_name = '.'.join(backend['provider'].split('.')[:-1])
    klass_name = backend['provider'].split('.')[-1]

    i = importlib.import_module(module_name)
    provider = getattr(i, klass_name)

    app.add_url_rule(path, name, provider(backend), methods=METHODS)
    app.add_url_rule(catch_path, catch_name, provider(backend))
