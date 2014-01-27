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
    components: {
        files: [{
            expand: true,
            dot: true,
            cwd: '<%= appDir %>',
            dest: '<%= tmpDir %>',
            src: [
                'scripts/bower_components/**/*.js'
            ]
        }]
    }
};
