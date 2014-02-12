'use strict';

module.exports = function (grunt) {

    var config = {
        pkg: grunt.file.readJSON('./package.json'),
        appDir: 'app',
        tmpDir: '.tmp',
        distDir: 'dist',
        poDir: 'po',
        livereloadPort: 35729,
        serverURL: grunt.option('server') || 'http://localhost:5000'
    };

    require('load-grunt-tasks')(grunt);
    require('load-grunt-config')(grunt, {
        config: config,
        configPath: require('path').join(process.cwd(), 'tasks', 'options'),
        init: true
    });

    grunt.registerTask('server', [
        'clean',
        'less:development',
        'template',
        'connect:server',
        'open',
        'watch'
    ]);

    grunt.registerTask('test', [
        'clean:server',
        'karma',
        'jshint',
        'jscs'
    ]);

    grunt.registerTask('build', [
        'clean:dist',
        'jshint',
        'less:production',
        'template',
        'nggettext_compile',
        'requirejs',
        'copy:assets',
        'clean:tmp'
    ]);

    grunt.registerTask('default', 'build');
    grunt.registerTask('package', 'build compress');
};
