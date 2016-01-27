
module.exports = {
    target: {
        files: {
            '<%= distDir %>/styles/css/app.css': ['<%= tmpDir %>/**/*.css'],
            '<%= distDir %>/styles/css/docs.css': ['<%= tmpDir %>/docs/styles/*.css']
        }
    }
};
