module.exports = function(grunt) {

    'use strict';

    function data(url) {
        var config = {
            raven: {dsn: process.env.SUPERDESK_RAVEN_DSN || ''},
            server: {url: grunt.option('server') || url},
            analytics: {
                piwik: {
                    url: process.env.PIWIK_URL || '',
                    id: process.env.PIWIK_SITE_ID || ''
                },
                ga: {
                    id: process.env.TRACKING_ID || ''
                }
            }
        };

        return {data: {config: config}};
    }

    var files = {'<%= distDir %>/index.html': '<%= appDir %>/index.html'};

    return {
        mock: {
            options: data('http://superdesk.apiary.io'),
            files: files
        },
        test: {
            options: data('https://apytest.apy.sd-test.sourcefabric.org/api'),
            files: files
        }
    };
};
