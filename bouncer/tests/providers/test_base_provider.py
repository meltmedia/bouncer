import unittest

from ... import providers


class TestBaseProvider(unittest.TestCase):
    def setUp(self):
        self.provider = providers.BaseProvider(None)

    def test_init(self):
        """ it's a no-op method """
        self.provider.init(None)

    def test_serve(self):
        self.assertRaises(NotImplementedError, self.provider.serve)

    def test_call(self):
        self.assertRaises(NotImplementedError, self.provider)
