import boto.ec2
import logging

from . import config

log = logging.getLogger(__name__)


def getAll():
    addresses = []
    for name in config.accounts:
        for region in config.accounts[name]['regions']:
            addresses.append([a for a in get(name, region)])

    return set().union(*addresses)


# TODO: Add support for VPC detection?
def get(account_name, region):
    log.info('retrieving instances for %s %s' % (account_name, region))

    account = config.accounts[account_name]
    ec2 = connect_ec2(account, region)
    instances = ec2.get_only_instances()

    for instance in instances:
        address = getattr(instance, 'ip_address', None)

        if not address:
            continue

        if region == config.region:
            address = instance.private_ip_address

        yield str(address)


def connect_ec2(account, region='us-east-1'):
    """ Get a connection to EC2 for the given account and region.

    :param account: The account object.
    :type account: dict.
    :param region: The region name to access. Defaults to 'us-east-1'.
    :type region: str.
    :returns: boto.ec2.connection.EC2Connection

    """
    aws_id = account['key']
    aws_secret = account['secret']

    return boto.ec2.connect_to_region(
        region, aws_access_key_id=aws_id, aws_secret_access_key=aws_secret)
