import argparse


def defaults(default_config=None):
    parser = argparse.ArgumentParser(add_help=False)

    parser.add_argument(
        '-c', '--config', action='append',
        default=default_config,
        help='Configuration files to load. Can be used multiple times.'
        ' default files %s' % default_config)

    parser.add_argument(
        '--logconfig', default='etc/logging.json',
        help='Configuration file for logging.')

    parser.add_argument(
        '--level', default='info', help="Default logging level")

    return parser
