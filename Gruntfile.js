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

    grunt.registerTask('ci', ['jshint', 'jscs']);
    grunt.registerTask('server:test', ['clean', 'less:dev', 'template:test', 'connect:test']);
    grunt.registerTask('server', ['clean', 'less:dev', 'template:dev', 'connect:dev', 'open', 'watch']);
    grunt.registerTask('test', ['clean:server', 'karma']);
    grunt.registerTask('build', ['clean:dist', 'less:prod', 'template:prod', 'nggettext_compile', 'requirejs', 'copy:assets']);
    grunt.registerTask('package', ['ci', 'build']);
    grunt.registerTask('default', ['server']);
};
