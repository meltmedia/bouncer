var winston = require('winston');

// Colorize and timestamp console logging, and set sane levels
winston.setLevels(winston.config.syslog.levels);
winston.remove(winston.transports.Console).add(winston.transports.Console, {colorize: true, timestamp: true, level: 'debug'});

// Add a stream for express to use
var winstonStream = {
  write: function(message, encoding) {
    winston.debug(message);
  }
};

var express = require('express'),
    _ = require('underscore'),
    aws = require('aws-lib'),
    step = require('step'),
    config = require('konphyg')(__dirname + '/config');;

_.str = require('underscore.string');

var app = express();

var awsConfig = config('aws');

app.listen(4010);
winston.info("Server started on 4010")

var ec2_east = aws.createEC2Client(awsConfig.id, awsConfig.key);
var ec2_west = aws.createEC2Client(awsConfig.id, awsConfig.key, {host: awsConfig["us-west-1"]});

var ip_list = [];

var home = "us-east-1";

app.use(express.logger({stream:winstonStream}));
app.use(express.static(__dirname + '/public'));

app.all('*', function(req, res, next) {
  winston.debug("* check for ip/group " + hosts.ips.length);
  if (hosts.allow(req.ip)) {
    next();
  }
  else {

    res.send(403, "you are not from ec2")
  }
});

app.get("/", function(req, res){
  res.send('200', "welcome to the machine");
});

var hosts = {
  ips: [],

  load: function() {
    hosts.append("127.0.0.1");
    hosts._load(ec2_east);
    hosts._load(ec2_west);
  },

  _load: function(endpoint) {
    endpoint.call("DescribeInstances", {}, function(err, result) {
      var instances = result["reservationSet"]["item"];
      
      instances.forEach(function(instance) {
        hosts.append(hosts.getAddress(instance["instancesSet"]["item"]));
      });
    });
  },

  getAddress: function(instance) {
    if (_.str.startsWith(instance["placement"]["availabilityZone"], home)) {
      return instance["privateIpAddress"];
    }
    else {
      return instance["ipAddress"];
    }
  },

  append: function(address) {
    if (isDefined(address)) {
      if (_.indexOf(hosts.ips, address) == -1) {
        hosts.ips.push(address);
      }
    }
  },

  allow: function(address) {
    if (_.indexOf(hosts.ips, address) != -1) {
      return true;
    }

    return false;
  }
};

hosts.load();
winston.info(hosts.ips.length);

// UTILS
function isDefined(obj) {
  if (typeof(obj) != 'undefined' && obj != null) {
    return true;
  }
  else {
    return false;
  }
};
