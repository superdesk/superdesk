module.exports = function(grunt) {

    function data(url) {
        return {data: {
            raven: {
                dsn: process.env['SUPERDESK_RAVEN_DSN']
            },
            server: {url: grunt.option('server') || url}}
        };
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
