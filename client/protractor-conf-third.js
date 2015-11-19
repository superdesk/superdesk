'use strict';
var config = require('./protractor-conf-base.js');
config.specs = ['spec/**/[n-z]*[Ss]pec.js'];
exports.config = config;
