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
* Git Support.
* Support uploading.
* Administration interface.
* Check against security groups.
* Save Whitelist changes to speed up next start.

## Configuration

Configuration files are kept in the etc folder. Refer to the [defaults](etc/defaults.json) for options.

### Backends

Example backend configurations for S3 and Github. S3 accounts must be defined under the accounts section.

```
    "backends": {
      "example": {
        "provider": "bouncer.providers.s3.S3Provider",
        "path": "/",
        "account": "example",
        "bucket": "my-bucket-example",
        "prefix": "",
        "writable": false
      },
      "example-git": {
        "provider": "bouncer.providers.github.GithubProvider",
        "path": "/github/example/",
        "writable": false,
        "owner": "my-example-org",
        "token": null
      }
    }
```

### Remote Configuration

Loading encrypted configuration from a remote service is supported. In order to use this feature both `BOUNCER_SECRET` and `BOUNCER_CONFIG` environment variables need to be set. Currently the remote configuration can return base64 encoded text or a JSON object with the base64 encoded text under the key `data` or a key set by the environment variable `BOUNCER_ENC_KEY`.

Example remote configuration:

```
{
  "data": "<enc-string>"
}
```

## Running

The project can be run with the following command.

```
$ python -m bouncer -w 127.0.0.1
```

## Tests

Tests can be run with `make test`.

## License

Bouncer is free software distributed under the terms of the MIT license reproduced in the LICENSE file.

