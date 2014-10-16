from . import BaseProvider

import flask
import mimetypes

from boto.s3.connection import S3Connection

from .. import config


DEFAULT_MIMETYPE = "application/data"


class S3Provider(BaseProvider):
    def init(self, backend):
        self.backend = backend

        self.conn = self._connect()

    def _connect(self):
        account = self.backend['account']

        key = secret = None
        if account:
            key = config.accounts[account]['key']
            secret = config.accounts[account]['secret']

        conn = S3Connection(key, secret)

        return conn.get_bucket(self.backend['bucket'], validate=False)

    def serve(self, path=None):
        if not path:
            path = "index.html"

        filepath = "%s/%s" % (self.backend['prefix'], path)
        filepath = filepath.replace('//', '/')

        key = self._connect().lookup(filepath)

        if not key:
            flask.abort(404)

        def generate():
            for bytes in key:
                yield bytes

        mime = mimetypes.guess_type(filepath)[0] or DEFAULT_MIMETYPE

        return flask.Response(generate(), mimetype=mime)
