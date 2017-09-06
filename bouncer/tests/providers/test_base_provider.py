import unittest

from ... import providers


class TestBaseProvider(unittest.TestCase):
    def setUp(self):
        self.provider = providers.BaseProvider(None)

    def test_init(self):
        """ it's a no-op method """
        self.provider.init(None)

    def test_get(self):
        self.assertRaises(NotImplementedError, self.provider.get)

    def test_post(self):
        self.assertRaises(NotImplementedError, self.provider.post)

    def test_put(self):
        self.assertRaises(NotImplementedError, self.provider.put)

    def test_delete(self):
        self.assertRaises(NotImplementedError, self.provider.delete)

    def test_call(self):
        self.assertRaises(NotImplementedError, self.provider)
