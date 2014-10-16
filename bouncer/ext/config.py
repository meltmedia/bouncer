class BaseLoader(object):
    def extension(self):
        raise NotImplementedError()

    def load(self, filename):
        raise NotImplementedError()


class YamlLoader(BaseLoader):
    def extension(self):
        return 'yaml'

    def load(self, filename):
        import yaml

        with open(filename, 'rt') as f:
            return yaml.load(f)


class JsonLoader(BaseLoader):
    def extension(self):
        return 'json'

    def load(self, filename):
        import json

        with open(filename, 'rt') as f:
            return json.load(f)


class Configuration(object):
    def __init__(self, basename, loader=None):
        import logging

        self.BASE_NAME = basename
        self.ENV_PREFIX = "%s_" % self.BASE_NAME.upper()

        self.loader = loader or YamlLoader()

        self.DEFAULT_CONFIG = None
        self.DEFAULT_FILES = [
            "etc/%s.%s" % (self.BASE_NAME, self.loader.extension()),
            "~/.%s" % self.BASE_NAME
        ]

        self.data = {}
        self.log = logging.getLogger(__name__)

        self._load_default()

    def __getattr__(self, key):
        if key in self.data:
            return self.data[key]
        else:
            raise AttributeError(key)

    def _load_default(self):
        # these imports are needed due to the module hack used below.
        import os

        root = os.path.abspath('%s/../../' % os.path.dirname(__file__))

        filenames = []

        if os.path.exists('etc/defaults.%s' % self.loader.extension()):
            filenames.append('etc/defaults.%s' % self.loader.extension())

        default_path = '%s/etc/defaults.%s' % (root, self.loader.extension())
        if os.path.exists(default_path):
            filenames.append(default_path)

        self.DEFAULT_CONFIG = self.load(
            filenames=filenames,
            base={}, use_default=False)

    def get(self):
        """ Return a copy of the current configuration
        """
        # these imports are needed due to the module hack used below.
        import copy

        return copy.deepcopy(self.data)

    def load(self, filenames=None, base=None, use_default=True):
        """ Load configuration

        Kwargs:
           filenames (array): An array of filenames to load.
                              if None use defaults (default None)
           base (dict): Base configuration dictionary to update (default None)
           use_default (bool): Load the default configuration settings first.
                               If base is specified use_default will have
                               no effect.

        Returns:
           dict.  The loaded configuration settings.
        """

        # these imports are needed due to the module hack used below.
        import copy
        import os

        self.data = {}

        if use_default and self.DEFAULT_CONFIG:
            self.data = copy.deepcopy(self.DEFAULT_CONFIG)

        if base:
            self.data = base

        if filenames is None:
            filenames = self.DEFAULT_FILES

        for filename in filenames:
            if filename.startswith('~/'):
                filename = os.path.expanduser(filename)

            if not os.path.exists(filename):
                self.log.debug('file not found "%s", skipping' % filename)
                continue

            self.data.update(self.loader.load(filename))

        # populate the defaults as needed
        self.parse_defaults()

        # set any variables from the environment
        self._set_from_env()

        return self.data

    def parse_defaults(self):
        if not self.data:
            self.log.debug('no data to parse defaults from')
            return

        if 'defaults' not in self.data:
            self.log.debug('no defaults in data to parse')
            return

        for default in self.data['defaults']:
            if default not in self.data:
                continue

            # Can't do this on strings
            if isinstance(self.data[default], basestring):
                continue

            # Check if this is a dictionary
            if isinstance(self.data[default], dict):
                self._apply_dict_defaults(default)
            # Check if this is acts like list
            elif hasattr(self.data[default], "__getitem__") or \
                    hasattr(self.data[default], "__iter__"):
                self._apply_list_defaults(default)

    def _apply_list_defaults(self, default):
        # convert to a set and call union
        result = set(self.data[default])\
            .union(self.data['defaults'][default])

        # set back to a list
        self.data[default] = list(result)

    def _apply_dict_defaults(self, default):
        import copy

        for name in self.data[default]:
            data = copy.deepcopy(self.data['defaults'][default])
            data.update(self.data[default][name])
            self.data[default][name] = data

    def _set_from_env(self):
        """ Look for the ENV_PREFIX in the environment and set the
            configuration value from that variable split on underscores

            e.g. MYAPP_ACCOUNTS_ONE_SECRET="ONE" becomes accounts.one.secret
        """
        import os
        env_opts = [i for i in os.environ if i.startswith(self.ENV_PREFIX)]

        for opt in env_opts:
            mapList = [p.lower() for p in opt.split('_')[1:]]
            try:
                # get first to prevent adding extra irrelevant data
                self._get_nested(mapList)
                self._set_nested(mapList, os.environ[opt])
            except KeyError as e:
                # silently ignore KeyError
                self.log.debug('No value found for %s in %s.' % (e, mapList))
                continue

    def _get_nested(self, mapList):
        return reduce(lambda d, k: d[k], mapList, self.data)

    def _set_nested(self, mapList, value):
        self._get_nested(mapList[:-1])[mapList[-1]] = value
