'use strict';
var config = require('./protractor-conf.js');
config.config.specs = ['./node_modules/superdesk-core/spec/**/[g-m]*[Ss]pec.js'];
exports.config = config.config;
