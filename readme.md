# aws-web-server

The purpose of this web server is to offer up files only to authorized ec2 instances. This will query the ec2 endpoints and allow ip or group based file access. 

Features:
* select "home" region
* combined ips from multiple regions
* regularly check for new ips
* supports multiple aws accounts
* ip address white listing for non ec2 addresses 

Todo:
* check against security groups

## Configuration

Configuration files are kept in the config folder. Refer to the examples included.

### AWS Configuration

The aws configuration contains the Access ID and Secret Key for each account, as well as what endpoints are available and active.

    {
      "accounts": [
        {
          "name": "account one",
          "id": "ACCOUNT_ONE_ID",
          "key": "ACCOUNT_ONE_KEY",
          "active": ["us-east-1", "us-west-1"]
        },
        {
          "name": "account two",
          "id": "ACCOUNT_TWO_ID",
          "key": "ACCOUNT_TWO_KEY",
          "active": ["us-east-1", "eu-west-1"]
        }
      ],
      "regions": {
        "us-west-1": "ec2.us-west-1.amazonaws.com",
        "us-west-2": "ec2.us-west-2.amazonaws.com",
        "us-east-1": "ec2.us-east-1.amazonaws.com",
        "eu-west-1": "ec2.eu-west-1.amazonaws.com",
        "sa-east-1": "ec2.sa-east-1.amazonaws.com",
        "ap-southeast-1": "ec2.ap-southeast-1.amazonaws.com",
        "ap-southeast-2": "ec2.ap-southeast-2.amazonaws.com",
        "ap-northeast-1": "ec2.ap-northeast-1.amazonaws.com"
      }
    }

### Server Configuration

The server configuration sets the port to listen on (http), whether or not to use ssl (https), if ssl is enabled what paths to find the certificates at, what region the server is running in (differentiate when to use public or private ips), and what folder(s) to server content from. If no content folder is specified it defaults to the current directory /public.

For more ssl options see http://nodejs.org/api/tls.html#tls_tls_createserver_options_secureconnectionlistener

Support for serving multiple directories is supported. Each entry under public will be configured to server content. 

If the application is going to sit behind a trusted proxy (apache, nginx), adding the proxy setting will allow ip detection to work properly.

To disable listening on a port, simply remove it from the configuration

    {
      "http": 4010,
      "https": 4013,
      "home": "us-east-1",
      "proxy": true,
      "reload_interval": 5,
      "ssl_options": {
        "cert": "./ssl/star_meltdev_com.crt",
        "key": "./ssl/star_meltdev_com.key",
        "ca": ["./ssl/DigiCertCA.crt"]
      },
      "public": [
        {
          "context": "/example",
          "path": "/Users/jkennedy/git/meltmedia/sysops/aws-web-server/public"
        },
        {
          "context": "/",
          "path": "/Users/jkennedy/git/meltmedia/sysops/aws-web-server/public"
        }
      ],
      "whitelist": [
        "127.0.0.1"
      ]
    }

### Logging Configuration

Logging level, and locations can be configured. If access log is defined that filename will be used instead of the default logger. It's level is set at debug and all access requests from express are logged there.

The out logger is used for all other items inside the application and it's level is configured via the level option. Stdout logging can be enable or disable independently of the out file being defined. If the out file is not defined messages will still be logged through stdout (unless stdout is also disabled). Colorizing is configurable for stdout logging only. For the file outputs json logging is disabled.

    {
      "level": "info",
      "access": "access.log",
      "out": "server.log",
      "stdout": false,
      "colorize": false
    }
