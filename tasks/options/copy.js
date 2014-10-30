module.exports = {
    assets: {
        files: [{
            expand: true,
            dot: true,
            cwd: '<%= appDir %>',
            dest: '<%= serverDir %>',
            src: [
                'images/**/*',
                'styles/css/*.css',
                'scripts/**/*.{html,css,jpg,jpeg,png,gif,json}',
                'template/**/*.html',
                'scripts/bower_components/requirejs/require.js'
            ]
        }]
    },
    js: {
        files: [{
            expand: true,
            dot: true,
            cwd: '<%= appDir %>',
            dest: '<%= serverDir %>',
            src: [
                'scripts/config.js',
                'scripts/bower_components/**/*.js'
            ]
        }]
    },
    dist: {
        files: [{
            expand: true,
            dot: true,
            cwd: '<%= serverDir %>',
            dest: '<%= distDir %>',
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
