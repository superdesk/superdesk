module.exports = {
    assets: {
        files: [{
            expand: true,
            dot: true,
            dest: '<%= distDir %>',
            src: [
                '<%= appDir %>/images/**/*',
                '<%= appDir %>/styles/css/*.css',
                '<%= appDir %>/scripts/**/*.{html,css,jpg,jpeg,png,gif,json}',
                '<%= appDir %>/template/**/*.html',
                '<%= appDir %>/scripts/bower_components/requirejs/require.js'
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
