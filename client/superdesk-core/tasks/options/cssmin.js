
module.exports = {
    target: {
        files: {
            '<%= distDir %>/styles/css/docs.css': ['<%= tmpDir %>/docs/styles/*.css']
        }
    }
};
