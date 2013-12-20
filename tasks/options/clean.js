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
    tmp: {
        files: [{
            dot: true,
            src: ['<%= tmpDir %>']
        }]
    }
};
