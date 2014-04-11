

module.exports = function(grunt) {
    'use strict';

    var _ = require('lodash'),
        path = require('path');

    function getModules() {
        var pattern = grunt.template.process('<%= appDir %>/scripts/superdesk-*/module.js');
        return _.map(grunt.file.expand(pattern), function(modulePath) {
            return path.basename(path.dirname(modulePath)) + '/module';
        });
    }

    var include = [
        'main',
        'superdesk/filters/all',
        'superdesk/services/all',
        'superdesk/directives/all',
        'superdesk/auth/auth',
        'superdesk/data/data',
        'superdesk/datetime/datetime',
        'superdesk/error/error',
    ];

    include.push.apply(include, getModules());

    return {
        compile: {
            options: {
                name: 'main',
                out: '<%= distDir %>/scripts/main.js',
                baseUrl: '<%= appDir %>/scripts/',
                mainConfigFile: '<%= appDir %>/scripts/config.js',
                include: include
            }
        }
    };
};
