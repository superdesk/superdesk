module.exports = {
    options: {
        data: {
            server: {
                url: '<%= serverURL %>'
            }
        }
    },
    build: {
        files: {
            '<%= distDir %>/index.html': '<%= appDir %>/index.html'
        }
    }
};
