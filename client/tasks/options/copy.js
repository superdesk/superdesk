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
                'scripts/**/*.{html,css,jpg,jpeg,png,gif,svg,json}',
                'scripts/bower_components/requirejs/require.js'
            ]
        }]
    },
    docs: {
        files: [{
            expand: true,
            dot: true,
            cwd: '<%= appDir %>/docs',
            dest: '<%= distDir %>',
            src: [
                'views/**/*.{html,css,jpg,jpeg,png,gif,svg,json}'
            ]
        },
        {
            expand: true,
            dot: true,
            cwd: '<%= appDir %>',
            dest: '<%= distDir %>',
            src: [
                'docs/images/**/*.{jpg,jpeg,png,gif,svg}'
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
                'scripts/templates-cache.js',
                'scripts/superdesk.js',
                'scripts/vendor-docs.js',
                'scripts/superdesk-docs-core.js',
                'scripts/superdesk-docs-main.js'
            ]
        }]
    }
};
