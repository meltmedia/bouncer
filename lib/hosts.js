var _ = require('underscore'),
    step = require('step'),
    winston = require('winston');

_.str = require('underscore.string');

// Utils
function isDefined(obj) {
  if (typeof(obj) != 'undefined' && obj != null) {
    return true;
  }
  else {
    return false;
  }
};

var hosts = {
  ips: [],
  endpoints: [],
  home: null,
  whitelist: [],

  setWhitelist: function(whitelist) {
    if (_.isArray(whitelist)) {
      hosts.whitelist = whitelist;
    }
  },

  setHome: function(home) {
    hosts.home = home;
  },

  addEndpoint: function(endpoint) {
    hosts.endpoints.push(endpoint);
  },

  getAddress: function(instance) {
    if (_.str.startsWith(instance["placement"]["availabilityZone"], hosts.home)) {
      return instance["privateIpAddress"];
    }
    else {
      return instance["ipAddress"];
    }
  },

  getRegion: function(instance) {
    return instance["placement"]["availabilityZone"]
  },

  allow: function(address) {
    if (_.indexOf(hosts.ips, address) != -1) {
      return true;
    }

    return false;
  },

  load: function(callback) {
    var addresses = [];
    step(
      function start() {
        hosts.whitelist.forEach(function(address) {
          addresses.push(address);
        });

        var group = this.group();
        hosts.endpoints.forEach(function (endpoint) {
          endpoint.call("DescribeInstances", {}, group());
        });
      },
      function parse(err, results) {
        if (err) {
          callback(err);
          return;
        }
        else {
          results.forEach(function(result) {
            var i = 0;
            var region = null;
          
            result["reservationSet"]["item"].forEach(function(instance) {
              if (region == null) {
                region = hosts.getRegion(instance["instancesSet"]["item"]).slice(0, -1);
              }

              var address = hosts.getAddress(instance["instancesSet"]["item"]);

              if (isDefined(address)) {
                i++;
                addresses.push(address);
              }
            });

            winston.debug("loaded " + i + " from " + region);
          });

          hosts.ips = addresses;
          callback(null, addresses);
        }
      }
    );
  }
};

module.exports = hosts;
