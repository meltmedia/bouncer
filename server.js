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
    https = require('https'),
    http = require('http'),
    _ = require('underscore'),
    aws = require('aws-lib'),
    step = require('step'),
    fs = require('fs'),
    konphyg = require('konphyg')(__dirname + '/config'),
    hosts = require('./lib/hosts');

_.str = require('underscore.string');

var config = konphyg.all();

var app = express();

if (isDefined(config.server.https)) {
  try {
    https.createServer(opencerts(config.server.ssl_options), app).listen(config.server.https);
    test_ssl(config, function(err) {
      if (err) {
        throw err;
      }
      winston.info("SSL Server started on " + config.server.https);
    });
  }
  catch (ex) {
    winston.error("unable to bring up ssl server: " + ex);
  }
}

if (isDefined(config.server.http)) {
  app.listen(config.server.http);
  winston.info("Server started on " + config.server.http);
}

if (!isDefined(config.server.public)) {
  config.server.public = [{ "context": "/", "path": __dirname + "/public" }]
}

// set the "home" region
hosts.setHome(config.server.home);

// set the whitelisted ip's
hosts.setWhitelist(config.server.whitelist);

// add all regions for each account
config.aws.accounts.forEach( function(account) {
  account.active.forEach( function(region) {
    hosts.addEndpoint(
      aws.createEC2Client(
        account.id, 
        account.key, 
        { host: config.aws.regions[region] }
      )
    );
  });
});

// Configure winston as the logger for express
app.use(express.logger({stream:winstonStream}));

// set the directories to server files from
config.server.public.forEach(function(pub) {
  try {
    app.use(pub.context, express.static(pub.path));
    winston.debug("[mount] " + pub.context + " serving " + pub.path);
  }
  catch (ex) {
    winston.error("[mount] unable to mount " + pub.context + " with path " + pub.path);    
  }
});

// Authentication mechanism for all requests
app.all('*', function(req, res, next) {
  winston.debug("* check for ip/group for " + req.ip + " in " + hosts.ips.length);
  // check if the requesters ip is allowed
  if (hosts.allow(req.ip)) {
    next();
  }
  else {
    /* 
      if the requester ip address was not found, 
      reload IP addresses (in case it is a new instance)
    */
    hosts.load(function(err) {
      if (err) {
        // an error occurred while reloading the address list
        res.send(500, "unable to update allowed hosts");
        return;
      }
      
      winston.debug("** checking ip " + req.ip + " against " + hosts.ips.length);
      
      // recheck against the allowed addresses
      if (hosts.allow(req.ip)) {
        next();
      }
      else {
        // the address was still not allowed, send forbidden
        res.send(403, "you are not from ec2");
      }
    })
  }
});

// respond with a list of known addresses
app.get("/system/hosts", function(req, res) {
  res.send('200', hosts.ips);
});

// reload the list of known addresses
app.get("/system/reload", function(req, res) {
  hosts.load(function(err) {
    if (err) {
      res.send(500, err);
      return;
    }

    res.send(200, hosts.ips);
  });
});

// initial population of known addresses
function loadHosts() {
  hosts.load(function(err) {
    if (!err) {
      winston.debug("loaded hosts: " + hosts.ips.length);
    }
  });
};

setInterval(loadHosts, (5 * 60 * 1000));

loadHosts();

// Utils
// simplify checking if a variable is defined
function isDefined(obj) {
  if (typeof(obj) != 'undefined' && obj != null) {
    return true;
  }
  else {
    return false;
  }
}

// Test the https endpoint, for now this is purely informative
function test_ssl(options, callback) {
  winston.info("[https_test] testing https server");
  https.get('https://localhost:' + options.server.https + "/", function(res) {
    winston.info("[https_test] got a " + res.statusCode + " from the https server");
    callback();
  }).on('error', function(e) {
    winston.error("[https_test] unable to connect to https server: " + e);
    callback(e);
  });
}

// Open the certificates used for https, safe gaurds are 
// in place to allow calling this method more than once.
function opencerts(options) {
  if (isDefined(options.cert) && _.isString(options.cert)) {
    options.cert = fs.readFileSync(options.cert);
  }

  if (isDefined(options.key) && _.isString(options.key)) {
    options.key = fs.readFileSync(options.key);
  }

  if (isDefined(options.ca)) {
    cas = [];
    if (_.isArray(options.ca)) {
      options.ca.forEach(function(ca) {
        if (_.isString(ca)) {
          cas.push(fs.readFileSync(ca));
        }
      })
    } else if (_.isString(options.ca)) {
      cas.push(fs.readFileSync(options.ca));
    }

    if (cas.length > 0) {
      options.ca = cas;
    }
  }

  return options;
}
