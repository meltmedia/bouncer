from mock import patch, mock_open
import unittest

# Check if the import of yaml will cause a problem, and fake it.
try:
    import yaml  # noqa
except:
    import sys

    class FakeYaml(object):
        @staticmethod
        def load(file_handle):
            raise Exception('Yaml could not be loaded')

    sys.modules["yaml"] = FakeYaml

from .. import config


class TestConfig(unittest.TestCase):
    def test_base_loader(self):
        loader = config.BaseLoader()

        self.assertRaises(NotImplementedError, loader.extension)
        self.assertRaises(NotImplementedError, loader.load, None)

    @patch('json.load')
    def test_json_loader(self, json_load):
        json_load.return_value = 'json-data'

        loader = config.JsonLoader()

        self.assertEqual(loader.extension(), 'json')

        m = mock_open()

        with patch('{}.open'.format(config.__name__), m, create=True):
            results = loader.load('my-config')

        m.assert_called_once_with('my-config', 'rt')
        self.assertEqual(results, 'json-data')

    @patch('yaml.load')
    def test_yaml_loader(self, yaml_load):
        yaml_load.return_value = 'yaml-data'

        loader = config.YamlLoader()

        self.assertEqual(loader.extension(), 'yaml')

        m = mock_open()

        with patch('{}.open'.format(config.__name__), m, create=True):
            results = loader.load('my-config')

        m.assert_called_once_with('my-config', 'rt')
        self.assertEqual(results, 'yaml-data')
