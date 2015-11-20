
module.exports = function(grunt) {
    'use strict';

    var path = require('path');

    function getModules() {
        var pattern = grunt.template.process('<%= appDir %>/scripts/superdesk-*/module.js');
        return grunt.file.expand(pattern).map(function(modulePath) {
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
                mainConfigFile: '<%= appDir %>/scripts/config.js',
                out: '<%= tmpDir %>/concat/scripts/main.js',
                optimize: 'none',
                include: include
            }
        },
        compileBowerSuperdesk: {
            options: {
                name: 'superdesk/superdesk',
                baseUrl: '<%= appDir %>/scripts/',
                mainConfigFile: '<%= appDir %>/scripts/config.js',
                out: '<%= bowerDir %>/scripts/superdesk.js',
                optimize: 'none',
                include: ['superdesk/superdesk']
            }
        },
        compileBowerSettings: {
            options: {
                name: 'superdesk-settings/module',
                baseUrl: '<%= appDir %>/scripts/',
                mainConfigFile: '<%= appDir %>/scripts/config.js',
                out: '<%= bowerDir %>/scripts/superdesk-settings.js',
                optimize: 'none',
                include: ['superdesk-settings/module']
            }
        },
        compileBowerDashboard: {
            options: {
                name: 'superdesk-dashboard/module',
                baseUrl: '<%= appDir %>/scripts/',
                mainConfigFile: '<%= appDir %>/scripts/config.js',
                out: '<%= bowerDir %>/scripts/superdesk-dashboard.js',
                optimize: 'none',
                include: ['superdesk-dashboard/module']
            }
        },
        compileBowerArchive: {
            options: {
                name: 'superdesk-archive/module',
                baseUrl: '<%= appDir %>/scripts/',
                mainConfigFile: '<%= appDir %>/scripts/config.js',
                out: '<%= bowerDir %>/scripts/superdesk-archive.js',
                optimize: 'none',
                include: ['superdesk-archive/module']
            }
        },
        compileBowerIngest: {
            options: {
                name: 'superdesk-ingest/module',
                baseUrl: '<%= appDir %>/scripts/',
                mainConfigFile: '<%= appDir %>/scripts/config.js',
                out: '<%= bowerDir %>/scripts/superdesk-ingest.js',
                optimize: 'none',
                include: ['superdesk-ingest/module']
            }
        },
        compileDocs: {
            options: {
                name: 'superdesk/superdesk-docs',
                baseUrl: '<%= appDir %>/scripts/',
                mainConfigFile: '<%= appDir %>/scripts/config.js',
                out: '<%= tmpDir %>/concat/scripts/superdesk-docs-main.js',
                optimize: 'none',
                include: ['superdesk/superdesk-docs']
            }
        }
    };
};
