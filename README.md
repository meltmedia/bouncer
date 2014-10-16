# Bouncer

The purpose of this web server is to offer up files only to authorized ec2 instances. This will query the ec2 endpoints and allow ip based file access. 

Features:
* select "home" region
* combined ips from multiple regions
* regularly check for new ips
* supports multiple aws accounts
* ip address white listing for non ec2 addresses 
* rechecks ec2 addresses
* blacklisting
* quiet periods to prevent DOS attacks from unrecognized addresses

Future:
* Add API Endpoints.
* Cleanup how providers are loaded.
* Git and Github Support.
* Support uploading.
* Administration interface.
* Check against security groups.
* Save Whitelist changes to speed up next start.

## Configuration

Configuration files are kept in the etc folder. Refer to the [defaults](etc/defaults.json) for options.

## License

Bouncer is free software distributed under the terms of the MIT license reproduced in the LICENSE file.

