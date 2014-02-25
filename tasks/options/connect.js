
module.exports = function(grunt) {
    var base = ['<%= distDir %>', '<%= tmpDir %>', '<%= appDir %>'];
    return {
        options: {
            port: 9000,
            hostname: 'localhost',
            livereload: '<%= livereloadPort %>'
        },
        dev: {options: {base: base}},
        test: {
            options: {
                base: base,
                keepalive: true,
                port: 9090
            }
        }
    };
};
