module.exports = {
    dev: {
        options: {
            paths: [
                '<%= appDir %>/styles/less'
                ],
            compress: false,
            cleancss: true
        },
        files: {
            '<%= distDir %>/styles/css/bootstrap.css': '<%= appDir %>/styles/less/bootstrap.less',
            '<%= distDir %>/styles/css/users.css': '<%= appDir %>/scripts/superdesk-users/styles/users.less',
            '<%= distDir %>/styles/css/dashboard.css': '<%= appDir %>/scripts/superdesk-dashboard/styles/dashboard.less'
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
            '<%= distDir %>/styles/css/users.css': '<%= appDir %>/scripts/superdesk-users/styles/users.less',
            '<%= distDir %>/styles/css/dashboard.css': '<%= appDir %>/scripts/superdesk-dashboard/styles/dashboard.less'
        }
    }
};
