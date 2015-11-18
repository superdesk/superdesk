'use strict';
var config = require('./protractor-conf.js');
config.specs = ['spec/**/[g-m]*[Ss]pec.js'];
exports.config = config;
