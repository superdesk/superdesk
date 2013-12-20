module.exports = {
    options: {
        port: 9000,
        hostname: 'localhost',
        livereload: '<%= livereloadPort %>'
    },
    server: {
        options: {
            base: [
                '<%= distDir %>',
                '<%= tmpDir %>',
                '<%= appDir %>'
            ]
        }
    }
};
