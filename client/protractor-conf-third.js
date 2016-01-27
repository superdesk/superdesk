'use strict';
var config = require('./protractor-conf.js');
config.config.specs = ['./node_modules/superdesk-core/spec/**/[n-z]*[Ss]pec.js'];
exports.config = config.config;
