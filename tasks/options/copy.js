module.exports = {
    assets: {
        files: [{
            expand: true,
            dot: true,
            cwd: '<%= appDir %>',
            dest: '<%= distDir %>',
            src: [
                '.htaccess',
                '*.{ico,txt}',
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
            dest: '<%= distDir %>',
            src: [
                'scripts/config.js',
                'scripts/bower_components/**/*.js'
            ]
        }]
    }
};
