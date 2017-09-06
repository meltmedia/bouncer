import flask

DEFAULT_METHOD = 'get'


class BaseProvider():
    def __init__(self, backend):
        self.init(backend)

    def init(self, backend):
        """ Initialization method to override """
        pass

    def __call__(self, path=None):
        """ Main entry point to a provider """
        return getattr(self, self._get_method())(path)

    def _get_method(self):
        try:
            return flask.request.method.lower()
        except RuntimeError:
            return DEFAULT_METHOD

    def get(self, path=None):
        raise NotImplementedError()

    def post(self, path=None):
        raise NotImplementedError()

    def put(self, path=None):
        raise NotImplementedError()

    def delete(self, path=None):
        raise NotImplementedError()
