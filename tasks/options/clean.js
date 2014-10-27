module.exports = {
    dist: {
        files: [{
            dot: true,
            src: [
                '<%= tmpDir %>',
                '<%= distDir %>/*.*',
                '<%= distDir %>/template/**',
                '<%= distDir %>/scripts/*.*',
                '<%= distDir %>/scripts/**/*',
                '!<%= distDir %>/scripts/superdesk-core.js',
                '!<%= distDir %>/scripts/vendor.js',
                '<%= distDir %>/styles/css/*.*',
                '!<%= distDir %>/styles/css/app.css',
                '!<%= distDir %>/styles/css/bootstrap.css',
                '!<%= distDir %>/.git*'
            ]
        }]
    },
    server: {
        files: [{
            src: [
                '<%= tmpDir %>'
            ]
        }]
    }
};
