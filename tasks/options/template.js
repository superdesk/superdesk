module.exports = function(grunt) {

    'use strict';

    function data(url, forceUrl) {

        var server = grunt.option('server') || process.env.SUPERDESK_URL || url;
        var ws = grunt.option('ws') || process.env.SUPERDESK_WS_URL || 'ws://localhost:5100';

        if (forceUrl) {
            server = url;
        }

        var config = {
            raven: {dsn: process.env.SUPERDESK_RAVEN_DSN || ''},
            server: {url: server, ws: ws},
            analytics: {
                piwik: {
                    url: process.env.PIWIK_URL || '',
                    id: process.env.PIWIK_SITE_ID || ''
                },
                ga: {
                    id: process.env.TRACKING_ID || ''
                }
            },
            strictDi: /localhost/.test(server)
        };

        return {data: {config: config}};
    }

    var files = {'<%= distDir %>/index.html': '<%= appDir %>/index.html'};
    var APIARY_URL = process.env.APIARY_URL || 'http://superdesk.apiary.io';

    return {
        mock: {
            options: data(APIARY_URL, true),
            files: files
        },
        test: {
            options: data('https://master.sd-test.sourcefabric.org/api'),
            files: files
        }
    };
};
