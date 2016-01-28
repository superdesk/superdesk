'use strict';

module.exports = {
    app: {
        cwd: '<%= coreDir %>',
        src: [
            'scripts/**/*.html',
            'scripts/**/*.svg'
        ],
        dest: '<%= distDir %>/templates-cache.js',
        options: {
            htmlmin: {
                collapseWhitespace: true,
                collapseBooleanAttributes: true
            },
            bootstrap: function(module, script) {
                return '"use strict";' +
                    'angular.module("superdesk.templates-cache", [])' +
                    '.run([\'$templateCache\', function($templateCache) {' +
                    script + ' }]);';
            }
        }
    }
};
