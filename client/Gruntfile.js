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
        bowerDir: 'bower',
        poDir: 'po',
        livereloadPort: 35729,
        ngtemplates: {
            app: {
                cwd: "app",
                src: "scripts/**/*.html",
                dest: "app/scripts/templates.js",
                options: {
                    htmlmin: {
                        collapseWhitespace: true,
                        collapseBooleanAttributes: true
                    },
                    bootstrap:  function(module, script) {
                        return '\
                        define(["angular"], function (angular) {\
                            "use strict";\
                            var templates = angular.module("templates", []);\
                            templates.run(function($templateCache) {\
                              ' + script + '\
                            });\
                            return templates;\
                        });';
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
    grunt.registerTask('hint', ['jshint', 'jscs']);
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
        'watch'
    ]);

    grunt.registerTask('server', ['clean', 'style', 'template:test', 'connect:test', 'open:test', 'watch']);
    grunt.registerTask('server:e2e', ['clean', 'style', 'template:mock', 'connect:mock', 'watch']);
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
        'filerev',
        'usemin'
    ]);

    grunt.registerTask('package', ['ci', 'build']);
    grunt.registerTask('default', ['server']);
};
