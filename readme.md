# aws-web-server

The purpose of this web server is to offer up files only to authorized ec2 instances. This will query the ec2 endpoints and allow ip or group based file access. 

Features:
* select "home" region
* combined ips from multiple regions
* regularly check for new ips

Todo:
* Support multiple aws accounts
* check against groups
