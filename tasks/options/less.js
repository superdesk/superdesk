module.exports = {
    dev: {
        options: {
            paths: [
                '<%= appDir %>/styles/less',
                '<%= appDir %>/scripts/superdesk-users/styles'
                ],
            compress: false,
            cleancss: true
        },
        files: {
            '<%= distDir %>/styles/css/bootstrap.css': '<%= appDir %>/styles/less/bootstrap.less',
            '<%= distDir %>/styles/css/users.css': '<%= appDir %>/scripts/superdesk-users/styles/styles.less',
        }
    },
    prod: {
        options: {
            paths: ['<%= appDir %>/styles/less','<%= appDir %>/scripts/superdesk-users/styles'],
            compress: true,
            cleancss: true
        },
        files: {
            '<%= distDir %>/styles/css/bootstrap.css': '<%= appDir %>/styles/less/bootstrap.less',
            '<%= distDir %>/styles/css/users.css': '<%= appDir %>/scripts/superdesk-users/styles/styles.less',
        }
    }
};
