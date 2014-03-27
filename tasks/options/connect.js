
module.exports = function(grunt) {
    var base = ['<%= distDir %>', '<%= tmpDir %>', '<%= appDir %>'];
    return {
        options: {
            port: 9000,
            hostname: 'localhost',
            livereload: '<%= livereloadPort %>'
        },
        dev: {options: {base: base}},
        mock: {
            options: {
                base: base,
                port: 9001
            }
        },
        test: {
            options: {
                base: base,
                keepalive: true,
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
