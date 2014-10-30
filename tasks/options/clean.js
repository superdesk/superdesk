module.exports = {
    dist: {
        files: [{
            dot: true,
            src: [
                '<%= tmpDir %>',
                '<%= serverDir %>/*',
                '!<%= serverDir %>/.git*'
            ]
        }]
    },
    server: {
        files: '<%= tmpDir %>'
    }
};
