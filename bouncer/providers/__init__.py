class BaseProvider():
    def __init__(self, backend):
        self.init(backend)

    def init(self, backend):
        """ Initialization method to override """
        pass

    def __call__(self, path=None):
        return self.serve(path)

    def serve(self, path=None):
        raise NotImplementedError()
