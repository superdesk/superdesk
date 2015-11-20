'use strict';
var config = require('./protractor-conf-base.js');
config.specs = ['spec/**/[a-f]*[Ss]pec.js'];
exports.config = config;
