'use strict';
var config = require('./protractor-conf.js');
config.specs = ['spec/**/[n-z]*[Ss]pec.js'];
exports.config = config;
