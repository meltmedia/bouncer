# aws-web-server

The purpose of this web server is to offer up files only to authorized ec2 instances. This will query the ec2 endpoints and allow ip or group based file access. 

Features:
* select "home" region
* combined ips from multiple regions
* regularly check for new ips

Todo:
* Support multiple aws accounts
* check against groups

## Configuration

Configuration files are kept in the config folder. Refer to the examples included.

### AWS Configuration

The aws configuration contains the Access ID and Secret Key, as well as what endpoints are available and active.

    {
      "active": ["us-east-1", "us-west-1"],
      "id": "ID_HERE",
      "key": "KEY_HERE",
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

The server configuration sets the port to listen on, whether or not to use ssl, if ssl is enabled what paths to find the certificates at, what region the server is running in (differentiate when to use public or private ips), and what folder to server content from. If no content folder is specified it defaults to the current directory /public.

For more ssl options see http://nodejs.org/api/tls.html#tls_tls_createserver_options_secureconnectionlistener

Support for serving multiple directories is supported. Each entry under public will be configured to server content. 

    {
      "port": 4010,
      "sslport": 4013,
      "home": "us-east-1",
      "ssl": true,
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
      ]
    }
