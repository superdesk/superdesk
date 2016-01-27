
module.exports = function(grunt) {
    'use strict';

    var base = ['<%= distDir %>', '<%= tmpDir %>', '<%= appDir %>'];

    return {
        options: {
            port: 9000,
            livereload: '<%= livereloadPort %>'
        },
        test: {
            options: {
                base: base,
                middleware: function(connect, options, middlewares) {
                    middlewares.unshift(mockTemplates);
                    return middlewares;

                    // avoid 404 in dev server for templates
                    function mockTemplates(req, res, next) {
                        if (req.url === '/scripts/templates-cache.js') {
                            return res.end('');
                        } else {
                            return next();
                        }
                    }
                }
            }
        },
        travis: {
            options: {
                base: base,
                keepalive: true,
                livereload: false,
                port: 9000
            }
        },
        mock: {
            options: {
                base: base,
                keepalive: true,
                livereload: false,
                port: 9090
            }
        },
        build: {
            options: {
                base: ['<%= distDir %>'],
                port: 9090,
                livereload: false,
                keepalive: true
            }
        }
    };
};
