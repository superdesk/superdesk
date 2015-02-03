module.exports = {
    assets: {
        files: [{
            expand: true,
            dot: true,
            cwd: '<%= appDir %>',
            dest: '<%= distDir %>',
            src: [
                'images/**/*',
                'styles/css/*.css',
                'scripts/**/*.{html,css,jpg,jpeg,png,gif,json}',
                'scripts/bower_components/requirejs/require.js'
            ]
        }]
    },
    js: {
        files: [{
            expand: true,
            dot: true,
            cwd: '<%= appDir %>',
            dest: '<%= distDir %>',
            src: [
                'scripts/config.js',
                'scripts/bower_components/**/*.js'
            ]
        }]
    },
    bower: {
        files: [{
            expand: true,
            dot: true,
            cwd: '<%= distDir %>',
            dest: '<%= bowerDir %>',
            src: [
                'images/**',
                'styles/css/bootstrap.css',
                'styles/css/app.css',
                'scripts/vendor.js',
                'scripts/superdesk-core.js',
                'scripts/superdesk.js'
            ]
        }]
    }
};
