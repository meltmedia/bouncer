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
    config = require('konphyg')(__dirname + '/config'),
    hosts = require('./lib/hosts');

_.str = require('underscore.string');

var app = express();

var awsConfig = config('aws');

app.listen(4010);
winston.info("Server started on 4010")

// set the "home" region
hosts.setHome("us-east-1");
// Add us-east-1
hosts.addEndpoint(aws.createEC2Client(awsConfig.id, awsConfig.key));
// Add us-west-1
hosts.addEndpoint(aws.createEC2Client(awsConfig.id, awsConfig.key, {host: awsConfig["us-west-1"]}))

app.use(express.logger({stream:winstonStream}));
app.use(express.static(__dirname + '/public'));

app.all('*', function(req, res, next) {
  winston.debug("* check for ip/group for " + req.ip + " in " + hosts.ips.length);
  if (hosts.allow(req.ip)) {
    next();
  }
  else {
    hosts.load(function(err) {
      if (err) {
        res.send(500, "unable to update allowed hosts");
        return;
      }
      
      winston.info("** checking ip " + req.ip + " against " + hosts.ips.length);
      
      if (hosts.allow(req.ip)) {
        next();
      }
      else {
        res.send(403, "you are not from ec2");
      }
    })
  }
});

app.get("/", function(req, res){
  res.send('200', "welcome to the machine");
});

app.get("/hosts", function(req, res) {
  res.send('200', hosts.ips);
});

app.get("/reload", function(req, res) {
  hosts.load(function(err) {
    if (err) {
      res.send(500, err);
      return;
    }

    res.send(200, hosts.ips);
  });
});

hosts.load(function(err) {
  if (!err) {
    winston.debug("loaded hosts: " + hosts.ips.length);
  }
});
