
module.exports = function(grunt) {
    'use strict';

    var base = ['<%= distDir %>', '<%= tmpDir %>', '<%= appDir %>'];

    return {
        options: {
            port: 9000,
            livereload: '<%= livereloadPort %>'
        },
        test: {options: {base: base}},
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
