module.exports = {
    assets: {
        files: [
            {
                expand: true,
                dot: true,
                cwd: '<%= coreDir %>',
                dest: '<%= distDir %>',
                src: [
                    'fonts/*',
                    'images/**/*',
                    'scripts/**/*.{css,jpg,jpeg,png,gif,svg,json}'
                ]
            },
            {
                expand: true,
                dot: true,
                cwd: '<%= appDir %>',
                dest: '<%= distDir %>',
                src: [
                    'fonts/*',
                    'images/**/*',
                    'styles/css/*.css',
                    'scripts/**/*.{html,css,jpg,jpeg,png,gif,svg,json}'
                ]
            }
        ]
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
                'fonts/sd_icons.woff',
                'fonts/sd_icons.ttf',
                'scripts/vendor.js',
                'scripts/superdesk-core.js',
                'scripts/templates-cache.js',
                'scripts/superdesk-apps.js',
                'scripts/vendor-docs.js',
                'scripts/superdesk-docs-core.js',
                'scripts/superdesk-docs-main.js'
            ]
        }]
    }
};
