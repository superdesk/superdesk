module.exports = {
    dist: {
        files: [{
            dot: true,
            src: [
                '<%= tmpDir %>',
                '<%= distDir %>/*',
                '!<%= distDir %>/.git*'
            ]
        }]
    },
    server: {
        files: '<%= tmpDir %>'
    },
    bower: {
        files: [{
            src: [
                '<%= bowerDir %>/scripts/templates-cache.js',
                '<%= bowerDir %>/scripts/superdesk.js',
            ]
        }]
    }
};
