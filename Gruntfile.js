'use strict';

module.exports = function (grunt) {

    // util for grunt.template
    grunt.toJSON = function(input) {
        return JSON.stringify(input);
    };

    var config = {
        pkg: grunt.file.readJSON('./package.json'),
        appDir: 'app',
        tmpDir: '.tmp',
        distDir: 'dist',
        poDir: 'po',
        livereloadPort: 35729
    };

    grunt.initConfig(config);

    require('load-grunt-tasks')(grunt);
    require('load-grunt-config')(grunt, {
        config: config,
        configPath: require('path').join(process.cwd(), 'tasks', 'options')
    });

    grunt.registerTask('style', ['less:dev', 'cssmin']);

    grunt.registerTask('test', ['karma:unit']);
    grunt.registerTask('hint', ['jshint', 'jscs']);
    grunt.registerTask('ci', ['test', 'hint']);
    grunt.registerTask('ci:travis', ['karma:travis', 'hint']);
    grunt.registerTask('bamboo', ['karma:bamboo']);

    grunt.registerTask('server', ['clean', 'style', 'template:test', 'connect:dev', 'open:test', 'watch']);
    grunt.registerTask('server:mock', ['clean', 'style', 'template:mock', 'connect:mock', 'open:mock', 'watch']);
    grunt.registerTask('server:e2e', ['clean', 'style', 'template:mock', 'connect:test', 'watch']);

    grunt.registerTask('build', [
        'clean',
        'style',
        'template:test',
        'nggettext_compile',
        'requirejs',
        'copy',
        'filerev',
        'usemin'
    ]);

    grunt.registerTask('package', ['ci', 'build']);
    grunt.registerTask('default', ['server']);
};
