'use strict';

module.exports = function (grunt) {

    var config = {
        pkg: grunt.file.readJSON('./package.json'),
        appDir: 'app',
        tmpDir: '.tmp',
        distDir: 'dist',
        poDir: 'po',
        livereloadPort: 35729
    };

    require('load-grunt-tasks')(grunt);
    require('load-grunt-config')(grunt, {
        config: config,
        configPath: require('path').join(process.cwd(), 'tasks', 'options'),
        init: true
    });

    grunt.registerTask('test', ['karma']);
    grunt.registerTask('hint', ['jshint', 'jscs']);
    grunt.registerTask('ci', ['test', 'hint']);
    grunt.registerTask('server', ['clean', 'less:dev', 'template', 'connect:dev', 'open', 'watch']);
    grunt.registerTask('server:e2e', ['clean', 'less:dev', 'template', 'connect:test']);
    grunt.registerTask('build', ['clean', 'less:prod', 'template', 'nggettext_compile', 'requirejs', 'copy:assets']);
    grunt.registerTask('package', ['ci', 'build']);
    grunt.registerTask('default', ['server']);
};
