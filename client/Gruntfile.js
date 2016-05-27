'use strict';

module.exports = function(grunt) {
    require('superdesk-core/Gruntfile')(grunt);

    grunt.loadNpmTasks('grunt-connect-proxy');

    var middlewareConfig = grunt.config('connect.test.options.middleware');
    grunt.config('connect.test.options.middleware', function(connect, options, middlewares) {
        middlewares.push(require('grunt-connect-proxy/lib/utils').proxyRequest);
        middlewareConfig(connect, options, middlewares);
        return middlewares;
    });

    grunt.config('connect.proxies', [
        {
            context: '/tansaclient',
            host: 'd02.tansademo.net',
            changeOrigin: true,
            port: 8080
        }
    ]);

    grunt.registerTask('server', [
        'clean',
        'style',
        'template:test',
        'configureProxies:test',
        'connect:test',
        'watch'
    ]);
};
