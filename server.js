// Config and logging need to be done first to allow logging
// to work early, and to configure the logging
var konphyg = require('konphyg')(__dirname + '/config'),
    winston = require('winston');

var config = konphyg.all();

// Use syslog levels so debug is at the bottom
winston.setLevels(winston.config.syslog.levels);
// remove the default console transport
winston.remove(winston.transports.Console);

// if an output file is specified, use it
if (config.log.out) {
  winston.add(winston.transports.File, { filename: config.log.out, json: false, timestamp: true });
}

// if stdout is enable add the console logger back
if (config.log.stdout) {
  winston.add(winston.transports.Console, {colorize: config.log.colorize, timestamp: true, level: config.log.level});
}

// configure the access logger
var access_log = winston;
// if there is a log file specified for access, configure it
if (config.log.access) {
  winston.loggers.add('access', {
    file: {
      filename: config.log.access,
      timestamp: true,
      level: 'debug',
      json: false
    }
  });

  access_log = winston.loggers.get('access');
  access_log.remove(winston.transports.Console);
}

// Add a stream for express to use, this is backed by the access logger
var winstonStream = {
  write: function(message, encoding) {
    access_log.debug(message);
  }
};

// Normal app configuration begins
var express = require('express'),
    https = require('https'),
    http = require('http'),
    _ = require('underscore'),
    aws = require('aws-lib'),
    step = require('step'),
    fs = require('fs'),
    hosts = require('./lib/hosts');

_.str = require('underscore.string');

var app = express();

// set the reload interval || default 5
var reload_interval = config.server.reload_interval || 5;

// if requests are proxied use the upstream IP
if (config.server.proxy) {
  app.enable('trust proxy');
  winston.info("enabling trusted proxy");
}

// if https is enabled, configure it
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

// if http is enabled, configure it
if (isDefined(config.server.http)) {
  app.listen(config.server.http);
  winston.info("Server started on " + config.server.http);
}

// if there are no content folders specified, set a default
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

// re-load all hosts every n minutes (converted to millis)
winston.debug("starting timer to reload hosts every " + reload_interval + " minutes");
setInterval(loadHosts, (reload_interval * 60 * 1000));

// initial population of known addresses
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

// Callback method for loading hosts that only logs
function loadHosts() {
  hosts.load(function(err) {
    if (!err) {
      winston.debug("loaded hosts: " + hosts.ips.length);
    }
  });
};

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
