var _ = require('underscore'),
    step = require('step');

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
        addresses.push("127.0.0.1");
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
          var i = 0;
          results.forEach(function(result) {
            result["reservationSet"]["item"].forEach(function(instance) {
              i++;
              var address = hosts.getAddress(instance["instancesSet"]["item"]);

              if (isDefined(address)) {
                addresses.push(address);
              }
            })
          })
          hosts.ips = addresses;
          callback(null);
        }
      }
    );
  }
};

module.exports = hosts;
