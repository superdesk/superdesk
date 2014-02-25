module.exports = {
    dev: {
        options: {
            paths: ['<%= appDir %>/styles/less'],
            compress: false,
            cleancss: true
        },
        files: {
            '<%= distDir %>/styles/css/bootstrap.css': '<%= appDir %>/styles/less/bootstrap.less'
        }
    },
    prod: {
        options: {
            paths: ['<%= appDir %>/styles/less'],
            compress: true,
            cleancss: true
        },
        files: {
            '<%= distDir %>/styles/css/bootstrap.css': '<%= appDir %>/styles/less/bootstrap.less'
        }
    }
};
