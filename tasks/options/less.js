module.exports = {
    development: {
        options: {
            paths: ['<%= appDir %>/styles/less'],
            yuicompress: true
        },
        files: {
            '<%= distDir %>/styles/css/bootstrap.css': '<%= appDir %>/styles/less/bootstrap.less'
        }
    }
};
