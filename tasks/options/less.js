module.exports = {
    development: {
        options: {
            paths: ['<%= appDir %>/styles/less'],
            compress: true,
            cleancss: true
        },
        files: {
            '<%= distDir %>/styles/css/bootstrap.css': '<%= appDir %>/styles/less/bootstrap.less'
        }
    },
    production: {
        options: {
            paths: ['<%= appDir %>/styles/less'],
        },
        files: {
            '<%= distDir %>/styles/css/bootstrap.css': '<%= appDir %>/styles/less/bootstrap.less'
        }
    }
};
