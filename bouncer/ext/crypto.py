import base64
import logging
import os

try:
    from simplecrypt import decrypt as _decrypt
except ImportError:
    _decrypt = lambda s, d: d

from urllib2 import urlopen


LOG = logging.getLogger(__name__)

HERE = os.getcwd()


def read(uri):
    data = None

    if callable(uri):
        data = uri()
    else:
        handle = open_uri(uri)

        data = handle.read()
        handle.close()

    return data


def decrypt(secret, data):
    return _decrypt(secret, base64.b64decode(data))


def open_uri(uri):
    try:
        handle = urlopen(uri)
    except ValueError:  # invalid URL
        handle = open(resolve_path(uri))

    return handle


def resolve_path(path):
    # check if the path needs to be expanded
    if path.startswith('~'):
        path = os.path.expanduser(path)

    # check if the path is relative
    if not path.startswith('/'):
        path = os.path.abspath(os.path.join(HERE, path))

    if not os.path.exists(path):
        msg = 'Unable to find file "{}"'.format(path)
        LOG.error(msg)
        raise ValueError(msg)

    return path
