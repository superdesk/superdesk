'use strict';
var config = require('./protractor-conf.js');
config.specs = ['spec/**/[a-f]*[Ss]pec.js'];
exports.config = config;
