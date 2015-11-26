'use strict';
var config = require('./protractor-conf-base.js');
config.specs = ['spec/**/[g-m]*[Ss]pec.js'];
exports.config = config;
