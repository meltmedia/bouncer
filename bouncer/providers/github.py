import base64
import flask
import mimetypes
import requests

from . import BaseProvider


DEFAULT_MIMETYPE = "application/data"
DEFAULT_ARCHIVE = 'tarball'
ARCHIVE_ZIP = 'zipball'
ARCHIVE_TAR = 'tarball'


class GithubProvider(BaseProvider):
    def init(self, backend):
        self.backend = backend

    def get(self, path=None):
        if path is None:
            flask.abort(404)

        # https://api.github.com/users/octocat/orgs
        # Accept: application/vnd.github.v3+json

        # GET /repos/:owner/:repo/contents/:path
        repository = ""
        filepath = ""
        ref = flask.request.args.get('ref', None)

        try:
            repository = path.split('/')[0]
            filepath = '/'.join(path.split('/')[1:])
        except IndexError:
            return flask.abort(404)

        if not repository:
            return flask.abort(404)

        if self._is_archive_request():
            return self._get_archive(
                repository,
                flask.request.args.get('archive_format'),
                ref)

        if not filepath:
            return flask.abort(404)

        return self._get_file(repository, filepath, ref)

    def _is_archive_request(self):
        if flask.request.args.get('archive_format') is None:
            return False

        if flask.request.args.get('ref') is None:
            return False

        return True

    def _get_archive(self, repository, archive_format, ref):
        """ Stream github archive """
        # GET /repos/:owner/:repo/:archive_format/:ref
        url = 'https://api.github.com/repos/{}/{}/{}/{}'.format(
            self.backend['owner'], repository, archive_format, ref)

        # Force the archive format into an acceptable choice
        if archive_format.startswith('zip'):
            archive_format = ARCHIVE_ZIP
        elif archive_format.startswith('tar'):
            archive_format = ARCHIVE_TAR
        else:
            archive_format = DEFAULT_ARCHIVE

        response = requests.get(url, stream=True)

        return flask.Response(
            flask.stream_with_context(response.iter_content()),
            content_type=response.headers['content-type']
        )

    def _get_file(self, repository, filepath, ref=None):
        url = 'https://api.github.com/repos/{}/{}/contents/{}'.format(
            self.backend['owner'], repository, filepath)
        params = {}

        if ref:
            params['ref'] = ref

        response = requests.get(url, headers={
            "Accept": "application/vnd.github.v3+json"
        }, params=params)

        data = {}
        try:
            data = response.json()
        except:
            return flask.abort(404)

        if type(data) is list:
            return flask.abort(404)

        if data['type'] != 'file':
            return flask.abort(404)

        mime = mimetypes.guess_type(filepath)[0] or DEFAULT_MIMETYPE

        response_data = None

        if data['encoding'] == 'base64':
            response_data = base64.b64decode(data['content'])

        if not response_data:
            return flask.abort(404)

        return flask.Response(response_data, mimetype=mime)
