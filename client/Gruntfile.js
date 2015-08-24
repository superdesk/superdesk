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
        specDir: 'spec',
        tasksDir: 'tasks',
        bowerDir: 'bower',
        poDir: 'po',
        livereloadPort: 35729,
        ngtemplates: {
            app: {
                cwd: 'app',
                src: 'scripts/superdesk*/**/*.html',
                dest: 'app/scripts/templates.js',
                options: {
                    htmlmin: {
                        collapseWhitespace: true,
                        collapseBooleanAttributes: true
                    },
                    bootstrap: function(module, script) {
                        return '"use strict";' +
                            'var templates = angular.module("templates", []);' +
                            'templates.run([\'$templateCache\', function($templateCache) {' +
                            script + ' }]);';
                    }
                }
            }
        }
    };

    grunt.initConfig(config);

    require('load-grunt-tasks')(grunt);
    require('load-grunt-config')(grunt, {
        config: config,
        configPath: require('path').join(process.cwd(), 'tasks', 'options')
    });

    // automatically minify and cache HTML templates into $templateCache
    grunt.loadNpmTasks('grunt-angular-templates');

    grunt.registerTask('style', ['less:dev', 'cssmin']);

    grunt.registerTask('test', ['karma:unit']);
    grunt.registerTask('hint', ['jshint', 'jscs', 'eslint:specs', 'eslint:tasks', 'eslint:root']);
    grunt.registerTask('hint:docs', ['jshint:docs', 'jscs:docs']);
    grunt.registerTask('ci', ['test', 'hint']);
    grunt.registerTask('ci:travis', ['karma:travis', 'hint']);
    grunt.registerTask('bamboo', ['karma:bamboo']);

    grunt.registerTask('docs', [
        'clean',
        'less:docs',
        'cssmin',
        'template:docs',
        'connect:test',
        'open:docs',
        'ngtemplates',
        'watch'
    ]);

    grunt.registerTask('server', [
        'clean',
        'style',
        'template:test',
        'connect:test',
        'open:test',
        'ngtemplates',
        'watch'
    ]);
    grunt.registerTask('server:e2e', [
        'clean',
        'style',
        'template:mock',
        'connect:mock',
        'ngtemplates',
        'watch'
    ]);
    grunt.registerTask('server:travis', ['clean', 'style', 'template:travis', 'connect:travis']);

    grunt.registerTask('bower', [
        'build',
        'copy:bower'
    ]);
    grunt.registerTask('build', [
        'clean',
        'less:dev',
        'useminPrepare',
        'concat',
        'requirejs', // must go after concat
        'uglify',
        'cssmin',
        'copy:assets',
        'copy:js',
        'copy:docs',
        'template:test',
        'nggettext_compile',
        'ngtemplates',
        'filerev',
        'usemin'
    ]);

    grunt.registerTask('package', ['ci', 'build']);
    grunt.registerTask('default', ['server']);
};
