'use strict';
var config = require('./protractor-conf.js');
config.config.specs = [require('path').join(__dirname, 'node_modules/superdesk-core/spec/**/[a-f]*[Ss]pec.js')];
exports.config = config.config;
