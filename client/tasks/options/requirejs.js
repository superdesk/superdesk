
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

    var include = ['main'];
    include.push.apply(include, getModules());

    return {
        compile: {
            options: {
                name: 'main',
                baseUrl: '<%= appDir %>/scripts/',
                out: '<%= tmpDir %>/concat/scripts/main.js',
                mainConfigFile: '<%= appDir %>/scripts/config.js',
                include: include,
                optimize: 'none'
            }
        }
    };
};
